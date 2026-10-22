"""List charges: the Charges page (`POST /api/v6/charged-bookings`, POST only: a GET answers "Session Expired").

The answer is the bookings search shape (`bookings`, `users_info`, `addresses`) where each booking carries its
`payment_logs`; logs re-authorized later come in `reauthorized_payment_logs[<booking id>]` (admin bundle 227).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bookingkoala_api_mcp.bookingkoala.client import api
from bookingkoala_api_mcp.bookingkoala.tools._bookings import booking_row, money, parse_day, text
from bookingkoala_api_mcp.bookingkoala.tools._people import iso
from bookingkoala_api_mcp.core.helpers import limit, page_cursor
from bookingkoala_api_mcp.core.tools import tool

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "search": {"type": "string", "description": "Customer name, email or phone, or a booking id."},
        "start_date": {"type": "string", "description": "First booking day, YYYY-MM-DD. Default: no lower bound."},
        "end_date": {"type": "string", "description": "Last booking day, YYYY-MM-DD. Default: no upper bound."},
        "limit": {"type": "integer", "description": "1 to 100. Default: 20."},
        "cursor": {"type": "string", "description": "next_cursor from the previous call."},
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_PAYMENT: dict[str, Any] = {
    "payment_log_id": 41,
    "type": "booking",
    "status": "paid",
    "amount": 216.5,
    "tax": 16.5,
    "refunded_amount": 0.0,
    "refunded": False,
    "method": "new_credit_card",
    "card_last4": "4242",
    "charged_at": "2026-11-16T15:02:11Z",
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "charges": [
        {
            "booking_id": 3,
            "status": "completed",
            "date": "2026-11-16",
            "arrival_time": "11:00",
            "length_minutes": 160,
            "occurrence": "recurring",
            "recurring_id": 1,
            "frequency": "every_4_weeks",
            "customer": {"customer_id": 2, "name": "Dana Whitfield", "email": "dana.whitfield@example.com"},
            "address": "540 W 28th Street, New York, NY 10022",
            "provider_ids": [3],
            "providers": [{"provider_id": 3, "name": "Marcus Lee"}],
            "payment_method": "new_credit_card",
            "total": 216.5,
            "charged": True,
            "payments": [EXAMPLE_PAYMENT],
        }
    ],
    "next_cursor": None,
}


def payment_row(log: dict[str, Any]) -> dict[str, Any]:
    refunded = money(log.get("refunded_amount")) or 0.0
    return {
        "payment_log_id": log.get("id") or log.get("_id"),
        "type": text(log.get("payment_type")),
        "status": text(log.get("status")),
        "amount": money(log.get("charged_amount") if log.get("charged_amount") is not None else log.get("amount")),
        "tax": money(log.get("tax_amount")),
        "refunded_amount": refunded,
        "refunded": bool(log.get("is_refunded")) or refunded > 0,
        "method": text(log.get("payment_method")),
        "card_last4": text(log.get("card_last4_digits")),
        "charged_at": iso(log.get("charged_on")),
    }


@tool(
    name="list_charges",
    title="List charges",
    access="read",
    confirm=False,
    description="Charged bookings with their payments and refunds, as the Charges page lists them.",
    details=(
        "Returns bookings that were charged, newest first, each with its payments: the booking charge, extras, "
        "tips, fees and refunds, with amount, tax, refunded amount and card. Filter by booking day and search by "
        "customer. BookingKoala gives no total: next_cursor is set while a full page comes back. booking_id and "
        "payment_log_id go to refund_charge. Empty until the store charges through a connected payment processor "
        "or marks bookings paid in cash."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /charges",
    example_response=EXAMPLE_RESPONSE,
)
async def list_charges(ctx: ToolContext, args: dict[str, Any]) -> Any:
    page, size = page_cursor(args.get("cursor")), limit(args, 20, 100)
    body = {
        "limit": size,
        "page": page,
        "location_id": 0,
        "industry_id": 0,
        "frequency_id": 0,
        "start_date": parse_day(args["start_date"], "start_date") if args.get("start_date") else "",
        "end_date": parse_day(args["end_date"], "end_date") if args.get("end_date") else "",
        "search": args.get("search") or "",
    }
    data = await api(ctx, "POST", "/api/v6/charged-bookings", params={"user_type": "admin", "status": ""}, json=body)
    data = data if isinstance(data, dict) else {}
    bookings = data.get("bookings") or []
    reauthorized = data.get("reauthorized_payment_logs") or {}
    users, addresses = data.get("users_info") or {}, data.get("addresses") or {}
    charges = []
    for booking in bookings:
        logs = [*(booking.get("payment_logs") or []), *(reauthorized.get(str(booking.get("_id"))) or [])]
        charges.append({**booking_row(booking, users, addresses), "payments": [payment_row(log) for log in logs]})
    return {"charges": charges, "next_cursor": str(page + 1) if len(bookings) >= size else None}
