#!/usr/bin/env python3
"""Give each unassigned BookingKoala booking to the active provider with the fewest jobs that day.

    python assign_unassigned.py --from 2026-11-16 --to 2026-11-20            # shows the plan only
    python assign_unassigned.py --from 2026-11-16 --to 2026-11-20 --assign   # assigns after the plan

Load is counted from each provider's bookings on the job's date. BookingKoala tells the provider about each job
it assigns, and refuses a provider who is not available at that time: those jobs are listed and stay unassigned.
"""

import argparse
from collections import defaultdict

from bookingkoala_api_mcp.core.errors import ToolError
from bookingkoala_api_mcp.scripting import call, paginate, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--from", dest="start", required=True, help="First day, YYYY-MM-DD")
    parser.add_argument("--to", dest="end", required=True, help="Last day, YYYY-MM-DD")
    parser.add_argument("--assign", action="store_true", help="Assign the jobs, not only show the plan")
    args = parser.parse_args()

    window = {"start_date": args.start, "end_date": args.end, "limit": 20}
    jobs = list(paginate("list_bookings", {**window, "status": "unassigned"}, "bookings"))
    providers = [p for p in paginate("list_providers", {}, "providers") if p.get("type") != "team"]
    if not jobs or not providers:
        print(f"{len(jobs)} unassigned jobs, {len(providers)} active providers: nothing to do")
        return
    load: dict[tuple[int, str], int] = defaultdict(int)
    for provider in providers:
        params = {**window, "status": "upcoming", "provider_id": provider["provider_id"]}
        for booking in paginate("list_bookings", params, "bookings"):
            load[(provider["provider_id"], booking["date"])] += 1

    print(f"{len(jobs)} unassigned jobs from {args.start} to {args.end}")
    for job in sorted(jobs, key=lambda b: (b["date"], b.get("arrival_time") or "")):
        pick = min(providers, key=lambda p: (load[(p["provider_id"], job["date"])], p.get("priority") or 0))
        who = (job.get("customer") or {}).get("name")
        line = f"#{job['booking_id']} {who}, {job['date']} {job.get('arrival_time')} -> {pick['name']}"
        if not args.assign:
            print(f"  plan {line}")
            continue
        try:
            call("assign_provider", {"booking_id": job["booking_id"], "provider_id": pick["provider_id"]})
        except ToolError as err:
            print(f"  not placed {line}: {err}")
            continue
        load[(pick["provider_id"], job["date"])] += 1
        print(f"  assigned {line}")


if __name__ == "__main__":
    run(main)
