"""List drafts: GET `/api/v6/drafts?limit&page&location=&industry=&s=` (drafts and quotes)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode

from bookingkoala_api_mcp.bookingkoala.client import api
from bookingkoala_api_mcp.bookingkoala.tools._bookings import money, text, time_of
from bookingkoala_api_mcp.core.helpers import limit, page_cursor
from bookingkoala_api_mcp.core.tools import tool

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "search": {"type": "string", "description": "Customer name or email."},
        "limit": {"type": "integer", "minimum": 1, "maximum": 50, "description": "Page size. Default: 20."},
        "cursor": {"type": "string", "description": "next_cursor from the previous call."},
    },
    "additionalProperties": False,
}

EXAMPLE_DRAFT: dict[str, Any] = {
    "draft_id": 1,
    "is_quote": False,
    "customer_id": 2,
    "customer_name": "Dana Whitfield",
    "date": None,
    "arrival_time": None,
    "industry_id": 1,
    "form_id": 1,
    "total": 200.0,
    "duplicate_of": 3,
}


def _row(row: dict[str, Any]) -> dict[str, Any]:
    customer = row.get("customer") or {}
    name = text(customer.get("full_name")) or text(
        " ".join(filter(None, [customer.get("first_name"), customer.get("last_name")]))
    )
    return {
        "draft_id": row.get("_id"),
        "is_quote": bool(row.get("is_quote") or row.get("quote") is True),
        "customer_id": row.get("uid") or customer.get("id") or None,
        "customer_name": name,
        "date": text(row.get("booking_date")),
        "arrival_time": time_of(row.get("arrival_time")) if row.get("arrival_time") else None,
        "industry_id": row.get("industry_id"),
        "form_id": row.get("form_id"),
        "total": money(row.get("final_amount")),
        "duplicate_of": row.get("duplicate_from") or None,
    }


@tool(
    name="list_drafts",
    title="List drafts",
    access="read",
    description="Draft bookings and quotes saved in the store, not yet booked.",
    details=(
        "Lists the drafts and quotes on the Drafts page: customer, date when set, total and whether it is "
        "a quote. create_booking leaves a draft here. Page with next_cursor."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /drafts",
    example_response={"drafts": [EXAMPLE_DRAFT], "next_cursor": None},
)
async def list_drafts(ctx: ToolContext, args: dict[str, Any]) -> Any:
    page, size = page_cursor(args.get("cursor")), limit(args, 20, 50)
    query = urlencode(
        {"limit": size, "page": page, "location": "", "industry": "", "s": (args.get("search") or "").strip()}
    )
    data = await api(ctx, "GET", f"/api/v6/drafts?{query}")
    rows = data if isinstance(data, list) else (data or {}).get("drafts") or [] if isinstance(data, dict) else []
    return {
        "drafts": [_row(row) for row in rows if isinstance(row, dict)],
        "next_cursor": str(page + 1) if len(rows) >= size else None,
    }
