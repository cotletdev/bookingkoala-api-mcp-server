"""Shapes of BookingKoala's user records (customers, providers, teams) as the people tools return them."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from bookingkoala_api_mcp.core.errors import ErrorCode, ToolError


def status_of(value: Any) -> str:
    """The app's numeric record status: 1 active, anything else inactive."""
    return "active" if value == 1 else "inactive"


def iso(epoch: Any) -> str | None:
    """Epoch seconds as UTC ISO 8601; None for a missing or zero value."""
    if not isinstance(epoch, int | float) or epoch <= 0:
        return None
    return datetime.fromtimestamp(epoch, UTC).isoformat().replace("+00:00", "Z")


def clock(hhmm: Any) -> str | None:
    """1100 -> "11:00": the app keeps arrival times as an hhmm number."""
    if not isinstance(hhmm, int) or hhmm < 0:
        return None
    return f"{hhmm // 100:02d}:{hhmm % 100:02d}"


def name_of(user: dict[str, Any]) -> str:
    full = user.get("full_name") or " ".join(p for p in (user.get("first_name"), user.get("last_name")) if p)
    return str(full or "").strip()


def address(raw: dict[str, Any] | None) -> dict[str, Any] | None:
    """A saved address; None when the record has none filled in."""
    if not raw or not (raw.get("address") or raw.get("city") or raw.get("zipcode")):
        return None
    return {
        "address_id": raw.get("_id") or raw.get("id"),
        "address": raw.get("address") or "",
        "apt": raw.get("apt") or "",
        "city": raw.get("city") or "",
        "state": raw.get("state") or "",
        "zipcode": raw.get("zipcode") or "",
        "country": raw.get("country") or "",
        "default": bool(raw.get("default")),
    }


def rating(raw: dict[str, Any] | None) -> dict[str, Any]:
    stats = raw or {}
    return {"average": stats.get("average") or 0, "count": stats.get("total_count") or 0}


def record_id(value: Any, field: str) -> int:
    """A positive integer id from the input."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = 0
    if number < 1:
        raise ToolError(f"{field} must be a positive integer id.", ErrorCode.INVALID_INPUT)
    return number
