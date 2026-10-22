"""Get booking: GET `/api/v6/bookings/{id}`, `/price-details` and `/provider-payments`."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from bookingkoala_api_mcp.bookingkoala.client import api
from bookingkoala_api_mcp.bookingkoala.tools._bookings import (
    BOOKING_ID,
    EXAMPLE_BOOKING,
    address_text,
    booking_row,
    money,
    text,
    time_of,
)
from bookingkoala_api_mcp.core.errors import ErrorCode, ToolError
from bookingkoala_api_mcp.core.tools import tool

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"booking_id": BOOKING_ID},
    "required": ["booking_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    **EXAMPLE_BOOKING,
    "end_time": "12:00",
    "customer": {
        "customer_id": 2,
        "name": "Dana Whitfield",
        "email": "dana.whitfield@example.com",
        "phone": "2125550147",
    },
    "providers": [{"provider_id": 3, "name": "Marcus Lee", "email": "marcus.lee@example.com"}],
    "service": {"industry_id": 1, "form_id": 1, "parameters": [{"name": "bedrooms", "quantity": 1}], "extras": []},
    "notes": {"booking": None, "for_provider": None, "from_provider": None, "private": None},
    "price": {
        "service_total": 109.0,
        "frequency_discount": 10.9,
        "discounted_total": 98.1,
        "tax": 0.0,
        "tip": 0.0,
        "service_fee": 0.0,
        "final_amount": 200.0,
        "adjusted_price": 200.0,
    },
    "provider_pay": {"payable_amount": 50.0, "base_pay": 50.0, "tip": 0.0, "bonus": 0.0, "parking": 0.0},
    "created_at": 1792609493,
}


def _note(value: Any) -> str | None:
    """Notes are saved as HTML pages; an empty one is a bare `<html>` shell."""
    plain = re.sub(r"<[^>]+>", " ", str(value or ""))
    return text(re.sub(r"\s+", " ", plain))


@tool(
    name="get_booking",
    title="Get booking",
    access="read",
    description="One booking with its price breakdown, provider pay, notes and service.",
    details=(
        "Reads a booking by id: date and arrival window, customer, address, assigned providers, the service "
        "parameters and extras, notes, the price breakdown (service total, discounts, tax, tip, final amount) "
        "and what the providers are paid for it."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /bookings/{booking_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def get_booking(ctx: ToolContext, args: dict[str, Any]) -> Any:
    return await read_booking(ctx, int(args["booking_id"]))


async def read_booking(ctx: ToolContext, booking_id: int) -> dict[str, Any]:
    """The booking as get_booking returns it; also the answer of the booking writes."""
    data = await api(ctx, "GET", f"/api/v6/bookings/{booking_id}")
    if not isinstance(data, dict) or not data.get("_id"):
        raise ToolError(f"No booking {booking_id} in this store. Use list_bookings.", ErrorCode.TARGET_ERROR)
    price = await api(ctx, "GET", f"/api/v6/bookings/{booking_id}/price-details") or {}
    pay = await api(ctx, "GET", f"/api/v6/bookings/{booking_id}/provider-payments") or {}
    customer = data.get("customer_info") or {}
    providers = data.get("provider_info") or []
    users = {str(customer.get("id")): customer, **{str(p.get("id")): p for p in providers}}
    row = booking_row(data, users)
    return {
        **row,
        "end_time": time_of(data.get("end_time")),
        "customer": {**row["customer"], "phone": text(customer.get("phone_number"))},
        "address": address_text(data.get("address")),
        "providers": [
            {"provider_id": p.get("id"), "name": text(p.get("full_name")), "email": text(p.get("email_id"))}
            for p in providers
        ],
        "service": {
            "industry_id": data.get("industry_id"),
            "form_id": data.get("form_id"),
            "parameters": [
                {"name": p.get("name"), "quantity": p.get("quantity")} for p in data.get("pricing_parameter") or []
            ],
            "extras": [{"name": text(e.get("name")), "quantity": e.get("quantity")} for e in data.get("extras") or []],
        },
        "notes": {
            "booking": _note(data.get("booking_note")),
            "for_provider": _note(data.get("provider_note")),
            "from_provider": _note(data.get("note_from_provider")),
            "private": _note(data.get("private_customer_note")),
        },
        "price": {
            "service_total": money(price.get("service_total_to_display")),
            "frequency_discount": money(price.get("frequency_discount_amount")),
            "discounted_total": money(price.get("discounted_total")),
            "tax": money(price.get("booking_tax")),
            "tip": money(price.get("total_tip_amount")),
            "service_fee": money(price.get("service_fee")),
            "final_amount": money(price.get("final_amount")),
            "adjusted_price": money(price.get("adjusted_price")),
        },
        "provider_pay": {
            "payable_amount": money(pay.get("payable_amount")),
            "base_pay": money(pay.get("provider_payment")),
            "tip": money(pay.get("tip")),
            "bonus": money(pay.get("bonus")),
            "parking": money(pay.get("parking")),
        },
        "created_at": data.get("created_on"),
    }
