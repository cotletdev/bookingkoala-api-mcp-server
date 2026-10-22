"""Send a quote: the Send quote popup of the Drafts page (admin bundle 227), three calls in the panel's order.

1. `PUT /api/v3/quote` saves recipient and expiry on the quote (`?save_log=yes` the first time it is sent);
2. `GET /api/v3/send-quote-email-data?slug=send_quote&draft_id=` gives the store's email subject and body;
3. `POST /api/v3/quote/send` `{id, email_id, subject, content, industry_id}` mails it.

A quote is a draft whose `quote` has a `status` (saved with "Save as quote" in the booking form,
`POST /api/v3/draft?quote=true`). Drafts come from `GET /api/v6/drafts`.
"""

from __future__ import annotations

import re
import time
from datetime import UTC, date, datetime, timedelta
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

from bookingkoala_api_mcp.bookingkoala.client import api
from bookingkoala_api_mcp.bookingkoala.tools._bookings import parse_day
from bookingkoala_api_mcp.core.errors import ErrorCode, ToolError
from bookingkoala_api_mcp.core.tools import tool

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext


def _obj(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _today() -> date:
    """Today in the US (the stores' market), so a day is not cut short in Europe."""
    return datetime.now(ZoneInfo("America/New_York")).date()


_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
# Drafts are found by paging the list; a store with more drafts than this is not searched further.
_PAGE, _PAGES = 100, 5
# The popup's default expiry: a month from today.
_DEFAULT_DAYS = 30
_ACTIVE, _EXPIRED = 1, 9

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "draft_id": {"type": "integer", "minimum": 1, "description": "Id of a quote from list_drafts."},
        "email": {"type": "string", "description": "Send to this address. Default: the quote's customer."},
        "expires_on": {
            "type": "string",
            "description": "Last day the customer can book it, YYYY-MM-DD. Default: as saved, else a month ahead.",
        },
        "subject": {"type": "string", "maxLength": 200, "description": "Email subject. Default: the store's."},
        "message": {
            "type": "string",
            "description": "Email body (HTML allowed). Default: the store's Send quote template.",
        },
    },
    "required": ["draft_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "draft_id": 14,
    "quote_id": 6,
    "email": "dana.whitfield@example.com",
    "subject": "Your quote from Sparkle Clean",
    "expires_on": "2026-12-16",
    "share_link": "q7Hk2mPz",
    "sent": True,
}


def _midnight(day: str) -> int:
    return int(datetime.combine(date.fromisoformat(day), datetime.min.time(), UTC).timestamp())


async def _quote(ctx: ToolContext, args: dict[str, Any]) -> dict[str, Any]:
    """The draft with its quote; refuses before approval a draft that is not a quote or has no address."""
    draft_id, draft = int(args["draft_id"]), None
    for page in range(1, _PAGES + 1):
        params = {"limit": _PAGE, "page": page, "location": "", "industry": "", "s": ""}
        rows = await api(ctx, "GET", "/api/v6/drafts", params=params) or []
        draft = next((row for row in rows if isinstance(row, dict) and row.get("_id") == draft_id), None)
        if draft is not None:
            break
        if len(rows) < _PAGE:
            raise ToolError("No draft with this draft_id in the store.", ErrorCode.INVALID_INPUT)
    if draft is None:
        raise ToolError("No draft with this draft_id among the store's newest drafts.", ErrorCode.INVALID_INPUT)
    quote = _obj(draft.get("quote"))
    if not quote.get("id") or not quote.get("status"):
        raise ToolError(
            "This draft is not a quote. Open it in the booking form and save it as a quote first.",
            ErrorCode.INVALID_INPUT,
        )
    customer = _obj(draft.get("customer"))
    email = str(args.get("email") or quote.get("email_id") or customer.get("email_id") or "").strip()
    if not _EMAIL.match(email):
        raise ToolError("The quote has no customer email; pass email.", ErrorCode.INVALID_INPUT)
    if args.get("expires_on"):
        expires = parse_day(args["expires_on"], "expires_on")
        if expires < _today().isoformat():
            raise ToolError("expires_on is in the past.", ErrorCode.INVALID_INPUT)
    elif quote.get("expires_on") and quote["expires_on"] > time.time():
        expires = datetime.fromtimestamp(quote["expires_on"], UTC).date().isoformat()
    else:
        expires = (_today() + timedelta(days=_DEFAULT_DAYS)).isoformat()
    return {"draft": draft, "quote": quote, "email": email, "expires": expires}


async def check_quote(ctx: ToolContext, args: dict[str, Any]) -> None:
    """Before approval: an unknown draft, a draft that is not a quote or no address fails now."""
    await _quote(ctx, args)


@tool(
    name="send_quote",
    title="Send a quote",
    access="write",
    confirm=True,
    description="Email a saved quote to the customer with a link to book it.",
    details=(
        "Sends a quote from list_drafts as the Send quote popup does: saves the recipient and expiry date on the "
        "quote, then emails the store's Send quote template (or your subject and message) with the quote's "
        "booking link. email defaults to the quote's customer; expires_on to the saved date, else a month "
        "ahead. Only drafts saved as quotes can be sent; a plain draft is refused before you confirm. The "
        "customer gets the email at once. By default you confirm each call; you can switch that off for this "
        "tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /quotes/{draft_id}/send",
    example_response=EXAMPLE_RESPONSE,
    check=check_quote,
)
async def send_quote(ctx: ToolContext, args: dict[str, Any]) -> Any:
    found = await _quote(ctx, args)
    draft, quote, email = found["draft"], found["quote"], found["email"]
    first_send = not quote.get("expires_on")
    saved = await api(
        ctx,
        "PUT",
        "/api/v3/quote",
        params={"save_log": "yes"} if first_send else None,
        json={
            "id": quote["id"],
            "status": _ACTIVE if found["expires"] >= _today().isoformat() else _EXPIRED,
            "draft_id": draft["_id"],
            "email_id": email,
            "expires_on": _midnight(found["expires"]),
            "send_reminder": bool(quote.get("send_reminder")),
            "send_reminder_after": int(quote.get("send_reminder_after") or 0),
            "send_reminder_on": quote.get("send_reminder_on"),
            "is_offer_applied": bool(quote.get("is_offer_applied")),
            "offer_value": float(quote.get("offer_value") or 0),
            "offer_value_type": quote.get("offer_value_type") or "percentage",
            "share_link": quote.get("share_link"),
            "created_on": int(quote.get("created_on") or time.time()),
        },
    )
    saved = saved if isinstance(saved, dict) else quote
    template = await api(
        ctx, "GET", "/api/v3/send-quote-email-data", params={"slug": "send_quote", "draft_id": draft["_id"]}
    )
    template = template if isinstance(template, dict) else {}
    subject = (args.get("subject") or template.get("subject") or "").strip()
    if not subject:
        raise ToolError("The store has no Send quote email template; pass subject and message.", ErrorCode.TARGET_ERROR)
    await api(
        ctx,
        "POST",
        "/api/v3/quote/send",
        json={
            "id": saved.get("id") or quote["id"],
            "email_id": email,
            "subject": subject,
            "content": args.get("message") or template.get("content") or "",
            "industry_id": draft.get("industry_id"),
        },
    )
    return {
        "draft_id": draft["_id"],
        "quote_id": saved.get("id") or quote["id"],
        "email": email,
        "subject": subject,
        "expires_on": found["expires"],
        "share_link": saved.get("share_link") or quote.get("share_link"),
        "sent": True,
    }
