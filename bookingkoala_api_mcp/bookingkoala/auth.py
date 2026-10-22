"""Who is signed in: the store owner's own user record (GET /api/v6/users/{id}), for "Signed in as ..."."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bookingkoala_api_mcp.bookingkoala.client import api, session
from bookingkoala_api_mcp.core.errors import AuthExpiredError

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext


async def whoami(ctx: ToolContext) -> str | None:
    """None only when BookingKoala says signed out; any other failure raises (detection tries again later)."""
    s = session(ctx)
    if s is None:
        return None
    try:
        me = await api(ctx, "GET", f"/api/v6/users/{s.user_id}", s=s) or {}
    except AuthExpiredError:
        return None
    name = " ".join(p for p in (me.get("first_name"), me.get("last_name")) if p).strip()
    email = me.get("email_id")
    who = f"{name} ({email})" if name and email else name or email or None
    return f"{who}, {s.store}" if who else None
