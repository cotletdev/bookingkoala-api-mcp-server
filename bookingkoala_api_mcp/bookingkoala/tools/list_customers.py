"""List customers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bookingkoala_api_mcp.bookingkoala.client import api
from bookingkoala_api_mcp.core.helpers import limit, page_cursor
from bookingkoala_api_mcp.core.tools import tool

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "search": {"type": "string", "description": "Part of a name, email or phone number."},
        "status": {
            "type": "string",
            "enum": ["active", "inactive"],
            "description": "active or inactive (deactivated) customers. Default: active.",
        },
        "limit": {"type": "integer", "description": "1 to 100. Default: 20."},
        "cursor": {"type": "string", "description": "next_cursor from the previous call."},
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "customers": [
        {
            "customer_id": 2,
            "first_name": "Linda",
            "last_name": "Morales",
            "email": "linda.morales@example.com",
            "phone": "2125550147",
            "is_new": True,
            "blocked": False,
            "tags": [],
            "note": "",
        }
    ],
    "next_cursor": None,
}


def customer_row(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "customer_id": raw.get("id") or raw.get("_id"),
        "first_name": raw.get("first_name") or "",
        "last_name": raw.get("last_name") or "",
        "email": raw.get("email_id") or "",
        "phone": raw.get("phone_number") or "",
        "is_new": bool(raw.get("is_new")),
        "blocked": bool(raw.get("is_blocked")),
        "tags": raw.get("tags") or [],
        "note": raw.get("note") or "",
    }


@tool(
    name="list_customers",
    title="List customers",
    access="read",
    confirm=False,
    description="Customers of the store, with email and phone; search by name, email or phone.",
    details=(
        "Returns the store's customers as the Customers page lists them, newest first, active or deactivated. "
        "BookingKoala gives no total: next_cursor is set while a full page comes back. Use customer_id in "
        "get_customer."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /customers",
    example_response=EXAMPLE_RESPONSE,
)
async def list_customers(ctx: ToolContext, args: dict[str, Any]) -> Any:
    page, size = page_cursor(args.get("cursor")), limit(args, 20, 100)
    query = {"limit": size, "page": page, "status": args.get("status") or "active", "s": args.get("search") or ""}
    rows = await api(ctx, "GET", "/api/v3/customers", params=query) or []
    return {
        "customers": [customer_row(row) for row in rows],
        "next_cursor": str(page + 1) if len(rows) >= size else None,
    }
