"""Create booking from an existing one: GET `/api/v6/bookings/{id}/duplicate`.

The copy is a draft with the source's customer, service, frequency and the app's own price sheet; its date
is set and it is booked in the booking form (`/admin/booking/draft/<industry>/<form>/<id>`). Never a
rebuilt price sheet.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bookingkoala_api_mcp.bookingkoala.client import api, require_session
from bookingkoala_api_mcp.bookingkoala.tools._bookings import BOOKING_ID
from bookingkoala_api_mcp.core.errors import ErrorCode, ToolError
from bookingkoala_api_mcp.core.tools import tool

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "from_booking_id": {**BOOKING_ID, "description": "Booking to copy, from list_bookings."},
    },
    "required": ["from_booking_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "draft_id": 1,
    "from_booking_id": 3,
    "form_url": "https://yourstore.bookingkoala.com/admin/booking/draft/1/1/1",
}


@tool(
    name="create_booking",
    title="Create booking",
    access="write",
    description="Start a new booking as a copy of an existing one: same customer, service and price.",
    details=(
        "Copies the booking as Duplicate in its sidebar does. The copy is saved as a draft (list_drafts) "
        "with the same customer, address, service, extras and price; open form_url to pick the date and "
        "book it. Nobody is told until it is booked."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /bookings",
    example_response=EXAMPLE_RESPONSE,
)
async def create_booking(ctx: ToolContext, args: dict[str, Any]) -> Any:
    s = require_session(ctx)
    source = int(args["from_booking_id"])
    data = await api(ctx, "GET", f"/api/v6/bookings/{source}/duplicate", s=s)
    if not isinstance(data, dict) or not data.get("_id"):
        raise ToolError("BookingKoala did not return the copy.", ErrorCode.TARGET_ERROR)
    draft = data["_id"]
    return {
        "draft_id": draft,
        "from_booking_id": source,
        "form_url": f"{s.origin}/admin/booking/draft/{data.get('industry_id')}/{data.get('form_id')}/{draft}",
    }
