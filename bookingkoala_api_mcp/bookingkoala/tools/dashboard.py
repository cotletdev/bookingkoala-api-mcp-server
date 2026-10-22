"""Dashboard totals."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

from bookingkoala_api_mcp.bookingkoala.client import api
from bookingkoala_api_mcp.core.errors import ErrorCode, ToolError
from bookingkoala_api_mcp.core.tools import tool

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "start_date": {"type": "string", "description": "YYYY-MM-DD. Default: first day of this month."},
        "end_date": {"type": "string", "description": "YYYY-MM-DD, included. Default: last day of this month."},
    },
    "required": [],
    "additionalProperties": False,
}

_SPLIT = {"total": 600, "bookings": 600, "custom_invoices": 0, "separate_charges": 0}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "start_date": "2026-10-01",
    "end_date": "2026-10-31",
    "revenue": {
        "total": _SPLIT,
        "paid": {**_SPLIT, "total": 400, "bookings": 400},
        "pending": {**_SPLIT, "total": 200, "bookings": 200},
        "tips": {**_SPLIT, "total": 0, "bookings": 0},
        "one_time": 0,
        "recurring": 400,
        "sales_tax": 0,
        "refunds": 0,
        "parking": 0,
        "service_fees": 0,
        "reschedule_fees": 0,
        "average_per_booking": 200,
    },
    "provider_payments": {
        "total": {**_SPLIT, "total": 150, "bookings": 150},
        "paid": {**_SPLIT, "total": 0, "bookings": 0},
        "pending": {**_SPLIT, "total": 150, "bookings": 150},
        "contractors_ic": 150,
        "employees_w2": 0,
        "job_bonuses": 0,
        "cancellation_fees": 0,
        "tips": 0,
    },
    "bookings": {
        "total": 3,
        "one_time": 0,
        "recurring": 3,
        "created": 10,
        "unassigned": 2,
        "cancelled": 0,
        "cancelled_same_day": 0,
        "new_customers": 0,
    },
    "ratings": {"average": 5, "ratings": 2, "reviews": 2, "by_stars": {"5": 2}},
    "referrals": {"invited": 0, "registered": 0, "booked": 0, "completed": 0},
}


def _day(value: Any, field: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        raise ToolError(f"{field} must be a date as YYYY-MM-DD.", ErrorCode.INVALID_INPUT) from None


def _num(value: Any) -> float | int:
    return value if isinstance(value, int | float) else 0


def _split(raw: Any) -> dict[str, Any]:
    raw = raw if isinstance(raw, dict) else {}
    return {key: _num(raw.get(key)) for key in ("total", "bookings", "custom_invoices", "separate_charges")}


@tool(
    name="dashboard",
    title="Dashboard",
    access="read",
    confirm=False,
    description="Store totals for a date range: revenue, provider pay, bookings, ratings, referrals.",
    details=(
        "Returns the figures of the admin Dashboard for the dates given (this month by default): revenue "
        "paid and pending, split into bookings, custom invoices and separate charges; what providers earned "
        "and what is still unpaid; booking counts, unassigned and cancelled included; ratings and referrals. "
        "Amounts are in the store's currency."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /dashboard",
    example_response=EXAMPLE_RESPONSE,
)
async def dashboard(ctx: ToolContext, args: dict[str, Any]) -> Any:
    today = datetime.now(ZoneInfo(ctx.profile.timezone or "UTC")).date()
    start = _day(args.get("start_date"), "start_date") or today.replace(day=1)
    next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
    end = _day(args.get("end_date"), "end_date") or next_month - timedelta(days=1)
    if end < start:
        raise ToolError("end_date must not be before start_date.", ErrorCode.INVALID_INPUT)
    query = {"start_date": start.isoformat(), "end_date": end.isoformat()}
    data = await api(ctx, "GET", "/bkreport/v1/reports/dashboard", params=query) or {}
    revenue, trends = data.get("revenue") or {}, data.get("trends") or {}
    extra = revenue.get("additional_revenue") or {}
    payments = data.get("payments") or {}
    by_category = payments.get("payments_by_category") or {}
    bonus = payments.get("additional_payments") or {}
    bookings = data.get("bookings") or {}
    ratings = data.get("ratings") or {}
    referrals = (data.get("referrals") or {}).get("referral_dashboard_report") or {}
    return {
        **query,
        "revenue": {
            "total": _split(revenue.get("total")),
            "paid": _split(revenue.get("paid_revenue")),
            "pending": _split(revenue.get("pending_revenue")),
            "tips": _split(revenue.get("tips")),
            "one_time": _num(revenue.get("one_time")),
            "recurring": _num(revenue.get("recurring")),
            "sales_tax": _num(revenue.get("sales_tax")),
            "refunds": _num(revenue.get("refund")),
            "parking": _num(extra.get("parking")),
            "service_fees": _num(extra.get("service_fee")),
            "reschedule_fees": _num(extra.get("reschedule_fee")),
            "average_per_booking": _num(trends.get("average_revenue_per_booking")),
        },
        "provider_payments": {
            "total": _split(payments.get("total")),
            "paid": _split(payments.get("paid_payments")),
            "pending": _split(payments.get("pending_payments")),
            "contractors_ic": _num((by_category.get("IC") or {}).get("total")),
            "employees_w2": _num((by_category.get("W2") or {}).get("total")),
            "job_bonuses": _num(bonus.get("job_bonuses")),
            "cancellation_fees": _num(bonus.get("cancellation_fee")),
            "tips": _num(bonus.get("tip")),
        },
        "bookings": {
            "total": _num(bookings.get("total")),
            "one_time": _num(bookings.get("one_time")),
            "recurring": _num(bookings.get("recurring")),
            "created": _num(bookings.get("created_bookings")),
            "unassigned": _num(bookings.get("unassigned_bookings")),
            "cancelled": _num(bookings.get("cancelled_bookings")),
            "cancelled_same_day": _num(bookings.get("cancelled_same_day")),
            "new_customers": _num((bookings.get("booking_metrics") or {}).get("new_customers")),
        },
        "ratings": {
            "average": _num(ratings.get("overall_average_rating")),
            "ratings": _num(ratings.get("total_overall_ratings")),
            "reviews": _num(ratings.get("total_reviews")),
            "by_stars": ratings.get("starwise_rating") or {},
        },
        "referrals": {key: _num(referrals.get(key)) for key in ("invited", "registered", "booked", "completed")},
    }
