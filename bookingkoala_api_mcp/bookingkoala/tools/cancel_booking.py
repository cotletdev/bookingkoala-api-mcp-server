"""Cancel booking: `cancellation-preview`, then POST `/api/v6/bookings/{id}/cancel`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bookingkoala_api_mcp.bookingkoala.client import api
from bookingkoala_api_mcp.bookingkoala.tools._bookings import BOOKING_ID
from bookingkoala_api_mcp.core.errors import ErrorCode, ToolError
from bookingkoala_api_mcp.core.tools import tool

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "booking_id": BOOKING_ID,
        "whole_schedule": {
            "type": "boolean",
            "description": "Cancel the whole recurring schedule from this booking on. Default: false.",
        },
        "reason": {"type": "string", "description": "Why it is cancelled (kept on the booking)."},
        "notify": {
            "type": "boolean",
            "description": "Email the customer and providers about it. Default: false.",
        },
    },
    "required": ["booking_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"booking_id": 11, "cancelled": True, "cancel_type": "onetime"}


@tool(
    name="cancel_booking",
    title="Cancel booking",
    access="write",
    confirm=True,
    description="Cancel one booking or its whole recurring schedule, without a cancellation fee.",
    details=(
        "Checks the store's cancellation rules first (a store that requires a reason gets the 'Other' "
        "reason with your text), then cancels as Cancel in the booking's sidebar does, with no fee. "
        "Nobody is told unless notify is true. Cancelled bookings leave list_bookings."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /bookings/{booking_id}/cancel",
    example_response=EXAMPLE_RESPONSE,
)
async def cancel_booking(ctx: ToolContext, args: dict[str, Any]) -> Any:
    booking_id = int(args["booking_id"])
    cancel_type = "recurring" if args.get("whole_schedule") else "onetime"
    path = f"/api/v6/bookings/{booking_id}"
    preview = await api(ctx, "GET", f"{path}/cancellation-preview?cancel_type={cancel_type}") or {}
    reason = (args.get("reason") or "").strip()
    reason_ids: list[int] = []
    if preview.get("is_reason_required"):
        reasons = await api(ctx, "GET", "/api/v3/cancellation-reason") or []
        other = [r["id"] for r in reasons if str(r.get("title", "")).strip().lower() == "other"]
        reason_ids = other[:1] or [r["id"] for r in reasons[:1]]
    if preview.get("is_comment_required") and not reason:
        raise ToolError("This store needs a reason to cancel: give reason.", ErrorCode.INVALID_INPUT)
    body = {
        "cancel_type": cancel_type,
        "cancellation_reason": reason_ids,
        "reason": reason,
        "cancellation_fee": 0,
        "provider_cancellation_pay": 0,
        "is_canceled_after_5pm": bool(preview.get("is_canceled_after_5pm")),
        "exclude_notifications": not args.get("notify"),
        "discount": 0,
        "tax_amount": 0,
    }
    await api(ctx, "POST", f"{path}/cancel", json=body)
    return {"booking_id": booking_id, "cancelled": True, "cancel_type": cancel_type}
