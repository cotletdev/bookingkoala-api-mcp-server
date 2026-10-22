#!/usr/bin/env python3
"""Provider pay for a pay period: the store's totals, then each provider's payment logs.

    python provider_pay_report.py --from 2026-11-01 --to 2026-11-15
    python provider_pay_report.py --from 2026-11-01 --to 2026-11-15 --out pay.json

Totals come from the dashboard (paid, pending, contractors, employees, bonuses, tips).
"""

import argparse

from bookingkoala_api_mcp.scripting import call, paginate, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--from", dest="start", required=True, help="First day, YYYY-MM-DD")
    parser.add_argument("--to", dest="end", required=True, help="Last day, YYYY-MM-DD")
    parser.add_argument("--logs", type=int, default=20, help="Newest payment logs per provider, 1 to 50")
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()

    totals = call("dashboard", {"start_date": args.start, "end_date": args.end})["provider_payments"]
    rows = [{"provider": "All providers", **totals}]
    for provider in paginate("list_providers", {}, "providers"):
        detail = call("get_provider", {"provider_id": provider["provider_id"], "payment_logs_limit": args.logs})
        rows.append(
            {
                "provider": provider["name"],
                "provider_id": provider["provider_id"],
                "type": provider.get("type"),
                "payment_status": detail.get("payment_status"),
                "payment_logs": detail.get("payment_logs"),
            }
        )
    write_rows(rows, args.out)


if __name__ == "__main__":
    run(main)
