"""Create customer."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bookingkoala_api_mcp.bookingkoala.client import api, require_session
from bookingkoala_api_mcp.bookingkoala.tools.get_customer import EXAMPLE_RESPONSE as CUSTOMER
from bookingkoala_api_mcp.bookingkoala.tools.get_customer import customer_detail
from bookingkoala_api_mcp.core.errors import ErrorCode, ToolError
from bookingkoala_api_mcp.core.tools import tool

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext


def _text(description: str) -> dict[str, str]:
    return {"type": "string", "description": description}


INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "first_name": _text("First name."),
        "last_name": _text("Last name."),
        "email": _text("Email address. BookingKoala sends the customer an invitation to set a password."),
        "phone": _text("Phone number, digits only for US numbers, e.g. 2125550147."),
        "address": _text("Street address, e.g. 540 W 28th Street, New York, NY, USA."),
        "apt": _text("Apartment or suite."),
        "city": _text("City."),
        "state": _text("State, e.g. New York."),
        "zipcode": _text("ZIP or postal code."),
        "country": _text("Country, e.g. United States."),
        "gender": {"type": "string", "enum": ["male", "female", "other"], "description": "Gender, optional."},
        "sms_notifications": {"type": "boolean", "description": "Text the customer booking updates. Default: false."},
    },
    "required": ["first_name", "last_name", "email"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    **CUSTOMER,
    "customer_id": 9,
    "is_new": True,
    "rating": {"average": 0, "count": 0},
    "referral_code": None,
    "bookings_count": {"upcoming_bookings": 0, "cash_bookings": 0},
    "pending_bookings": [],
}


def _new_id(answer: Any) -> int | None:
    if isinstance(answer, int):
        return answer
    if isinstance(answer, dict):
        for key in ("_id", "id", "uid", "user_id"):
            if isinstance(answer.get(key), int):
                return answer[key]
        if isinstance(answer.get("user"), dict):
            return _new_id(answer["user"])
    return None


@tool(
    name="create_customer",
    title="Create customer",
    access="write",
    confirm=True,
    description="New customer in the store. BookingKoala emails them an invitation to set a password.",
    details=(
        "Adds a customer as Add Customer in the admin does, with an optional address that becomes their "
        "default service address. BookingKoala emails the customer at once to set a password for the "
        "store's booking page, so use their real address. An email already in the store is refused. "
        "Returns the new customer as get_customer does."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /customers",
    example_response=EXAMPLE_RESPONSE,
)
async def create_customer(ctx: ToolContext, args: dict[str, Any]) -> Any:
    s = require_session(ctx)
    email = args["email"].strip().lower()
    if "@" not in email:
        raise ToolError("email must be an email address.", ErrorCode.INVALID_INPUT)
    body: dict[str, Any] = {
        "first_name": args["first_name"].strip(),
        "last_name": args["last_name"].strip(),
        "email_id": email,
        "phone_number": "".join(ch for ch in args.get("phone") or "" if ch.isdigit() or ch == "+"),
        "created_by": s.user_id,
        "ip": s.ip,
        "gender": args.get("gender") or "",
        "send_sms_notification": "true" if args.get("sms_notifications") else "false",
        "address": (args.get("address") or "").strip(),
        "zipcode": (args.get("zipcode") or "").strip(),
        "short_address": "",
        "country": (args.get("country") or "").strip(),
        "city": (args.get("city") or "").strip(),
        "state": (args.get("state") or "").strip(),
        "apt": (args.get("apt") or "").strip(),
        "latlng": {"lat": 0, "lng": 0},
        "customer": {"source": "form"},
    }
    answer = await api(ctx, "POST", "/api/v3/customer", s=s, json=body)
    customer_id = _new_id(answer)
    if customer_id is None:
        found = await api(
            ctx, "GET", "/api/v3/customers", s=s, params={"limit": 5, "page": 1, "status": "active", "s": email}
        )
        match = [row for row in found or [] if str(row.get("email_id") or "").lower() == email]
        if not match:
            raise ToolError("BookingKoala did not create the customer.", ErrorCode.TARGET_ERROR)
        customer_id = int(match[0].get("id") or match[0].get("_id"))
    return await customer_detail(ctx, customer_id)
