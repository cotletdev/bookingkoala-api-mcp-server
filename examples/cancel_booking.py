#!/usr/bin/env python3
"""Cancel one BookingKoala booking, or its whole recurring schedule from that booking on, with no fee.

    python cancel_booking.py --booking 231 --reason "Customer moved away"
    python cancel_booking.py --booking 231 --whole-schedule --notify

Nobody is emailed unless you pass --notify. The booking is shown first and you confirm with y.
"""

import argparse
import json

from bookingkoala_api_mcp.scripting import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--booking", type=int, required=True, help="Booking id")
    parser.add_argument("--reason", help="Why it is cancelled, kept on the booking")
    parser.add_argument("--whole-schedule", action="store_true", help="Cancel the rest of the recurring schedule")
    parser.add_argument("--notify", action="store_true", help="Email the customer and providers")
    parser.add_argument("--yes", action="store_true", help="Do not ask before cancelling")
    args = parser.parse_args()

    booking = call("get_booking", {"booking_id": args.booking})
    who = (booking.get("customer") or {}).get("name")
    print(
        f"#{booking['booking_id']} {who}, {booking.get('date')} {booking.get('arrival_time')}, {booking.get('service')}"
    )
    if not args.yes and input("Cancel it? [y/N] ").strip().lower() != "y":
        return
    result = call(
        "cancel_booking",
        {
            "booking_id": args.booking,
            "reason": args.reason,
            "whole_schedule": args.whole_schedule or None,
            "notify": args.notify or None,
        },
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run(main)
