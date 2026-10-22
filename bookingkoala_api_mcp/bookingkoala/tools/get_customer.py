"""Get customer."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bookingkoala_api_mcp.bookingkoala.client import api, require_session
from bookingkoala_api_mcp.bookingkoala.tools._people import address, clock, iso, name_of, rating, record_id, status_of
from bookingkoala_api_mcp.core.errors import ErrorCode, ToolError
from bookingkoala_api_mcp.core.tools import tool

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"customer_id": {"type": "integer", "description": "customer_id from list_customers."}},
    "required": ["customer_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "customer_id": 2,
    "name": "Linda Morales",
    "first_name": "Linda",
    "last_name": "Morales",
    "email": "linda.morales@example.com",
    "phone": "2125550147",
    "company_name": "",
    "gender": "female",
    "status": "active",
    "is_new": True,
    "sms_notifications": False,
    "created_at": "2026-06-11T07:01:04Z",
    "rating": {"average": 5, "count": 2},
    "referral_code": "LINDAM",
    "addresses": [
        {
            "address_id": 7,
            "address": "540 W 28th Street, New York, NY, USA",
            "apt": "3E",
            "city": "New York",
            "state": "New York",
            "zipcode": "10001",
            "country": "",
            "default": True,
        }
    ],
    "bookings_count": {"upcoming_bookings": 1, "cash_bookings": 1},
    "pending_bookings": [
        {
            "booking_id": 1,
            "date": "2026-11-16",
            "arrival_time": "11:00",
            "length_minutes": 160,
            "occurrence": "recurring",
            "frequency": "every_4_weeks",
            "recurring_id": 1,
            "provider_ids": [3],
            "payment_method": "cash",
            "total": 200,
        }
    ],
    "gift_cards": [],
    "referrals": {},
}


def _booking(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "booking_id": raw.get("_id"),
        "date": raw.get("booking_date"),
        "arrival_time": clock(raw.get("arrival_time")),
        "length_minutes": raw.get("length"),
        "occurrence": raw.get("occurrence"),
        "frequency": raw.get("frequency_repeat_slug") or None,
        "recurring_id": raw.get("recurring_id") or None,
        "provider_ids": raw.get("provider_ids") or [],
        "payment_method": raw.get("payment_method") or None,
        "total": raw.get("final_amount"),
    }


@tool(
    name="get_customer",
    title="Get customer",
    access="read",
    confirm=False,
    description="One customer: contact details, addresses, booking counts and bookings not charged yet.",
    details=(
        "Returns the customer's profile as their page in the admin shows it: name, email, phone, saved "
        "addresses (address_id is what a booking or invoice for this customer uses), counts of upcoming and "
        "cash bookings, the bookings not charged yet (past ones included), gift cards received and the "
        "referral summary. Times "
        "of day are in the store's time zone."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /customers/{customer_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def get_customer(ctx: ToolContext, args: dict[str, Any]) -> Any:
    return await customer_detail(ctx, record_id(args.get("customer_id"), "customer_id"))


async def customer_detail(ctx: ToolContext, cid: int) -> dict[str, Any]:
    """The get_customer answer for one customer id (create_customer returns it too)."""
    s = require_session(ctx)
    profile = await api(ctx, "GET", f"/api/v3/customer/{cid}", s=s)
    if not isinstance(profile, dict) or profile.get("role") not in (None, "customer"):
        raise ToolError("No customer with this customer_id in the store.", ErrorCode.TARGET_ERROR)
    # One after another: parallel calls race the csrf preload and its cookie.
    addresses = await api(ctx, "GET", f"/api/v3/customer/{cid}/address", s=s)
    counts = await api(ctx, "GET", f"/api/v3/customer/{cid}/bookings-count", s=s)
    pending = await api(ctx, "GET", f"/api/v6/customers/{cid}/pending-bookings", s=s)
    gift_cards = await api(ctx, "GET", f"/api/v3/customer/{cid}/gift-cards", s=s, params={"type": "received"})
    referrals = await api(ctx, "GET", f"/api/v6/customers/{cid}/referral-summary", s=s)
    bookings = (pending.get("bookings") or []) if isinstance(pending, dict) else []
    return {
        "customer_id": profile.get("_id") or cid,
        "name": name_of(profile),
        "first_name": profile.get("first_name") or "",
        "last_name": profile.get("last_name") or "",
        "email": profile.get("email_id") or "",
        "phone": profile.get("phone_number") or "",
        "company_name": profile.get("company_name") or "",
        "gender": profile.get("gender") or None,
        "status": status_of(profile.get("status")),
        "is_new": bool(profile.get("is_new")),
        "sms_notifications": bool(profile.get("sms_notification")),
        "created_at": iso(profile.get("created_on")),
        "rating": rating(profile.get("rating_stats")),
        "referral_code": (profile.get("customer") or {}).get("refferal_code") or None,
        "addresses": [a for a in (address(row) for row in addresses or []) if a],
        "bookings_count": counts if isinstance(counts, dict) else {},
        "pending_bookings": [_booking(b) for b in bookings],
        "gift_cards": gift_cards or [],
        "referrals": referrals if isinstance(referrals, dict) else {},
    }
