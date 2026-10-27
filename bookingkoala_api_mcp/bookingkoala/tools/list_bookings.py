"""List bookings: POST `/api/v6/bookings/search?user_type=admin&status=<s>` (a read sent as POST)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bookingkoala_api_mcp.bookingkoala.client import api
from bookingkoala_api_mcp.bookingkoala.tools._bookings import EXAMPLE_BOOKING, booking_row, parse_day
from bookingkoala_api_mcp.core.errors import ErrorCode, ToolError
from bookingkoala_api_mcp.core.helpers import limit, page_cursor
from bookingkoala_api_mcp.core.tools import tool

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext

# `authorized` is refused by the app.
STATUS_FILTERS = ["all", "upcoming", "today", "unassigned", "completed", "pending", "declined", "paused"]

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": STATUS_FILTERS,
            "description": "Which bookings: upcoming (default), today, unassigned, completed, pending (charge "
            "pending), declined (charge declined), paused or all.",
        },
        "search": {"type": "string", "description": "Customer name, email or phone."},
        "start_date": {"type": "string", "format": "date", "description": "From this date."},
        "end_date": {"type": "string", "format": "date", "description": "Up to this date."},
        "customer_id": {"type": "integer", "minimum": 1, "description": "Only this customer's bookings."},
        "provider_id": {"type": "integer", "minimum": 1, "description": "Only this provider's bookings."},
        "limit": {"type": "integer", "minimum": 1, "maximum": 50, "description": "Page size. Default: 20."},
        "cursor": {"type": "string", "description": "next_cursor from the previous call."},
    },
    "additionalProperties": False,
}


@tool(
    name="list_bookings",
    title="List bookings",
    access="read",
    description="Bookings of the store: upcoming, unassigned, completed, charge pending or declined.",
    details=(
        "Lists bookings as the Bookings page shows them, newest schedule dates first within the filter, with "
        "the customer, address, assigned providers, total and whether it is charged. Filter by status, date "
        "range, a search on the customer, or one customer or provider. Cancelled bookings are not listed. "
        "Page with next_cursor."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /bookings",
    example_response={"bookings": [EXAMPLE_BOOKING], "next_cursor": None},
)
async def list_bookings(ctx: ToolContext, args: dict[str, Any]) -> Any:
    if args.get("customer_id") and args.get("provider_id"):
        raise ToolError("Give customer_id or provider_id, not both.", ErrorCode.INVALID_INPUT)
    status = args.get("status") or "upcoming"
    page, size = page_cursor(args.get("cursor")), limit(args, 20, 50)
    body: dict[str, Any] = {
        "limit": size,
        "page": page,
        "status": status,
        "search": (args.get("search") or "").strip(),
        "start_date": parse_day(args["start_date"], "start_date") if args.get("start_date") else "",
        "end_date": parse_day(args["end_date"], "end_date") if args.get("end_date") else "",
        "location_id": 0,
        "industry_id": 0,
        "frequency_id": 0,
    }
    if args.get("customer_id"):
        body.update(user_type="customer", uids=[args["customer_id"]])
    elif args.get("provider_id"):
        body.update(user_type="provider", uids=[args["provider_id"]])
    data = await api(ctx, "POST", f"/api/v6/bookings/search?user_type=admin&status={status}", json=body) or {}
    rows = data.get("bookings") or []
    users, addresses = data.get("users_info") or {}, data.get("addresses") or {}
    return {
        "bookings": [booking_row(row, users, addresses) for row in rows],
        # No total in the answer: a full page means there may be more (the panel's "Load more").
        "next_cursor": str(page + 1) if len(rows) >= size else None,
    }
