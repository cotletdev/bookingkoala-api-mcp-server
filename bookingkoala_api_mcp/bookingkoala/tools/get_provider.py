"""Get provider or team, with reviews and payment logs."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bookingkoala_api_mcp.bookingkoala.client import api, require_session
from bookingkoala_api_mcp.bookingkoala.tools._people import address, iso, name_of, rating, record_id, status_of
from bookingkoala_api_mcp.core.errors import ErrorCode, ToolError
from bookingkoala_api_mcp.core.tools import tool

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "provider_id": {"type": "integer", "description": "provider_id from list_providers (a team too)."},
        "payment_logs_limit": {
            "type": "integer",
            "description": "Newest payment logs to include, 1 to 50. Default: 20.",
        },
    },
    "required": ["provider_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "provider_id": 3,
    "name": "Marcus Reed",
    "type": "single",
    "category": "IC",
    "email": "marcus.reed@example.com",
    "phone": "2125550133",
    "status": "active",
    "payment_status": "active",
    "priority": 1,
    "created_at": "2026-06-11T07:01:04Z",
    "address": None,
    "rating": {"average": 5, "count": 2},
    "team_member_ids": [],
    "team_lead_id": None,
    "team_ids": [],
    "sets_own_schedule": True,
    "sees_unassigned_jobs": True,
    "reviews": [
        {
            "review_id": 2,
            "booking_id": 2,
            "customer_id": 2,
            "customer_name": "Linda Morales",
            "rating": 5,
            "review": "Very professional and friendly.",
            "date": "2026-10-20T19:24:53Z",
        }
    ],
    "payment_logs": [],
}


def _reviews(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    users = data.get("users_info") or {}
    out = []
    for raw in data.get("reviews") or []:
        user = users.get(str(raw.get("uid"))) or {}
        out.append(
            {
                "review_id": raw.get("_id"),
                "booking_id": raw.get("booking_id"),
                "customer_id": raw.get("uid"),
                "customer_name": name_of(user) or None,
                "rating": raw.get("rating"),
                "review": raw.get("review") or "",
                "date": iso(raw.get("review_date")),
            }
        )
    return out


@tool(
    name="get_provider",
    title="Get provider",
    access="read",
    confirm=False,
    description="One provider or team: contact, category, team members, reviews and payment logs.",
    details=(
        "Returns the provider's profile as their page in the admin shows it: contact details, IC or W2 "
        "category, priority, scheduling permissions, the team's members and lead (for a team) or the teams "
        "it belongs to, customer reviews and the newest payment logs (what the store paid the provider). "
        "Payment logs come as BookingKoala records them."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /providers/{provider_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def get_provider(ctx: ToolContext, args: dict[str, Any]) -> Any:
    pid = record_id(args.get("provider_id"), "provider_id")
    size = max(1, min(int(args.get("payment_logs_limit") or 20), 50))
    s = require_session(ctx)
    profile = await api(ctx, "GET", f"/api/v3/provider/{pid}", s=s)
    if not isinstance(profile, dict) or profile.get("role") != "provider":
        raise ToolError("No provider with this provider_id in the store.", ErrorCode.TARGET_ERROR)
    review_query = {"limit": 20, "page": 1, "s": "", "location": "", "industry": "", "start_date": "", "end_date": ""}
    reviews = await api(ctx, "GET", f"/api/v6/providers/{pid}/reviews", s=s, params=review_query)
    pay_query = {"limit": size, "page": 1, "pagination": "new"}
    logs = await api(ctx, "GET", f"/api/v3/provider/{pid}/payment-logs", s=s, params=pay_query)
    provider = profile.get("provider") or {}
    return {
        "provider_id": profile.get("_id") or pid,
        "name": provider.get("team_name") or name_of(profile),
        "type": provider.get("provider_type") or "single",
        "category": provider.get("provider_category") or None,
        "email": profile.get("email_id") or "",
        "phone": profile.get("phone_number") or "",
        "status": status_of(profile.get("status")),
        "payment_status": provider.get("payment_status") or None,
        "priority": provider.get("priority"),
        "created_at": iso(profile.get("created_on")),
        "address": address(profile.get("address")),
        "rating": rating(profile.get("rating_stats")),
        "team_member_ids": provider.get("team_members") or [],
        "team_lead_id": provider.get("team_lead_id") or None,
        "team_ids": (provider.get("team") or {}).get("team_ids") or [],
        "sets_own_schedule": provider.get("provider_set_own_schedule") == "yes",
        "sees_unassigned_jobs": provider.get("show_unassigned_jobs") == "yes",
        "reviews": _reviews(reviews),
        "payment_logs": logs if isinstance(logs, list) else [],
    }
