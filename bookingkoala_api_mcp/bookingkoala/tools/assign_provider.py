"""Assign provider: POST `/api/v6/providers/{provider_id}/assign-booking`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bookingkoala_api_mcp.bookingkoala.client import api
from bookingkoala_api_mcp.bookingkoala.tools._bookings import BOOKING_ID, PROVIDER_ID
from bookingkoala_api_mcp.bookingkoala.tools.get_booking import EXAMPLE_RESPONSE, read_booking
from bookingkoala_api_mcp.core.tools import tool

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "booking_id": BOOKING_ID,
        "provider_id": {**PROVIDER_ID, "description": "Provider or team id from list_providers."},
        "whole_schedule": {
            "type": "boolean",
            "description": "Assign every later booking of the recurring schedule too. Default: false.",
        },
        "even_if_unavailable": {
            "type": "boolean",
            "description": "Assign although the provider is not available then. Default: false.",
        },
    },
    "required": ["booking_id", "provider_id"],
    "additionalProperties": False,
}


@tool(
    name="assign_provider",
    title="Assign provider",
    access="write",
    confirm=True,
    description="Assign a provider or team to a booking, or to its whole recurring schedule.",
    details=(
        "Puts the provider on the booking, as Assign in the booking's sidebar does, and returns the "
        "booking as get_booking shows it. BookingKoala tells the provider about the job. A provider who "
        "is not available at that time is refused unless even_if_unavailable is true."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /bookings/{booking_id}/assign",
    example_response=EXAMPLE_RESPONSE,
)
async def assign_provider(ctx: ToolContext, args: dict[str, Any]) -> Any:
    booking_id = int(args["booking_id"])
    body = {
        "booking_id": booking_id,
        "non_available_provider": bool(args.get("even_if_unavailable")),
        "apply_to_all": "true" if args.get("whole_schedule") else "false",
    }
    await api(ctx, "POST", f"/api/v6/providers/{int(args['provider_id'])}/assign-booking", json=body)
    return await read_booking(ctx, booking_id)
