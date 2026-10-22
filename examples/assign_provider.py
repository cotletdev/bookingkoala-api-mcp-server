#!/usr/bin/env python3
"""Assign a provider or team to one BookingKoala booking, or to its whole recurring schedule.

    python assign_provider.py --booking 212 --provider 3
    python assign_provider.py --booking 212 --provider 3 --whole-schedule

BookingKoala tells the provider about the job. Ids come from list_bookings.py and list_providers.
"""

import argparse
import json

from bookingkoala_api_mcp.scripting import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--booking", type=int, required=True, help="Booking id")
    parser.add_argument("--provider", type=int, required=True, help="Provider or team id")
    parser.add_argument("--whole-schedule", action="store_true", help="Every later booking of the schedule too")
    parser.add_argument("--even-if-unavailable", action="store_true", help="Assign outside the provider's hours")
    args = parser.parse_args()

    booking = call(
        "assign_provider",
        {
            "booking_id": args.booking,
            "provider_id": args.provider,
            "whole_schedule": args.whole_schedule or None,
            "even_if_unavailable": args.even_if_unavailable or None,
        },
    )
    print(json.dumps({"booking_id": booking["booking_id"], "providers": booking.get("providers")}, indent=2))


if __name__ == "__main__":
    run(main)
