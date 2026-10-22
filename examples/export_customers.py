#!/usr/bin/env python3
"""Export the customers of your BookingKoala store to CSV or JSON: name, email, phone, tags, note.

    python export_customers.py --out customers.csv
    python export_customers.py --status inactive --out deactivated.csv
    python export_customers.py --search smith

Pages are followed automatically.
"""

import argparse

from bookingkoala_api_mcp.scripting import paginate, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--status", choices=["active", "inactive"], default="active")
    parser.add_argument("--search", help="Part of a name, email or phone number")
    parser.add_argument("--max", type=int, help="Stop after this many customers")
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()

    params = {"status": args.status, "search": args.search, "limit": 20}
    write_rows(list(paginate("list_customers", params, "customers", args.max)), args.out)


if __name__ == "__main__":
    run(main)
