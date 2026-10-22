#!/usr/bin/env python3
"""Add a customer to your BookingKoala store, after checking that the email is not there yet.

    python add_customer.py --first Dana --last Whitfield --email dana@example.com --phone 3145550147 \
        --address "4100 Lindell Blvd" --city "St. Louis" --state Missouri --zip 63108

BookingKoala emails the new customer an invitation to set a password.
"""

import argparse
import json

from bookingkoala_api_mcp.scripting import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--first", required=True, help="First name")
    parser.add_argument("--last", required=True, help="Last name")
    parser.add_argument("--email", required=True)
    parser.add_argument("--phone", help="Digits only for US numbers")
    parser.add_argument("--address", help="Street address")
    parser.add_argument("--apt")
    parser.add_argument("--city")
    parser.add_argument("--state")
    parser.add_argument("--zip")
    parser.add_argument("--country", default="United States")
    args = parser.parse_args()

    existing = [c for c in call("list_customers", {"search": args.email})["customers"] if c["email"] == args.email]
    if existing:
        raise SystemExit(f"{args.email} is already customer {existing[0]['customer_id']}")
    customer = call(
        "create_customer",
        {
            "first_name": args.first,
            "last_name": args.last,
            "email": args.email,
            "phone": args.phone,
            "address": args.address,
            "apt": args.apt,
            "city": args.city,
            "state": args.state,
            "zipcode": args.zip,
            "country": args.country if args.address else None,
        },
    )
    print(json.dumps(customer, indent=2))


if __name__ == "__main__":
    run(main)
