#!/usr/bin/env python3
"""Your BookingKoala store's totals for a date range: revenue, provider pay, bookings, ratings, referrals.

python store_dashboard.py                                  # this month
python store_dashboard.py --from 2026-10-01 --to 2026-10-31
"""

import argparse
import json

from bookingkoala_api_mcp.scripting import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--from", dest="start", help="First day, YYYY-MM-DD. Default: first day of this month")
    parser.add_argument("--to", dest="end", help="Last day, YYYY-MM-DD. Default: last day of this month")
    args = parser.parse_args()

    print(json.dumps(call("dashboard", {"start_date": args.start, "end_date": args.end}), indent=2))


if __name__ == "__main__":
    run(main)
