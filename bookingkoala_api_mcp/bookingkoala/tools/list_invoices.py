"""List invoices: `POST /bkinvoice/v1/invoices`, or `/customer/invoices` with `uid` for one customer.

The list wants `limit` and `page` as strings and both dates set (empty ones answer "#25137"). Fields read from
the Invoices page of admin bundle 227. Invoice ids are 24-hex strings.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

from bookingkoala_api_mcp.bookingkoala.client import api
from bookingkoala_api_mcp.bookingkoala.tools._bookings import money, parse_day, text
from bookingkoala_api_mcp.bookingkoala.tools._people import iso
from bookingkoala_api_mcp.core.errors import ErrorCode, ToolError
from bookingkoala_api_mcp.core.helpers import limit, page_cursor
from bookingkoala_api_mcp.core.tools import tool

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext


def _obj(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _today() -> date:
    """Today in the US (the stores' market), so a day is not cut short in Europe."""
    return datetime.now(ZoneInfo("America/New_York")).date()


PAY_STATUSES = ["paid", "unpaid", "partially_paid", "void", "uncollectible"]
# Without dates the panel shows the current year; this goes two years back and one ahead.
_BACK_DAYS, _AHEAD_DAYS = 730, 365

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "search": {"type": "string", "description": "Invoice number, customer email, name or phone."},
        "customer_id": {"type": "integer", "minimum": 1, "description": "Only this customer's invoices."},
        "pay_status": {"type": "string", "enum": PAY_STATUSES, "description": "Payment status filter."},
        "start_date": {"type": "string", "description": "From this issue day, YYYY-MM-DD. Default: 2 years ago."},
        "end_date": {"type": "string", "description": "To this issue day, YYYY-MM-DD. Default: a year ahead."},
        "limit": {"type": "integer", "description": "1 to 100. Default: 20."},
        "cursor": {"type": "string", "description": "next_cursor from the previous call."},
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "invoices": [
        {
            "invoice_id": "6716a3f2c1e8b94d2a7f0c15",
            "number": "INV-1004",
            "customer": {"customer_id": 2, "name": "Dana Whitfield", "email": "dana.whitfield@example.com"},
            "type": "booking",
            "pay_status": "unpaid",
            "total": 216.5,
            "paid": 0.0,
            "amount_due": 216.5,
            "issued_at": "2026-11-16T15:02:11Z",
            "due_at": "2026-11-30T05:00:00Z",
            "recurring": False,
            "card_on_file": True,
            "booking_ids": [3],
        }
    ],
    "next_cursor": None,
}


def _customer(raw: dict[str, Any]) -> dict[str, Any]:
    customer = _obj(raw.get("customer"))
    name = " ".join(p for p in (customer.get("first_name"), customer.get("last_name")) if p) or raw.get("customer_name")
    return {
        "customer_id": raw.get("uid") or customer.get("id") or customer.get("_id"),
        "name": text(name),
        "email": text(customer.get("email_id") or raw.get("customer_email")),
    }


def invoice_row(raw: dict[str, Any]) -> dict[str, Any]:
    total = money(raw.get("total_amount"))
    paid = money(raw.get("paid_amount")) or 0.0
    due = money(raw.get("amount_due"))
    return {
        "invoice_id": raw.get("_id"),
        "number": text(raw.get("inv_num") or raw.get("number")),
        "customer": _customer(raw),
        "type": text(raw.get("inv_type")),
        "pay_status": text(raw.get("pay_status")),
        "total": total,
        "paid": paid,
        "amount_due": due if due is not None else (round(total - paid, 2) if total is not None else None),
        "issued_at": iso(raw.get("issue_date") or raw.get("created_on")),
        "due_at": iso(raw.get("due_date")),
        "recurring": bool(raw.get("rec_id")),
        "card_on_file": bool(raw.get("card_on_file")) and raw.get("card_on_file") != "no",
        "booking_ids": [int(b) for b in raw.get("booking_ids") or [] if str(b).isdigit()],
    }


@tool(
    name="list_invoices",
    title="List invoices",
    access="read",
    confirm=False,
    description="Invoices of the store or of one customer, with payment status, total and amount due.",
    details=(
        "Returns invoices as the Invoices page lists them, newest first: number, customer, booking or custom "
        "type, payment status (paid, unpaid, partially_paid, void, uncollectible), total, paid, amount due, "
        "issue and due dates. Filter by customer, payment status and issue dates (default: two years back to a "
        "year ahead), or search by number, email, name or phone. BookingKoala gives no "
        "total: next_cursor is set while a full page comes back. invoice_id goes to resend_invoice."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /invoices",
    example_response=EXAMPLE_RESPONSE,
)
async def list_invoices(ctx: ToolContext, args: dict[str, Any]) -> Any:
    page, size = page_cursor(args.get("cursor")), limit(args, 20, 100)
    today = _today()
    start = parse_day(args["start_date"], "start_date") if args.get("start_date") else None
    end = parse_day(args["end_date"], "end_date") if args.get("end_date") else None
    start = start or (today - timedelta(days=_BACK_DAYS)).isoformat()
    end = end or (today + timedelta(days=_AHEAD_DAYS)).isoformat()
    if start > end:
        raise ToolError("start_date is after end_date.", ErrorCode.INVALID_INPUT)
    body: dict[str, Any] = {
        "s": args.get("search") or "",
        "start_date": start,
        "end_date": end,
        "limit": str(size),
        "page": str(page),
        "sort_by": "",
        "sort_type": "",
        "status": "1",
        "pay_status": args.get("pay_status") or "",
        "card_on_file": "",
        "type": "",
        "rec_id": "",
    }
    path = "/bkinvoice/v1/invoices"
    if args.get("customer_id"):
        body["uid"] = int(args["customer_id"])
        path = "/bkinvoice/v1/customer/invoices"
    rows = await api(ctx, "POST", path, json=body) or []
    rows = [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []
    return {
        "invoices": [invoice_row(row) for row in rows],
        "next_cursor": str(page + 1) if len(rows) >= size else None,
    }
