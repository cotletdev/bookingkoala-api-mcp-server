"""Booking shapes shared by the booking tools.

Bookings are small integers (`_id`). A booking's `status` is a number: 0 upcoming, 1 completed, 8 unassigned
(seen on the team store); the others come from the list filter the panel uses. Times: `booking_date`
`YYYY-MM-DD`, `arrival_time` an `HHMM` number in the store's time zone.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from bookingkoala_api_mcp.core.errors import ErrorCode, ToolError

BOOKING_ID: dict[str, Any] = {"type": "integer", "minimum": 1, "description": "Booking id from list_bookings."}
PROVIDER_ID: dict[str, Any] = {
    "type": "integer",
    "minimum": 1,
    "description": "Provider or team id (BookingKoala's provider `_id`).",
}
# Seen on the team store: 0 upcoming, 1 completed, 8 unassigned. Others pass through as numbers.
STATUSES = {0: "upcoming", 1: "completed", 2: "cancelled", 8: "unassigned"}

EXAMPLE_BOOKING: dict[str, Any] = {
    "booking_id": 3,
    "status": "upcoming",
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
    "payment_method": "cash",
    "total": 200.0,
    "charged": False,
}


def text(value: Any) -> str | None:
    value = str(value).strip() if value is not None else ""
    return value or None


def time_of(value: Any) -> str | None:
    """`1100` -> `11:00`; None when unset."""
    if not isinstance(value, int | float) or value < 0:
        return None
    hours, minutes = divmod(int(value), 100)
    return f"{hours:02d}:{minutes:02d}"


def parse_time(value: str, field: str) -> int:
    """`11:00`, `9:30` or `14` -> the `HHMM` number BookingKoala keeps."""
    raw = value.strip().lower().replace(" ", "")
    pm, am = raw.endswith("pm"), raw.endswith("am")
    raw = raw.removesuffix("pm").removesuffix("am")
    hours_raw, _, minutes_raw = raw.partition(":")
    try:
        hours, minutes = int(hours_raw), int(minutes_raw or 0)
    except ValueError:
        raise ToolError(f"{field} is a time like 09:30.", ErrorCode.INVALID_INPUT) from None
    if pm and hours < 12:
        hours += 12
    if am and hours == 12:
        hours = 0
    if not (0 <= hours < 24 and 0 <= minutes < 60):
        raise ToolError(f"{field} is a time like 09:30.", ErrorCode.INVALID_INPUT)
    return hours * 100 + minutes


def parse_day(value: str, field: str) -> str:
    try:
        return date.fromisoformat(value.strip()).isoformat()
    except ValueError:
        raise ToolError(f"{field} is a date like 2026-11-16.", ErrorCode.INVALID_INPUT) from None


def money(value: Any) -> float | None:
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def status_of(value: Any) -> str | int | None:
    return STATUSES.get(value, value) if isinstance(value, int) else None


def address_text(address: dict[str, Any] | None) -> str | None:
    if not address:
        return None
    line = text(address.get("address"))
    apt = text(address.get("apt"))
    return ", ".join(part for part in (line, f"apt {apt}" if apt else None) if part) or None


def booking_row(
    booking: dict[str, Any], users: dict[str, Any] | None = None, addresses: dict[str, Any] | None = None
) -> dict[str, Any]:
    """One booking in list form; `users` and `addresses` are the search answer's `users_info` and `addresses`."""
    users, addresses = users or {}, addresses or {}
    customer = users.get(str(booking.get("uid"))) or {}
    provider_ids = [int(pid) for pid in booking.get("provider_ids") or []]
    return {
        "booking_id": booking.get("_id"),
        "status": status_of(booking.get("status")),
        "date": booking.get("booking_date"),
        "arrival_time": time_of(booking.get("arrival_time")),
        "length_minutes": booking.get("length"),
        "occurrence": booking.get("occurrence"),
        "recurring_id": booking.get("recurring_id") or None,
        "frequency": text(booking.get("frequency_repeat_slug")),
        "customer": {
            "customer_id": booking.get("uid"),
            "name": text(customer.get("full_name")),
            "email": text(customer.get("email_id")),
        },
        "address": address_text(addresses.get(str(booking.get("address_id")))),
        "provider_ids": provider_ids,
        "providers": [
            {"provider_id": pid, "name": text((users.get(str(pid)) or {}).get("full_name"))} for pid in provider_ids
        ],
        "payment_method": text(booking.get("payment_method")),
        "total": money(booking.get("final_amount")),
        "charged": bool(booking.get("is_charged")),
    }
