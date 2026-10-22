"""Your session of the app: its cookies from your own Chrome, saved on this machine.

`<cli> connect` reads them from Chrome over the Chrome DevTools Protocol, in one of two ways:

- Chrome 144+ with remote debugging switched on at chrome://inspect/#remote-debugging. Chrome writes
  the port to `DevToolsActivePort` in its profile folder and asks you to allow each connection.
- Any Chrome started with `--remote-debugging-port=9222 --user-data-dir=<folder>`: pass `--cdp http://127.0.0.1:9222`.

The session file holds cookies, the app's session keys from localStorage and your time zone, never your password,
and is readable by your user alone (0600). Names, domains and the session cookie come from `app.py`.
"""

from __future__ import annotations

import json
import os
import platform
import re
import stat
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from bookingkoala_api_mcp import app
from bookingkoala_api_mcp.core.errors import ErrorCode, ToolError

SESSION_COOKIE = app.SESSION_COOKIES[0]


def home() -> Path:
    """Where the session is kept: $<ENV>_MCP_HOME, or ~/.config/<slug>-api-mcp."""
    return Path(os.environ.get(f"{app.ENV}_MCP_HOME") or Path.home() / ".config" / f"{app.SLUG}-api-mcp")


def session_path() -> Path:
    return home() / "session.json"


@dataclass
class Session:
    cookies: list[dict[str, Any]] = field(default_factory=list)
    user_agent: str | None = None
    chrome_major: int | None = None
    locale: str | None = None
    # Where the cookies came from, so a signed-out session can be read again: "auto", a CDP URL, or "token".
    source: str | None = None
    proxy: str | None = None
    # Origin -> {key: value} for app.LOCAL_STORAGE_KEYS, read from the app's open tabs.
    local_storage: dict[str, dict[str, str]] = field(default_factory=dict)
    # IANA zone of the browser, e.g. "America/New_York". Tools that say "today" use it.
    timezone: str | None = None

    @property
    def signed_in(self) -> bool:
        if all(any(c["name"] == name and c.get("value") for c in self.cookies) for name in app.SESSION_COOKIES):
            return True
        return any(values.get(key) for values in self.local_storage.values() for key in app.LOCAL_STORAGE_KEYS)


def cookie_domain(store: str | None = None) -> str:
    """The host of a pasted token's cookie: app.COOKIE_DOMAIN with the store name filled in."""
    if "{store}" not in app.COOKIE_DOMAIN:
        return app.COOKIE_DOMAIN
    store = (store or "").strip().lower().removeprefix("https://").split("/")[0]
    store = store.removesuffix(app.COOKIE_DOMAIN.replace("{store}", ""))
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", store):
        raise ToolError(
            f"Give your store name, e.g. yourstore for {app.COOKIE_DOMAIN.replace('{store}', 'yourstore')}.",
            ErrorCode.INVALID_INPUT,
        )
    return app.COOKIE_DOMAIN.replace("{store}", store)


def system_timezone() -> str:
    """This computer's IANA zone: $TZ, the /etc/localtime link, else UTC."""
    if (tz := os.environ.get("TZ", "").strip()) and "/" in tz:
        return tz.lstrip(":")
    try:
        target = os.path.realpath("/etc/localtime")
    except OSError:
        target = ""
    if "zoneinfo/" in target:
        return target.split("zoneinfo/", 1)[1]
    return "UTC"


def load() -> Session:
    """The saved session, with <ENV>_AUTH_TOKEN and <ENV>_PROXY from the environment on top."""
    session = Session()
    path = session_path()
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        session = Session(**{k: v for k, v in data.items() if k in Session.__dataclass_fields__})
    if token := os.environ.get(f"{app.ENV}_AUTH_TOKEN", "").strip():
        domain = cookie_domain(os.environ.get(f"{app.ENV}_STORE"))
        session.cookies = [c for c in session.cookies if c["name"] != SESSION_COOKIE]
        session.cookies.append({"name": SESSION_COOKIE, "value": token, "domain": domain, "path": "/"})
        session.source = session.source or "token"
        session.timezone = session.timezone or system_timezone()
    if proxy := os.environ.get(f"{app.ENV}_PROXY", "").strip():
        session.proxy = proxy
    return session


def save(session: Session) -> Path:
    path = session_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IRUSR | stat.S_IWUSR)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(asdict(session), fh, indent=2)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    return path


def from_token(token: str, store: str | None = None) -> Session:
    """A session from the session cookie's value copied by hand (Chrome DevTools > Application > Cookies)."""
    token = token.strip()
    if not token:
        raise ToolError("The token is empty.", ErrorCode.INVALID_INPUT)
    cookie = {"name": SESSION_COOKIE, "value": token, "domain": cookie_domain(store), "path": "/"}
    return Session(cookies=[cookie], source="token", timezone=system_timezone())


def chrome_profile_dirs() -> list[Path]:
    """Default Chrome profile folders of this OS, stable channel first."""
    system = platform.system()
    if system == "Darwin":
        base = Path.home() / "Library" / "Application Support" / "Google"
        return [base / "Chrome", base / "Chrome Beta", base / "Chrome Canary"]
    if system == "Windows":
        base = Path(os.environ.get("LOCALAPPDATA", "")) / "Google"
        return [base / "Chrome" / "User Data", base / "Chrome Beta" / "User Data", base / "Chrome SxS" / "User Data"]
    base = Path.home() / ".config"
    return [base / "google-chrome", base / "google-chrome-beta", base / "chromium"]


def auto_endpoint(profile_dir: str | None = None) -> str:
    """The browser WebSocket URL from DevToolsActivePort, written while remote debugging is on."""
    dirs = [Path(profile_dir).expanduser()] if profile_dir else chrome_profile_dirs()
    for folder in dirs:
        port_file = folder / "DevToolsActivePort"
        if port_file.exists():
            lines = port_file.read_text(encoding="utf-8").split()
            if len(lines) >= 2 and lines[0].isdigit():
                return f"ws://127.0.0.1:{lines[0]}{lines[1]}"
    raise ToolError(
        "Chrome remote debugging is off. Open chrome://inspect/#remote-debugging in Chrome, switch it on, "
        "and run this again. Or start Chrome with --remote-debugging-port=9222 and pass --cdp http://127.0.0.1:9222.",
        ErrorCode.AUTH_REQUIRED,
    )


def _endpoint(cdp: str) -> str:
    """A ws:// URL as given, or the browser WebSocket URL behind an http:// DevTools address."""
    if cdp.startswith(("ws://", "wss://")):
        return cdp
    with urllib.request.urlopen(cdp.rstrip("/") + "/json/version", timeout=10) as resp:
        return json.loads(resp.read())["webSocketDebuggerUrl"]


class _Cdp:
    """A tiny synchronous CDP client: one WebSocket to the browser target."""

    def __init__(self, url: str) -> None:
        from websockets.sync.client import connect

        # Chrome shows "Allow remote debugging?" for this connection; give the user time to click it.
        self._ws = connect(url, open_timeout=60, max_size=64 * 1024 * 1024)
        self._id = 0

    def send(self, method: str, params: dict[str, Any] | None = None, session_id: str | None = None) -> dict[str, Any]:
        self._id += 1
        message: dict[str, Any] = {"id": self._id, "method": method, "params": params or {}}
        if session_id:
            message["sessionId"] = session_id
        self._ws.send(json.dumps(message))
        while True:
            message = json.loads(self._ws.recv(timeout=60))
            if message.get("id") != self._id:
                continue
            if "error" in message:
                raise ToolError(f"Chrome refused {method}: {message['error'].get('message')}", ErrorCode.INTERNAL_ERROR)
            return message.get("result") or {}

    def evaluate(self, target_id: str, expression: str) -> Any:
        """The value of a JavaScript expression in one tab. Nothing in the tab changes."""
        attached = self.send("Target.attachToTarget", {"targetId": target_id, "flatten": True})
        session_id = attached["sessionId"]
        try:
            result = self.send("Runtime.evaluate", {"expression": expression, "returnByValue": True}, session_id)
            return (result.get("result") or {}).get("value")
        finally:
            self.send("Target.detachFromTarget", {"sessionId": session_id})

    def close(self) -> None:
        self._ws.close()


def _in_domains(host: str) -> bool:
    host = host.lstrip(".").lower()
    return any(host == domain or host.endswith(f".{domain}") for domain in app.DOMAINS)


def _read_tabs(client: _Cdp) -> tuple[str | None, dict[str, dict[str, str]]]:
    """The browser's time zone and the app's session keys in localStorage, from its open tabs."""
    timezone: str | None = None
    storage: dict[str, dict[str, str]] = {}
    keys = json.dumps(list(app.LOCAL_STORAGE_KEYS))
    read_keys = (
        f"JSON.stringify(Object.fromEntries({keys}.map(k => [k, localStorage.getItem(k)]).filter(e => e[1] !== null)))"
    )
    try:
        targets = client.send("Target.getTargets").get("targetInfos") or []
    except ToolError:
        return None, {}
    for target in targets:
        if target.get("type") != "page":
            continue
        url = target.get("url") or ""
        parts = urlsplit(url)
        try:
            if timezone is None and parts.scheme in ("http", "https"):
                zone = client.evaluate(target["targetId"], "Intl.DateTimeFormat().resolvedOptions().timeZone")
                timezone = zone if isinstance(zone, str) and zone else None
            origin = f"{parts.scheme}://{parts.netloc}"
            app_tab = parts.scheme == "https" and _in_domains(parts.hostname or "") and origin not in storage
            if app.LOCAL_STORAGE_KEYS and app_tab:
                values = json.loads(client.evaluate(target["targetId"], read_keys) or "{}")
                if isinstance(values, dict) and values:
                    storage[origin] = {str(k): str(v) for k, v in values.items()}
        except (ToolError, KeyError, ValueError):
            continue
    return timezone, storage


def from_chrome(cdp: str | None = None, profile_dir: str | None = None) -> Session:
    """Read the app's cookies of a running Chrome. Nothing is changed in the browser."""
    url = _endpoint(cdp) if cdp else auto_endpoint(profile_dir)
    try:
        client = _Cdp(url)
    except Exception as exc:
        raise ToolError(
            f"Could not connect to Chrome at {urlsplit(url).netloc} ({type(exc).__name__}). "
            "Is Chrome open, and did you click Allow in its remote debugging prompt?",
            ErrorCode.AUTH_REQUIRED,
        ) from exc
    try:
        version = client.send("Browser.getVersion")
        cookies = client.send("Storage.getCookies").get("cookies") or []
        timezone, storage = _read_tabs(client)
    finally:
        client.close()
    mine = [
        {"name": c["name"], "value": c["value"], "domain": c["domain"], "path": c.get("path") or "/"}
        for c in cookies
        if _in_domains(c.get("domain", ""))
    ]
    user_agent = version.get("userAgent")
    match = re.search(r"Chrome/(\d+)", user_agent or "") or re.search(r"/(\d+)\.", version.get("product", ""))
    session = Session(
        cookies=mine,
        user_agent=user_agent,
        chrome_major=int(match.group(1)) if match else None,
        source=cdp or "auto",
        local_storage=storage,
        timezone=timezone or system_timezone(),
    )
    if not session.signed_in:
        raise ToolError(
            f"This Chrome is not signed in to {app.NAME}. Sign in at {app.LOGIN_URL}, then run this again.",
            ErrorCode.AUTH_REQUIRED,
        )
    return session


def refresh(session: Session) -> Session | None:
    """Read the cookies again from where they came from; None when the source is a hand-copied token."""
    if not session.source or session.source == "token":
        return None
    fresh = from_chrome(None if session.source == "auto" else session.source)
    fresh.proxy = session.proxy
    save(fresh)
    return fresh
