#!/usr/bin/env python3
"""Move the recurring BookingKoala visits of one day to their next visit date, for a closed day.

    python reschedule_day.py --date 2026-11-19              # shows what would move
    python reschedule_day.py --date 2026-11-19 --move --notify

BookingKoala moves a recurring visit only to the date of a later visit in its schedule, so each booking goes to
the next visit of its own schedule. One-time bookings and stores that charge a reschedule fee are listed for
the panel. With --notify BookingKoala emails the customer and providers.
"""

import argparse

from bookingkoala_api_mcp.core.errors import ToolError
from bookingkoala_api_mcp.scripting import call, paginate, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--date", required=True, help="The closed day, YYYY-MM-DD")
    parser.add_argument("--move", action="store_true", help="Move the bookings, not only show the plan")
    parser.add_argument("--notify", action="store_true", help="Email the customer and providers")
    args = parser.parse_args()

    day = {"start_date": args.date, "end_date": args.date, "status": "upcoming", "limit": 20}
    bookings = list(paginate("list_bookings", day, "bookings"))
    print(f"{len(bookings)} bookings on {args.date}")
    for booking in bookings:
        who = (booking.get("customer") or {}).get("name")
        label = f"#{booking['booking_id']} {who} {booking.get('arrival_time')}"
        if not booking.get("recurring_id"):
            print(f"  panel {label}: one-time booking")
            continue
        later = paginate(
            "list_bookings",
            {"status": "upcoming", "customer_id": (booking.get("customer") or {}).get("customer_id"), "limit": 20},
            "bookings",
        )
        dates = sorted(
            b["date"] for b in later if b.get("recurring_id") == booking["recurring_id"] and b["date"] > args.date
        )
        if not dates:
            print(f"  panel {label}: no later visit in the schedule")
            continue
        if not args.move:
            print(f"  plan {label} -> {dates[0]}")
            continue
        try:
            call("reschedule_booking", {"booking_id": booking["booking_id"], "date": dates[0], "notify": args.notify})
        except ToolError as err:
            print(f"  panel {label}: {err}")
            continue
        print(f"  moved {label} -> {dates[0]}")


if __name__ == "__main__":
    run(main)
