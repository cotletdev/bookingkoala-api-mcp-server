"""Reschedule booking: POST `/api/v6/bookings/{id}/postpone`.

Body from the panel's `bk-postpone-popup` (admin-build 227, `submitPostpone`): the new date is one of the later
visits of the same schedule, listed by `postponement-preview?booking_date=`, sent with that visit's `_id`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bookingkoala_api_mcp.bookingkoala.client import api
from bookingkoala_api_mcp.bookingkoala.tools._bookings import BOOKING_ID, parse_day
from bookingkoala_api_mcp.bookingkoala.tools.get_booking import EXAMPLE_RESPONSE, read_booking
from bookingkoala_api_mcp.core.errors import ErrorCode, ToolError
from bookingkoala_api_mcp.core.tools import tool

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "booking_id": BOOKING_ID,
        "date": {
            "type": "string",
            "format": "date",
            "description": "New date: one of the later visit dates of the booking's recurring schedule.",
        },
        "notify": {
            "type": "boolean",
            "description": "Email the customer and providers about the change. Default: false.",
        },
    },
    "required": ["booking_id", "date"],
    "additionalProperties": False,
}


@tool(
    name="reschedule_booking",
    title="Reschedule booking",
    access="write",
    confirm=True,
    description="Postpone a visit of a recurring booking to the date of a later visit in its schedule.",
    details=(
        "Works like Postpone in the booking's sidebar: the visit moves to one of the schedule's later visit "
        "dates, keeping its arrival time and price, and the booking comes back as get_booking shows it. A date "
        "outside the schedule fails with the list of allowed dates. One-time bookings cannot be postponed. "
        "Nobody is told unless notify is true. A store that charges a reschedule fee refuses the move here: "
        "charge it in the panel."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /bookings/{booking_id}/reschedule",
    example_response=EXAMPLE_RESPONSE,
)
async def reschedule_booking(ctx: ToolContext, args: dict[str, Any]) -> Any:
    booking_id = int(args["booking_id"])
    new_date = parse_day(args["date"], "date")
    booking = await api(ctx, "GET", f"/api/v6/bookings/{booking_id}?limited_data=true")
    if not isinstance(booking, dict) or not booking.get("_id"):
        raise ToolError(f"No booking {booking_id} in this store. Use list_bookings.", ErrorCode.TARGET_ERROR)
    recurring_id, booking_date = booking.get("recurring_id"), booking.get("booking_date")
    if not recurring_id:
        raise ToolError("Only a visit of a recurring booking can be postponed.", ErrorCode.TARGET_ERROR)
    preview = await api(
        ctx,
        "GET",
        f"/api/v6/recurring-bookings/{recurring_id}/postponement-preview",
        params={"booking_date": booking_date},
    )
    visits = (preview.get("bookings") or []) if isinstance(preview, dict) else []
    target = next((v for v in visits if v.get("booking_date") == new_date), None)
    if target is None:
        allowed = ", ".join(str(v.get("booking_date")) for v in visits) or "none"
        raise ToolError(f"date must be one of the schedule's later visits: {allowed}.", ErrorCode.INVALID_INPUT)
    fee = await api(ctx, "GET", f"/api/v6/bookings/{booking_id}/reschedule-fee")
    if isinstance(fee, dict) and (fee.get("amount") or fee.get("fee")):
        raise ToolError("This store charges a reschedule fee for this booking.", ErrorCode.TARGET_ERROR)
    body = {
        "recurring_id": recurring_id,
        "booking_date": booking_date,
        "postpone_date": new_date,
        "postpone_booking_id": target.get("_id"),
        "amount": 0,
        "exclude_notifications": not args.get("notify"),
    }
    await api(ctx, "POST", f"/api/v6/bookings/{booking_id}/postpone", json=body)
    return await read_booking(ctx, booking_id)
