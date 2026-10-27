"""BookingKoala's admin API, recorded on the dev account (21.10.2026).

Each business is its own host, `<store>.bookingkoala.com`, and the admin app (Angular, `cdn.bookingkoala.com/
admin-build`) calls `/api/v3`, `/api/v6` and the other `/<service>/v<n>/` paths on that host. A call needs three
things, else the app answers HTTP 200 with `api_status` 0 and "Unauthorized request":

- `authorization: Bearer <token>`: the token from sign-in. The app keeps it in `localStorage.currentUser` and in
  the cookie `IRON_GATEWAY_CTX` (URL-encoded JSON `{Ip, token, id, role}`, 30 days, set by the app's JS at
  sign-in, deleted at sign-out). The other cookies do not authenticate.
- `auth-session-v2`: base64 of `<csrf>__<store>__<nonce>`, where `<csrf>` is the `data` of
  `GET /bkutility/v1/preload` (no auth; it also sets the httpOnly `iron_csrf_token` cookie the csrf is checked
  against) and `<nonce>` is base64 of 32 random bytes, new for every request (a repeated one answers
  "Request expired"). The app refreshes the csrf every 25 minutes.
- the `iron_csrf_token` cookie from that preload.

The `ip` header the app sends (the browser's address from `/getip/`) is not checked: any value passes, and the
session is not bound to the exit IP. A bad or expired token answers `api_status` 10, "Session Expired", which is
the only signed-out answer: the core cannot see it (HTTP 200), so `api` turns it into `auth_expired`.
"""

from __future__ import annotations

import base64
import json
import secrets
import time
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from urllib.parse import unquote, urlsplit

from bookingkoala_api_mcp.core.errors import AuthExpiredError, ErrorCode, ToolError

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext
    from bookingkoala_api_mcp.core.profile import Cookie

WWW = "https://www.bookingkoala.com"
SESSION_COOKIE = "IRON_GATEWAY_CTX"
CSRF_COOKIE = "iron_csrf_token"
_SUFFIX = ".bookingkoala.com"
# BookingKoala's own hosts, never a store.
_NOT_STORES = {"www", "cdn", "help", "files", "api"}
# api_status in the answer: 1 done, 10 signed out; 99 csrf refused (the app fetches a new one).
_OK, _SIGNED_OUT, _CSRF_REFUSED = 1, 10, 99
# "#101-13" (csrf cookie does not match) and "#101-16" (request expired) also mean a stale csrf.
_STALE_CSRF = ("#101-13", "#101-16")
# The app renews its csrf every 25 minutes; this one is renewed a little sooner.
_CSRF_TTL_S = 20 * 60
# (browser_id, origin) -> (csrf, fetched at epoch seconds). In this process's memory only, never in Redis.
_csrf: dict[tuple[str, str], tuple[str, float]] = {}


@dataclass(frozen=True)
class Session:
    origin: str
    store: str
    token: str
    user_id: int
    role: str
    ip: str


def store_of(host: str) -> str | None:
    """`yourstore` for `yourstore.bookingkoala.com`; None for BookingKoala's own hosts."""
    host = host.lstrip(".").lower()
    if not host.endswith(_SUFFIX):
        return None
    store = host.removesuffix(_SUFFIX)
    return store if store and "." not in store and store not in _NOT_STORES else None


def _parse(raw: str | None) -> dict[str, Any] | None:
    if not raw:
        return None
    try:
        value = json.loads(raw)
    except ValueError:
        return None
    return value if isinstance(value, dict) and value.get("token") and value.get("id") else None


def session_from(cookies: Iterable[Cookie], local_storage: dict[str, dict[str, str]]) -> Session | None:
    """The store and token in these cookies or this localStorage; None when they hold none."""
    found: tuple[str, dict[str, Any]] | None = None
    for cookie in cookies:
        if cookie.name != SESSION_COOKIE or not (store := store_of(cookie.domain)):
            continue
        if user := _parse(unquote(cookie.value)):
            found = (store, user)
            break
    if found is None:
        for origin, values in local_storage.items():
            if (store := store_of(urlsplit(origin).hostname or "")) and (user := _parse(values.get("currentUser"))):
                found = (store, user)
                break
    if found is None:
        return None
    store, user = found
    return Session(
        origin=f"https://{store}{_SUFFIX}",
        store=store,
        token=str(user["token"]),
        user_id=int(user["id"]),
        role=str(user.get("role") or ""),
        ip=str(user.get("Ip") or ""),
    )


def session(ctx: ToolContext) -> Session | None:
    """The store and token the browser is signed in with; None when it holds none.

    The session is in the cookie, in localStorage, or in both, so both are read.
    """
    return session_from(ctx.profile.cookies, ctx.profile.local_storage)


def require_session(ctx: ToolContext) -> Session:
    s = session(ctx)
    if s is None:
        raise AuthExpiredError("The app signed this account out. Sign in again in Chrome, then run connect.")
    return s


async def _csrf_token(ctx: ToolContext, s: Session, *, fresh: bool = False) -> str:
    key = (ctx.profile.browser_id, s.origin)
    cached = _csrf.get(key)
    if cached and not fresh and time.time() - cached[1] < _CSRF_TTL_S:
        return cached[0]
    response = await ctx.call("GET", f"{s.origin}/bkutility/v1/preload", headers=_headers(s, None))
    data = (response.json().get("response") or {}).get("data")
    if not isinstance(data, str) or not data:
        raise ToolError("BookingKoala did not answer its preload.", ErrorCode.TARGET_ERROR)
    _csrf[key] = (data, time.time())
    return data


def auth_headers(s: Session, csrf: str) -> dict[str, str]:
    """What an admin call adds to the page's own headers; a new nonce each time. login.py sends them from the tab."""
    nonce = base64.b64encode(secrets.token_bytes(32)).decode()
    signed = base64.b64encode(f"{csrf}__{s.store}__{nonce}".encode()).decode()
    return {"authorization": f"Bearer {s.token}", "ip": s.ip, "auth-session-v2": signed}


async def request_headers(ctx: ToolContext) -> dict[str, str]:
    """Bearer, `ip` and a fresh `auth-session-v2` for one admin call."""
    s = require_session(ctx)
    return auth_headers(s, await _csrf_token(ctx, s))


def _headers(s: Session, csrf: str | None) -> dict[str, str]:
    headers = {
        "accept": "application/json, text/plain, */*",
        "origin": s.origin,
        "referer": f"{s.origin}/admin/dashboard",
    }
    return headers if csrf is None else {**headers, **auth_headers(s, csrf)}


async def api(ctx: ToolContext, method: str, path: str, *, s: Session | None = None, **kwargs: Any) -> Any:
    """One admin API call (`path` from the host root, e.g. `/api/v6/users/1`); returns `response.data`.

    `AuthExpiredError` when the app says signed out, `ToolError` on any other refusal. A stale csrf gets one
    new preload and one retry.
    """
    s = s or require_session(ctx)
    extra = kwargs.pop("headers", None) or {}
    answer: dict[str, Any] = {}
    for attempt in range(2):
        csrf = await _csrf_token(ctx, s, fresh=attempt > 0)
        response = await ctx.call(method, f"{s.origin}{path}", headers={**_headers(s, csrf), **extra}, **kwargs)
        body = response.json()
        answer = (body.get("response") if isinstance(body, dict) else None) or {}
        status, message = answer.get("api_status"), str(answer.get("message") or "")
        if status == _SIGNED_OUT:
            raise AuthExpiredError("The app signed this account out. Sign in again in Chrome, then run connect.")
        if status == _OK:
            return answer.get("data")
        if status != _CSRF_REFUSED and not message.startswith(_STALE_CSRF):
            break
    raise ToolError(
        f"BookingKoala refused {method} {path}: {answer.get('message') or 'no answer'}.", ErrorCode.TARGET_ERROR
    )
