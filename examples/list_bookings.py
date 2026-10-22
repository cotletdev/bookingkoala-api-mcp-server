#!/usr/bin/env python3
"""Export BookingKoala bookings to CSV or JSON: date, arrival time, customer, address, providers, total.

    python list_bookings.py --status upcoming --out upcoming.csv
    python list_bookings.py --status completed --from 2026-10-01 --to 2026-10-31 --out october.csv
    python list_bookings.py --status today

Pages are followed automatically.
"""

import argparse

from bookingkoala_api_mcp.scripting import paginate, run, write_rows

STATUSES = ["all", "upcoming", "today", "unassigned", "completed", "pending", "declined", "paused"]


def flat(booking: dict) -> dict:
    customer = booking.get("customer") or {}
    return {
        "booking_id": booking["booking_id"],
        "status": booking.get("status"),
        "date": booking.get("date"),
        "arrival_time": booking.get("arrival_time"),
        "length_minutes": booking.get("length_minutes"),
        "frequency": booking.get("frequency"),
        "customer": customer.get("name"),
        "customer_email": customer.get("email"),
        "address": booking.get("address"),
        "providers": ", ".join(p.get("name") or "" for p in booking.get("providers") or []),
        "total": booking.get("total"),
        "charged": booking.get("charged"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--status", choices=STATUSES, default="upcoming")
    parser.add_argument("--from", dest="start", help="First day, YYYY-MM-DD")
    parser.add_argument("--to", dest="end", help="Last day, YYYY-MM-DD")
    parser.add_argument("--search", help="Customer name, email or phone")
    parser.add_argument("--max", type=int, help="Stop after this many bookings")
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()

    params = {"status": args.status, "start_date": args.start, "end_date": args.end, "search": args.search, "limit": 20}
    rows = [flat(b) for b in paginate("list_bookings", params, "bookings", args.max)]
    write_rows(rows, args.out)


if __name__ == "__main__":
    run(main)
