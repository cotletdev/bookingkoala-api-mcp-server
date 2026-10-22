#!/usr/bin/env python3
"""Unpaid BookingKoala invoices past their due date, and a reminder to each customer when you ask.

    python overdue_invoices.py                      # lists them
    python overdue_invoices.py --out overdue.csv
    python overdue_invoices.py --remind             # emails each invoice again
    python overdue_invoices.py --remind --sms       # email and text

Unpaid and partly paid invoices count. A reminder is the invoice sent again, as Resend in the panel.
"""

import argparse
from datetime import UTC, datetime

from bookingkoala_api_mcp.scripting import call, paginate, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--days", type=int, default=0, help="Only invoices at least this many days past due")
    parser.add_argument("--remind", action="store_true", help="Send each overdue invoice to its customer again")
    parser.add_argument("--sms", action="store_true", help="Also text the invoice link")
    parser.add_argument("--out", help="Save the list to .csv or .json instead of printing")
    args = parser.parse_args()

    now = datetime.now(UTC)
    overdue = []
    for status in ("unpaid", "partially_paid"):
        for invoice in paginate("list_invoices", {"pay_status": status, "limit": 20}, "invoices"):
            due = invoice.get("due_at")
            late = now - datetime.fromisoformat(due) if due else None
            if late is not None and late.total_seconds() > 0 and late.days >= args.days:
                customer = invoice.get("customer") or {}
                overdue.append(
                    {
                        "invoice_id": invoice["invoice_id"],
                        "number": invoice.get("number"),
                        "customer": customer.get("name"),
                        "email": customer.get("email"),
                        "amount_due": invoice.get("amount_due"),
                        "due_at": due,
                    }
                )
    if not args.remind:
        write_rows(overdue, args.out)
        return
    for invoice in overdue:
        call("resend_invoice", {"invoice_id": invoice["invoice_id"], "sms": args.sms or None})
        print(f"  reminded {invoice['customer']} ({invoice['number']}, {invoice['amount_due']} due)")
    print(f"{len(overdue)} overdue invoices")


if __name__ == "__main__":
    run(main)
