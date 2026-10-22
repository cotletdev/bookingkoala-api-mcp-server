#!/usr/bin/env python3
"""Email a saved BookingKoala quote to the customer with a link to book it.

python send_quote.py --list                      # saved drafts and quotes
python send_quote.py --quote 41
python send_quote.py --quote 41 --expires 2026-12-01 --subject "Your spring clean"
"""

import argparse
import json

from bookingkoala_api_mcp.scripting import call, paginate, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--list", action="store_true", help="Show saved drafts and quotes")
    parser.add_argument("--quote", type=int, help="draft_id of a quote")
    parser.add_argument("--email", help="Send to this address instead of the quote's customer")
    parser.add_argument("--expires", help="Last day to book it, YYYY-MM-DD")
    parser.add_argument("--subject", help="Email subject")
    args = parser.parse_args()

    if args.list or not args.quote:
        write_rows(list(paginate("list_drafts", {}, "drafts")), None)
        return
    params = {"draft_id": args.quote, "email": args.email, "expires_on": args.expires, "subject": args.subject}
    print(json.dumps(call("send_quote", params), indent=2))


if __name__ == "__main__":
    run(main)
