# BookingKoala API and MCP server, self-hosted

<!-- mcp-name: dev.cotlet/bookingkoala -->

A **BookingKoala API** and a **BookingKoala MCP server** you run on your own computer, in Python, on the session of your own Google Chrome. 17 of the 18 BookingKoala tools we run in production at [Cotlet](https://cotlet.dev/integrations/bookingkoala-api-mcp-server): bookings, drafts and quotes, customers, providers and teams, charges, invoices and the store dashboard.

BookingKoala has no public API and no official MCP server. Its API key only connects Zapier and Make, which react to new events and can write back one thing, a lead. This repo gives you both:

- **MCP server** for Claude Code, Claude Desktop, Cursor, Codex and any MCP client, over stdio or HTTP. [Setup](#mcp-server)
- **REST API** on `http://127.0.0.1:8787/api/v1/bookingkoala`, with OpenAPI docs at `/docs`. [Setup](#rest-api)
- **Python**: `call("list_bookings", status="unassigned")`, plus 12 ready scripts in [`examples/`](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/examples/).

It is for technical people who want to run it themselves, **for noncommercial use only** ([license](#license)). If you want it running 24/7 on a server, kept working when BookingKoala changes its app, for a team or a business, use the [hosted version at cotlet.dev](https://cotlet.dev/integrations/bookingkoala-api-mcp-server).

[![BookingKoala MCP server](https://img.shields.io/badge/BookingKoala%20MCP-17%20tools-6d4aef)](#all-17-tools)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-141318)](#requirements)
[![License: PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/license-PolyForm%20Noncommercial-141318)](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/LICENSE)
[![MCP Badge](https://lobehub.com/badge/mcp/cotletdev-bookingkoala-api-mcp-server)](https://lobehub.com/mcp/cotletdev-bookingkoala-api-mcp-server)

```bash
uv tool install bookingkoala-api-mcp                  # or: pip install bookingkoala-api-mcp
bookingkoala-mcp connect                           # reads your BookingKoala session from Chrome
bookingkoala-mcp call list_bookings status=upcoming
claude mcp add bookingkoala -- uvx bookingkoala-api-mcp mcp
```

## Contents

- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Install](#install)
- [Connect your Chrome](#connect-your-chrome)
- [MCP server](#mcp-server)
- [REST API](#rest-api)
- [Python and the example scripts](#python-and-the-example-scripts)
- [All 17 tools](#all-17-tools)
- [Configuration](#configuration)
- [Security and your BookingKoala account](#security-and-your-bookingkoala-account)
- [Errors](#errors)
- [Self-hosted or hosted](#self-hosted-or-hosted)
- [FAQ](#faq)
- [License](#license)

## How it works

```text
AI agent (MCP) / script (REST, Python) ──▶ bookingkoala-mcp on your computer ──your session──▶ yourstore.bookingkoala.com
                                                  ▲
                    bookingkoala-mcp connect ─────┘ reads it once from your Chrome (DevTools Protocol)
```

1. You sign in to your BookingKoala store admin in your own Chrome, the way you always do.
2. `bookingkoala-mcp connect` attaches to that Chrome through the Chrome DevTools Protocol, reads the bookingkoala.com cookies and your time zone, and saves them to `~/.config/bookingkoala-api-mcp/session.json`, readable by your user only. It never sees or stores your password.
3. Every tool call is a request to the admin API your store's own web app calls, on `yourstore.bookingkoala.com`, sent with [curl_cffi](https://github.com/lexiforest/curl_cffi), which copies Chrome's TLS fingerprint. The server signs each request the way the app does: a bearer token from your session and a new per-request header. No headless browser runs.

BookingKoala keeps the session for 30 days in the `IRON_GATEWAY_CTX` cookie of your store's host. When it signs you out, the server reads the session from Chrome again, if Chrome is open with remote debugging on.

## Requirements

- Python 3.11 or newer.
- Google Chrome 144 or newer, signed in to your BookingKoala store admin. Any Chrome or Chromium works with a [debugging port](#option-b-a-chrome-with-a-debugging-port).
- macOS, Linux or Windows.
- A store admin account. The tools can do what your BookingKoala role may do in the admin panel. A staff role with fewer permissions gets a refusal where the panel would show one.

## Install

From [PyPI](https://pypi.org/project/bookingkoala-api-mcp/):

```bash
uv tool install bookingkoala-api-mcp       # or: pipx install bookingkoala-api-mcp, or: pip install bookingkoala-api-mcp
bookingkoala-mcp --version
```

MCP clients can also run it with no install: `uvx bookingkoala-api-mcp mcp`.

From source:

```bash
git clone https://github.com/cotletdev/bookingkoala-api-mcp-server.git
cd bookingkoala-api-mcp-server
python3 -m venv .venv
. .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -e .
bookingkoala-mcp --version
```

With [uv](https://docs.astral.sh/uv/): `uv venv && uv pip install -e .`, then `uv run bookingkoala-mcp ...`.

Setting it up with an AI agent (Claude Code, Codex, Cursor)? Open it in this folder and ask it to set up the repo: [`AGENTS.md`](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/AGENTS.md) tells it every step, and it asks you only for the steps in Chrome.

To update: `uv tool upgrade bookingkoala-api-mcp` (or `pip install -U bookingkoala-api-mcp`), from source `git pull && pip install -e .`. We copy every change of the hosted BookingKoala tools into this repo.

## Connect your Chrome

### Option A: your everyday Chrome (recommended)

1. Open `chrome://inspect/#remote-debugging` in Chrome and switch **remote debugging** on. Chrome then accepts DevTools connections from programs on this computer, and asks you before each one.
2. Make sure you are signed in to your store admin at `https://yourstore.bookingkoala.com/admin`.
3. Run:

   ```bash
   bookingkoala-mcp connect
   ```

4. Chrome asks whether to allow the connection. Click **Allow**.

```text
Saved 15 BookingKoala cookies to /Users/you/.config/bookingkoala-api-mcp/session.json
Signed in to BookingKoala as Dana Whitfield (dana@sparkleclean.com), sparkleclean
```

You can switch remote debugging off again afterwards. Leave it on if you want the server to pick up a new session by itself after BookingKoala signs you out.

`connect` looks for Chrome's `DevToolsActivePort` file in the default profile folder. For Chrome Beta, Canary or a custom profile folder, pass `--profile-dir "<folder>"`.

### Option B: a Chrome with a debugging port

Chrome does not open a debugging port on your default profile, so start a separate one, sign in to BookingKoala there once, and connect to it:

```bash
# macOS
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-bookingkoala"
# Linux
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-bookingkoala"
# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%USERPROFILE%\.chrome-bookingkoala"

bookingkoala-mcp connect --cdp http://127.0.0.1:9222
```

`--cdp` also takes a `ws://` DevTools URL, for example of a Chrome on another machine reached over an SSH tunnel.

### Option C: paste the cookie by hand

For a server with no Chrome: in Chrome open DevTools on your store admin, **Application > Cookies > https://yourstore.bookingkoala.com**, copy the value of `IRON_GATEWAY_CTX`, then:

```bash
bookingkoala-mcp connect --token          # asks for your store name, then the value (hidden)
# or, without a session file:
export BOOKINGKOALA_STORE=yourstore BOOKINGKOALA_AUTH_TOKEN=...
```

A pasted cookie is not refreshed on its own. Paste a new one when BookingKoala signs you out, at the latest after 30 days. Tools that say "today" then use this computer's time zone.

Check the session at any time:

```bash
bookingkoala-mcp status
```

## MCP server

The MCP server lists every tool with its input schema, a description written for agents, and hints. Read tools are marked read-only. Tools that email customers, notify providers or cancel are marked so your client asks before running them.

### Claude Code

```bash
claude mcp add bookingkoala -- uvx bookingkoala-api-mcp mcp
# read only:
claude mcp add bookingkoala -- uvx bookingkoala-api-mcp mcp --read-only
```

### Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "bookingkoala": {
      "command": "uvx",
      "args": ["bookingkoala-api-mcp", "mcp"]
    }
  }
}
```

### Cursor

`~/.cursor/mcp.json`, the same block as Claude Desktop. A ready copy is in [`mcp.json`](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/mcp.json).

### Codex

`~/.codex/config.toml`:

```toml
[mcp_servers.bookingkoala]
command = "uvx"
args = ["bookingkoala-api-mcp", "mcp"]
```

### Over HTTP

`bookingkoala-mcp serve` also serves MCP over streamable HTTP at `http://127.0.0.1:8787/mcp`, for clients that take a URL:

```bash
bookingkoala-mcp serve
claude mcp add --transport http bookingkoala http://127.0.0.1:8787/mcp
```

Then ask your agent things like:

> *Go through the unassigned folder for this week. Give each job to the free provider with the fewest bookings that day, and tell me which jobs nobody can take.*
>
> *Thursday is a storm day. Move every Thursday booking to its next visit and email the customers and providers.*
>
> *Which invoices are more than 7 days overdue? Send each customer the invoice again.*
>
> *How much revenue and provider pay did we have from 1 to 15 November?*

## REST API

```bash
bookingkoala-mcp serve             # http://127.0.0.1:8787, MCP at /mcp, docs at /docs
```

Each tool has its own route under `/api/v1/bookingkoala`, the same paths as the hosted API at cotlet.dev, so code written against one works with the other. Path parts and the query string are arguments, and a JSON body adds the rest.

```bash
curl 'http://127.0.0.1:8787/api/v1/bookingkoala/bookings?status=unassigned&start_date=2026-11-16&end_date=2026-11-20'
curl 'http://127.0.0.1:8787/api/v1/bookingkoala/bookings/212'
curl -X POST http://127.0.0.1:8787/api/v1/bookingkoala/bookings/212/assign \
  -H 'Content-Type: application/json' \
  -d '{"provider_id": 3}'
```

Any tool by name, body as its arguments:

```bash
curl -X POST http://127.0.0.1:8787/api/v1/bookingkoala/tools/list_customers -d '{"search": "whitfield"}'
```

- `GET /api/v1/bookingkoala/tools`: every tool with its route, input schema and an example answer.
- `GET /docs`: interactive OpenAPI docs, `GET /openapi.json` the schema, for n8n, Postman or a generated client.
- Answers are JSON. Lists return `next_cursor`; pass it back as `cursor` for the next page.

The server listens on `127.0.0.1` only. To reach it from another device of yours, set a token, and every request then needs `Authorization: Bearer <token>`:

```bash
BOOKINGKOALA_MCP_TOKEN=$(openssl rand -hex 24) bookingkoala-mcp serve --host 0.0.0.0
```

## Python and the example scripts

Straight from Python, no server needed:

```python
from bookingkoala_api_mcp import call
from bookingkoala_api_mcp.scripting import paginate, write_rows

totals = call("dashboard", start_date="2026-11-01", end_date="2026-11-15")
bookings = list(paginate("list_bookings", {"status": "completed", "start_date": "2026-11-01"}, "bookings"))
write_rows(bookings, "completed.csv")
call("assign_provider", booking_id=212, provider_id=3)
```

Or one tool from the shell: `bookingkoala-mcp call list_customers search=whitfield`, or with a JSON object.

Ready scripts in [`examples/`](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/examples/). Each prints JSON, takes `--out file.csv` or `--out file.json` where it makes sense, and `--help`:

| Script | What it does |
|---|---|
| [`list_bookings.py`](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/examples/list_bookings.py) | Bookings by status and date range: date, arrival time, customer, address, providers, total. |
| [`export_customers.py`](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/examples/export_customers.py) | Customers to CSV or JSON: name, email, phone, tags, note. |
| [`store_dashboard.py`](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/examples/store_dashboard.py) | Store totals for a date range: revenue, provider pay, bookings, ratings, referrals. |
| [`assign_unassigned.py`](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/examples/assign_unassigned.py) | Gives each unassigned job to the provider with the fewest jobs that day. Shows the plan unless you pass `--assign`. |
| [`assign_provider.py`](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/examples/assign_provider.py) | Assigns one booking, or its whole recurring schedule, to a provider or team. |
| [`reschedule_day.py`](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/examples/reschedule_day.py) | Moves a closed day's recurring visits to their next visit date. Plan first, `--move` to do it. |
| [`cancel_booking.py`](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/examples/cancel_booking.py) | Cancels one booking or the rest of its schedule, with no fee, after you confirm. |
| [`rebook_customer.py`](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/examples/rebook_customer.py) | Copies a repeat customer's last visit into a draft. `--send-quote` emails their saved quote. |
| [`send_quote.py`](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/examples/send_quote.py) | Lists saved drafts and quotes, or emails one quote with a link to book it. |
| [`add_customer.py`](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/examples/add_customer.py) | Adds a customer after checking the email is not in the store yet. |
| [`provider_pay_report.py`](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/examples/provider_pay_report.py) | Provider pay totals for a pay period, then each provider's payment logs. |
| [`overdue_invoices.py`](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/examples/overdue_invoices.py) | Unpaid invoices past due. `--remind` sends each one to its customer again. |

```bash
python examples/assign_unassigned.py --from 2026-11-16 --to 2026-11-20
python examples/overdue_invoices.py --days 7 --out overdue.csv
```

On a schedule, cron on your own computer works while it is on: `0 7 * * 1-5 cd ~/bookingkoala-api-mcp-server && .venv/bin/python examples/list_bookings.py --status today`.

## All 17 tools

Ids come from the list tools: `booking_id` from `list_bookings`, `customer_id` from `list_customers`, `provider_id` from `list_providers`, `draft_id` from `list_drafts`, `invoice_id` from `list_invoices`. `bookingkoala-mcp tools` prints this list, `bookingkoala-mcp tools --json` adds the input schemas.

### Bookings

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_bookings` | read | `GET /bookings` | Bookings of the store: upcoming, unassigned, completed, charge pending or declined. |
| `get_booking` | read | `GET /bookings/{booking_id}` | One booking with its price breakdown, provider pay, notes and service. |
| `create_booking` | write | `POST /bookings` | Start a new booking as a copy of an existing one: same customer, service and price. |
| `assign_provider` | write | `POST /bookings/{booking_id}/assign` | Assign a provider or team to a booking, or to its whole recurring schedule. |
| `reschedule_booking` | write | `POST /bookings/{booking_id}/reschedule` | Postpone a visit of a recurring booking to the date of a later visit in its schedule. |
| `cancel_booking` | write | `POST /bookings/{booking_id}/cancel` | Cancel one booking or its whole recurring schedule, without a cancellation fee. |

### Drafts and quotes

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_drafts` | read | `GET /drafts` | Draft bookings and quotes saved in the store, not yet booked. |
| `send_quote` | write | `POST /quotes/{draft_id}/send` | Email a saved quote to the customer with a link to book it. |

### Customers

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_customers` | read | `GET /customers` | Customers of the store, with email and phone; search by name, email or phone. |
| `get_customer` | read | `GET /customers/{customer_id}` | One customer: contact details, addresses, booking counts and bookings not charged yet. |
| `create_customer` | write | `POST /customers` | New customer in the store. BookingKoala emails them an invitation to set a password. |

### Providers and teams

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_providers` | read | `GET /providers` | Providers (cleaners, technicians) and teams of the store, in priority order. |
| `get_provider` | read | `GET /providers/{provider_id}` | One provider or team: contact, category, team members, reviews and payment logs. |

### Charges, invoices and reports

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_charges` | read | `GET /charges` | Charged bookings with their payments and refunds, as the Charges page lists them. |
| `list_invoices` | read | `GET /invoices` | Invoices of the store or of one customer, with payment status, total and amount due. |
| `resend_invoice` | write | `POST /invoices/{invoice_id}/resend` | Send an invoice to its customer again by email, text or both. |
| `dashboard` | read | `GET /dashboard` | Store totals for a date range: revenue, provider pay, bookings, ratings, referrals. |

Never built, on purpose: your BookingKoala sign-in, password and profile, your own BookingKoala plan and billing, and anything else that moves money. Every request passes a guard that refuses those BookingKoala paths.

### Not in this version

| Tool | Why |
|---|---|
| `refund_charge` | It sends money back to a customer's card. The hosted version has it, with your approval for each call. Here, refund in the panel under Charges. |

## Configuration

| Variable | Default | What it does |
|---|---|---|
| `BOOKINGKOALA_MCP_HOME` | `~/.config/bookingkoala-api-mcp` | Folder of `session.json`. |
| `BOOKINGKOALA_AUTH_TOKEN` | | Value of the `IRON_GATEWAY_CTX` cookie, instead of `bookingkoala-mcp connect`. Needs `BOOKINGKOALA_STORE`. |
| `BOOKINGKOALA_STORE` | | Your store name, `yourstore` for `yourstore.bookingkoala.com`. |
| `BOOKINGKOALA_PROXY` | | Proxy for every request to BookingKoala, e.g. `http://user:pass@host:port`. |
| `BOOKINGKOALA_MCP_READ_ONLY` | | `1` hides and refuses every tool that changes BookingKoala (same as `--read-only`). |
| `BOOKINGKOALA_MCP_TOKEN` | | Bearer token required by `serve`; needed to listen beyond `127.0.0.1`. |
| `BOOKINGKOALA_MCP_HOST`, `BOOKINGKOALA_MCP_PORT` | `127.0.0.1`, `8787` | Address of `serve`. |

## Security and your BookingKoala account

- **Your password never reaches this code.** Only cookies are read, and only those of bookingkoala.com.
- **The session file is yours.** `session.json` is created with mode 0600. Anyone who has it can act as you in your store admin, so keep it out of git and shared folders.
- **Local by default.** `serve` binds to `127.0.0.1` and refuses another address without `BOOKINGKOALA_MCP_TOKEN`.
- **bookingkoala.com only.** Requests and redirects outside bookingkoala.com are refused.
- **Read-only mode.** `--read-only` or `BOOKINGKOALA_MCP_READ_ONLY=1` exposes the 10 read tools only.
- **Actions reach real people.** Assigning tells the provider. Quotes and invoices go to customers, a new customer gets an invitation email, and `notify` on a cancel or reschedule emails both sides. MCP clients ask before running them. A script does not, so try it on a test booking first.
- **You answer for what runs in your store.** Keep to your normal use of BookingKoala.

## Errors

The REST API answers `{"error": "<code>", "message": "..."}`. The MCP server returns the same code and message as a tool error.

| Status | Code | What to do |
|---|---|---|
| 401 | `auth_required`, `auth_expired` | No session, or BookingKoala signed you out. Sign in to your store admin in Chrome and run `bookingkoala-mcp connect`. |
| 403 | `app_permission_denied` | Your BookingKoala role cannot do this. |
| 403 | `scope_denied` | The server runs read-only, or the request would touch your sign-in or billing. |
| 403 | `target_blocked` | BookingKoala refused the request or showed a bot check. Open your store admin in Chrome once, then retry. |
| 409 | `captcha_required` | BookingKoala asks for a CAPTCHA. Solve it in Chrome. |
| 422 | `invalid_input` | An argument is missing or wrong; the message names it. |
| 429 | `rate_limited` | BookingKoala is limiting the account. Wait a few minutes. |
| 502 | `target_error` | BookingKoala answered with an error, or changed its app. The message carries BookingKoala's own reason. `git pull` for the latest tools, or [open an issue](https://github.com/cotletdev/bookingkoala-api-mcp-server/issues). |

## Self-hosted or hosted

| | This repo | [Cotlet, hosted](https://cotlet.dev/integrations/bookingkoala-api-mcp-server) |
|---|---|---|
| Tools | 17 | 18, with `refund_charge` |
| Runs | on your computer, while it is on | in the cloud, 24/7 |
| BookingKoala session | your Chrome, cookies in a local file | your own Cloud Browser in the EU, profile encrypted with AES-256-GCM |
| When BookingKoala changes its app | `git pull` once we have fixed it | fixed for you, every tool tested daily |
| Approvals | your MCP client asks per call | assignments, quotes, invoices and refunds wait for your OK, switchable per tool |
| Works with | MCP clients on your machine, local scripts | Claude.ai and ChatGPT connectors, n8n, Make, Zapier, any HTTP client |
| Who may use it | you, for noncommercial use | teams, businesses, agencies |
| Price | free | free 7-day trial with 2,000 credits, no card; then one-time packs from $29 for 5,000 credits |

On the hosted version a successful call uses 20 to 30 credits (25 for most tools), failed calls are free, and the Cloud Browser uses 50 credits a day while it has an app enabled for agents. [Full pricing](https://cotlet.dev/pricing).

## FAQ

**Does BookingKoala have an official API?**
Not a public one. BookingKoala publishes no REST API docs. The API key under Settings > General > Apps & Integrations only connects Zapier and Make: triggers for new or updated bookings, customers, providers, quotes, ratings and invoices, and one action, Create Lead. It cannot look up past bookings, assign a provider, reschedule, cancel or resend an invoice. Details: [cotlet.dev/integrations/bookingkoala-api-mcp-server](https://cotlet.dev/integrations/bookingkoala-api-mcp-server).

**Is there a BookingKoala MCP server for Claude, ChatGPT or Cursor?**
Yes, this one runs on your machine: `bookingkoala-mcp mcp` for Claude Code, Claude Desktop, Cursor and Codex. ChatGPT and Claude.ai connectors need a public HTTPS URL, which the [hosted BookingKoala MCP server](https://cotlet.dev/integrations/bookingkoala-api-mcp-server) gives you.

**Do I need Zapier or a BookingKoala API key?**
No. The tools use your signed-in admin session, the same one your browser uses.

**Can I export BookingKoala bookings or customers to CSV?**
Yes: `python examples/list_bookings.py --status all --out bookings.csv` and `python examples/export_customers.py --out customers.csv`, across all pages.

**Can it assign providers automatically?**
`examples/assign_unassigned.py` gives each unassigned job to the provider with the fewest jobs that day, after it shows you the plan. BookingKoala still refuses a provider who is not available at that time, and the script lists those jobs.

**Why does it need my Chrome?**
To read your BookingKoala session without your password. Chrome is used once per sign-in, not for each call.

**What happens when BookingKoala signs me out?**
Calls fail with `auth_expired`. With Chrome remote debugging on, the server reads the new session on the next call (click Allow when Chrome asks). Otherwise run `bookingkoala-mcp connect` again.

**Can it run on a VPS or in Docker?**
Technically yes, with `BOOKINGKOALA_STORE` and `BOOKINGKOALA_AUTH_TOKEN`. BookingKoala then sees your session from a datacenter IP. For an always-on setup the hosted version keeps your session in your own Cloud Browser on a fixed IP.

**Can I use it for my cleaning business?**
No. The license allows noncommercial use only, and running your store is business use. For your company, use [Cotlet](https://cotlet.dev) or write to [contact@cotlet.dev](mailto:contact@cotlet.dev).

**Is it open source?**
The source is public, the license is not an open source license: noncommercial use only, no business use.

**A tool broke or I need another one.**
[Open an issue](https://github.com/cotletdev/bookingkoala-api-mcp-server/issues) with the tool name and the error message.

## License

[PolyForm Noncommercial License 1.0.0](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/LICENSE). In short:

- **Allowed:** noncommercial use: you, for your own personal purposes with your own BookingKoala account, or a charity, school, public research or government body. Changing the code, and sharing it under the same license.
- **Not allowed:** any commercial use, your own business included; client work; selling or offering it, or a service built on it.

---

<p>
  <a href="https://cotlet.dev">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/logo-white.svg">
      <img src="https://raw.githubusercontent.com/cotletdev/bookingkoala-api-mcp-server/main/assets/logo.svg" alt="Cotlet" width="120">
    </picture>
  </a>
</p>

Maintained by [Cotlet](https://cotlet.dev) ([@cotletdev](https://x.com/cotletdev)). BookingKoala is a trademark of its owner. This project is unofficial and not affiliated with, endorsed or sponsored by BookingKoala.
