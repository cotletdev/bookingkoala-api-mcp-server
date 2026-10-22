"""Resend an invoice: the Resend popup of an invoice, `POST /bkinvoice/v1/resend` (admin bundle 227).

Body `{delivery: {send_cust_email, send_cust_sms, attach_pdf, cc_emails, billing_emails}, _id, uid, sync_inv}`;
the popup fills `delivery` from the invoice's own `settings.delivery` (`GET /bkinvoice/v1/invoices/{id}`).
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from bookingkoala_api_mcp.bookingkoala.client import api
from bookingkoala_api_mcp.core.errors import ErrorCode, ToolError
from bookingkoala_api_mcp.core.tools import tool

if TYPE_CHECKING:
    from bookingkoala_api_mcp.core.context import ToolContext


def _obj(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


_INVOICE_ID = re.compile(r"^[0-9a-f]{24}$")

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "invoice_id": {"type": "string", "pattern": "^[0-9a-f]{24}$", "description": "invoice_id from list_invoices."},
        "email": {"type": "boolean", "description": "Email the invoice to the customer. Default: true."},
        "sms": {"type": "boolean", "description": "Text the invoice link to the customer. Default: false."},
        "attach_pdf": {"type": "boolean", "description": "Attach the PDF to the email. Default: as the invoice."},
    },
    "required": ["invoice_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "invoice_id": "6716a3f2c1e8b94d2a7f0c15",
    "customer_id": 2,
    "email": True,
    "sms": False,
    "attach_pdf": True,
    "cc_emails": [],
    "sent": True,
}


def _yes(value: Any) -> bool:
    return value is True or str(value).lower() in ("yes", "true", "1")


async def _invoice(ctx: ToolContext, args: dict[str, Any]) -> dict[str, Any]:
    invoice_id = str(args["invoice_id"]).strip().lower()
    if not _INVOICE_ID.match(invoice_id):
        raise ToolError("invoice_id is the 24-character id from list_invoices.", ErrorCode.INVALID_INPUT)
    if not args.get("email", True) and not args.get("sms", False):
        raise ToolError("Choose email, sms or both, else the invoice reaches nobody.", ErrorCode.INVALID_INPUT)
    invoice = await api(ctx, "GET", f"/bkinvoice/v1/invoices/{invoice_id}", params={"addons": "false"})
    if not isinstance(invoice, dict) or not invoice.get("_id"):
        raise ToolError("No invoice with this invoice_id in the store.", ErrorCode.INVALID_INPUT)
    return invoice


async def check_resend(ctx: ToolContext, args: dict[str, Any]) -> None:
    """Before approval: an unknown invoice or no channel fails now."""
    await _invoice(ctx, args)


@tool(
    name="resend_invoice",
    title="Resend an invoice",
    access="write",
    confirm=True,
    description="Send an invoice to its customer again by email, text or both.",
    details=(
        "Sends an existing invoice from list_invoices to its customer again, as the invoice's Resend button "
        "does: by email (default) and, with sms true, a text with the invoice link. The invoice's CC and "
        "billing addresses get the email too. attach_pdf defaults to the invoice's own setting. The invoice "
        "itself does not change. The customer gets it at once. BookingKoala refuses some resends with a "
        "warning, for example a void invoice; the error carries its message. By default you confirm each call; "
        "you can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /invoices/{invoice_id}/resend",
    example_response=EXAMPLE_RESPONSE,
    check=check_resend,
)
async def resend_invoice(ctx: ToolContext, args: dict[str, Any]) -> Any:
    invoice = await _invoice(ctx, args)
    settings = _obj(invoice.get("settings"))
    saved = _obj(settings.get("delivery"))
    email, sms = args.get("email", True), args.get("sms", False)
    attach_pdf = args["attach_pdf"] if "attach_pdf" in args else _yes(saved.get("attach_pdf"))
    cc_emails = saved.get("cc_emails") or []
    await api(
        ctx,
        "POST",
        "/bkinvoice/v1/resend",
        json={
            "delivery": {
                "send_cust_email": "yes" if email else "no",
                "send_cust_sms": "yes" if sms else "no",
                "attach_pdf": "yes" if attach_pdf else "no",
                "cc_emails": cc_emails,
                "billing_emails": saved.get("billing_emails") or [],
            },
            "_id": invoice["_id"],
            "uid": invoice.get("uid"),
            "sync_inv": False,
        },
    )
    return {
        "invoice_id": invoice["_id"],
        "customer_id": invoice.get("uid"),
        "email": email,
        "sms": sms,
        "attach_pdf": attach_pdf,
        "cc_emails": [c.get("email_id") if isinstance(c, dict) else c for c in cc_emails],
        "sent": True,
    }
