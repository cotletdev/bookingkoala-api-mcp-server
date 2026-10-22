"""List providers and teams."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bookingkoala_api_mcp.bookingkoala.client import api
from bookingkoala_api_mcp.bookingkoala.tools._people import name_of, rating, status_of
from bookingkoala_api_mcp.core.helpers import limit, page_cursor
from bookingkoala_api_mcp.core.tools import tool

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "type": {
            "type": "string",
            "enum": ["all", "team"],
            "description": "all: providers and teams (default). team: teams only.",
        },
        "search": {"type": "string", "description": "Part of a name, email or phone number."},
        "status": {
            "type": "string",
            "enum": ["active", "inactive"],
            "description": "active or inactive (deactivated) providers. Default: active.",
        },
        "limit": {"type": "integer", "description": "1 to 100. Default: 20."},
        "cursor": {"type": "string", "description": "next_cursor from the previous call."},
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "providers": [
        {
            "provider_id": 4,
            "name": "Downtown Crew",
            "type": "team",
            "email": "",
            "phone": "",
            "status": "active",
            "priority": 2,
            "rating": {"average": 0, "count": 0},
            "team_member_ids": [5, 6],
            "team_ids": [],
            "team_lead_of": [],
        },
        {
            "provider_id": 5,
            "name": "Marcus Reed",
            "type": "single",
            "email": "marcus.reed@example.com",
            "phone": "2125550133",
            "status": "active",
            "priority": 3,
            "rating": {"average": 4.8, "count": 12},
            "team_member_ids": [],
            "team_ids": [4],
            "team_lead_of": [4],
        },
    ],
    "next_cursor": None,
}


def provider_row(raw: dict[str, Any]) -> dict[str, Any]:
    provider = raw.get("provider") or {}
    team = provider.get("team") or {}
    team_info = team.get("team_info") or {}
    return {
        "provider_id": raw.get("_id") or raw.get("id"),
        "name": provider.get("team_name") or name_of(raw),
        "type": provider.get("provider_type") or "single",
        "email": raw.get("email_id") or "",
        "phone": raw.get("phone_number") or "",
        "status": status_of(raw.get("status")),
        "priority": provider.get("priority"),
        "rating": rating(raw.get("rating_stats")),
        "team_member_ids": provider.get("team_members") or [],
        "team_ids": team.get("team_ids") or [],
        "team_lead_of": [int(k) for k, v in team_info.items() if (v or {}).get("team_lead") and str(k).isdigit()],
    }


@tool(
    name="list_providers",
    title="List providers",
    access="read",
    confirm=False,
    description="Providers (cleaners, technicians) and teams of the store, in priority order.",
    details=(
        "Returns the store's service providers as the Providers page lists them, single providers and teams "
        "together; type team returns teams only. A team lists its members' provider ids, a provider the "
        "teams it belongs to and leads. BookingKoala gives no total: next_cursor is set while a full page "
        "comes back. Use provider_id in get_provider and when assigning a booking."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /providers",
    example_response=EXAMPLE_RESPONSE,
)
async def list_providers(ctx: ToolContext, args: dict[str, Any]) -> Any:
    page, size = page_cursor(args.get("cursor")), limit(args, 20, 100)
    query = {
        "type": "team" if args.get("type") == "team" else "",
        "status": args.get("status") or "active",
        "limit": size,
        "page": page,
        "s": args.get("search") or "",
        "industry": "",
        "location": "",
        "sort": "",
    }
    rows = await api(ctx, "GET", "/api/v3/providers", params=query) or []
    return {
        "providers": [provider_row(row) for row in rows],
        "next_cursor": str(page + 1) if len(rows) >= size else None,
    }
