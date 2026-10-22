#!/usr/bin/env python3
"""Rebook a repeat BookingKoala customer from their last visit: a draft copy and, optionally, the quote by email.

    python rebook_customer.py --customer "Dana Whitfield"
    python rebook_customer.py --customer dana@example.com --send-quote

The copy is saved as a draft with the same service, address, extras and price; open its form_url to pick the
date. --send-quote emails the customer a saved quote of theirs from your drafts with a link to book it.
"""

import argparse
import json

from bookingkoala_api_mcp.scripting import call, paginate, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--customer", required=True, help="Name, email or phone of the customer")
    parser.add_argument("--send-quote", action="store_true", help="Email the customer's newest saved quote")
    args = parser.parse_args()

    found = call("list_customers", {"search": args.customer, "limit": 5})["customers"]
    if len(found) != 1:
        names = ", ".join(f"{c['first_name']} {c['last_name']} ({c['email']})" for c in found) or "nobody"
        raise SystemExit(f"Need exactly one customer for {args.customer!r}, found: {names}")
    customer = found[0]
    visits = list(
        paginate("list_bookings", {"status": "completed", "customer_id": customer["customer_id"]}, "bookings")
    )
    if not visits:
        raise SystemExit(f"{customer['first_name']} {customer['last_name']} has no completed booking to copy")
    last = max(visits, key=lambda b: (b["date"], b.get("arrival_time") or ""))
    draft = call("create_booking", {"from_booking_id": last["booking_id"]})
    print(json.dumps({"copied_from": last["booking_id"], "draft": draft}, indent=2))

    if args.send_quote:
        quotes = [
            d
            for d in paginate("list_drafts", {"search": customer["email"]}, "drafts")
            if d.get("is_quote") and d.get("customer_id") == customer["customer_id"]
        ]
        if not quotes:
            raise SystemExit("No saved quote for this customer in your drafts")
        quote = max(quotes, key=lambda d: d["draft_id"])
        print(json.dumps(call("send_quote", {"draft_id": quote["draft_id"]}), indent=2))


if __name__ == "__main__":
    run(main)
