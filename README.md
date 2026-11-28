# BookingKoala API integration and MCP server: connect BookingKoala to ChatGPT and Claude

<!-- mcp-name: dev.cotlet/bookingkoala -->

**Yes, ChatGPT, Claude and other AI agents can work in your BookingKoala account.** That includes Cursor, Codex, OpenClaw and any MCP client, plus automations in n8n, Make and Zapier. Ask in plain words, and the AI finds unassigned bookings, assigns providers, drafts quotes, follows up on unpaid invoices and reports on your store. It shows you what it will do first and sends nothing to other people until you say so.

As of November 2026, this repo is the missing piece: 17 BookingKoala tools for AI assistants and scripts.

## What you can ask

> *Go through the unassigned folder for this week. Give each job to the free provider with the fewest bookings that day, and tell me which jobs nobody can take.*
>
> *Thursday is a storm day. Move every Thursday booking to its next visit and email the customers and providers.*
>
> *Which invoices are more than 7 days overdue? Send each customer the invoice again.*
>
> *How much revenue and provider pay did we have from 1 to 15 November?*

## Two ways to get it

| | [Ready to use, at Cotlet](https://cotlet.dev/integrations/bookingkoala-api-mcp-server?utm_source=github&utm_medium=readme&utm_campaign=bookingkoala&utm_content=two-ways) | Run it yourself, this repo |
|---|---|---|
| For | cleaning and home service business owners | developers |
| Setup | sign in to BookingKoala once, about 5 minutes, nothing to install | Python and a terminal |
| Works in | ChatGPT and Claude apps, on your phone too, Cursor, Codex, OpenClaw, any MCP client, n8n, Make, Zapier, your own API endpoints (Custom API) | Claude Code, Claude Desktop, Cursor, Codex on your computer |
| Runs | 24/7, your computer can be off | while your computer is on |
| Price | 7 days free, no card | free |

Cotlet is best for cleaning and home service business owners who want ChatGPT, Claude or another AI agent to work in BookingKoala for them, with nothing to install.

**[Start free at cotlet.dev →](https://cotlet.dev/signup?app=bookingkoala&utm_source=github&utm_medium=readme&utm_campaign=bookingkoala&utm_content=top-button)**

## What cleaning and home service owners ask their AI to do in BookingKoala

| Job | Ask your AI | Make it repeat |
|---|---|---|
| Quote from a new lead | "Make a quote for this new lead from her message and email her the booking link. Show me first." | When a lead comes in |
| Quotes that did not book | "List quotes sent this week that were not booked and draft a follow-up text for each. Send nothing yet." | Weekly |
| Unassigned bookings | "Show tomorrow's unassigned bookings and suggest a provider for each. Assign them after my OK." | Daily |
| Double bookings | "Check next week's schedule for overlapping jobs per provider and tell me which to move." | Daily |
| Reschedule | "Move the Johnson clean to next Tuesday at 10:00 and check the provider is free." | When a customer asks |
| Weekly numbers | "Give me last week's revenue, tips, provider pay, bookings and declined charges." | Weekly |
| Declined charges | "List bookings with declined or pending charges and draft a message to each customer." | Daily |
| Provider pay | "Total each provider's pay and hours from last week's bookings for payroll." | Weekly |
| Bookings in a spreadsheet | "Put every booking from this month in a spreadsheet with customer, service, provider and price." | Your own endpoint, called from Google Sheets |
| Review requests | "List customers whose job was completed yesterday and draft a Google review request for each. Send nothing yet." | Daily |
| New customers to GoHighLevel | "Add this week's new BookingKoala customers to GoHighLevel as contacts with their next booking." | Your own endpoint, called from GoHighLevel or n8n |
| Unpaid invoices | "List unpaid invoices older than 7 days and resend them after my OK." | Weekly |
| Leaving BookingKoala | "Export all my customers, bookings, quotes and invoices before I switch to another system." | Once |

Your AI asks you before it books, reschedules, sends a quote or an invoice, or changes anything. A refund waits for your OK on each call, and Cotlet never charges a card for you.

## Your own BookingKoala API, built with Cotlet (hosted)

BookingKoala gives you no public API, only Zapier and Make triggers. With Cotlet you build your own: your AI does the job once in your Cloud Browser, you save it as an endpoint, and you call it from Google Sheets, GoHighLevel, Zapier, Make, n8n, your own code.

Examples you can build in a few minutes (none of them exists until you build it):

| Endpoint you build | What it returns or does |
|---|---|
| `bookings-for-day` | bookings for a date with customer, service, provider, price and status |
| `unassigned-bookings` | bookings that have no provider yet |
| `open-quotes` | quotes sent but not booked, with customer and price |
| `new-customers` | customers added since a date, with email and phone |
| `declined-charges` | bookings with declined or pending charges |
| `provider-pay` | pay and hours per provider for a period |
| `weekly-summary` | revenue, tips, provider pay, bookings and ratings for a period |
| `unpaid-invoices` | invoices with amount due and days since sent |
| `assign-provider` | assigns a provider or team to a booking (writes only after you allow it) |

Call it with your Cotlet API key, JSON in and JSON out:

```bash
curl -X POST https://cotlet.dev/api/v1/custom/bookings-for-day \
  -H "Authorization: Bearer $COTLET_API_KEY" -H "Content-Type: application/json" -d '{}'
```

Limits: one call runs up to 90 seconds, writes wait for your consent, payments are blocked. Start here: https://cotlet.dev/app/custom-api/new?app=bookingkoala

## Find it on Cotlet.dev

- [BookingKoala MCP server on Cotlet.dev](https://cotlet.dev/integrations/bookingkoala-api-mcp-server?utm_source=github&utm_medium=readme&utm_campaign=bookingkoala&utm_content=old-repo)
- [Does BookingKoala have an API or MCP server?](https://cotlet.dev/api-mcp-status/bookingkoala?utm_source=github&utm_medium=readme&utm_campaign=bookingkoala&utm_content=old-repo)

## What you can ask your AI to do in BookingKoala

These are real jobs BookingKoala users asked about. Cotlet lets ChatGPT, Claude or any MCP client do them in your own signed-in BookingKoala account.

### Bookings and scheduling

#### How do I sync every BookingKoala booking to Google Calendar, including edits and cancellations, so my calendar stays in step?

Partly. BookingKoala has a Google Calendar sync setting, and owners report edits and cancellations drifting. With Cotlet, your agent compares upcoming BookingKoala bookings with your Google Calendar, signed in in the same Cloud Browser, and fixes the events that differ. Nothing changes until you say yes.

Ask your agent: "Compare next week's BookingKoala bookings with my Google Calendar and list events that are missing, moved or cancelled. Show me before fixing."

As an API endpoint: Yes. Save the comparison as an endpoint in Cotlet and call it every morning from n8n, Make or Zapier.

#### Can an AI agent check my BookingKoala schedule and stop double bookings or overlapping jobs?

Yes. With Cotlet, your agent reads each provider's bookings for the coming days in your signed-in BookingKoala, lists overlaps and proposes who could take each job. Reassigning a provider waits until you say yes.

Ask your agent: "Read next week's BookingKoala bookings per provider, list any overlapping jobs and suggest which free provider could take each one."

As an API endpoint: Yes. Save the overlap check as an endpoint in Cotlet and call it every evening from n8n, Make or Zapier.

#### Can AI mark a BookingKoala booking as paid or reschedule it for me?

Partly. BookingKoala's Zapier app gives triggers, not these actions. With Cotlet, your agent reschedules a booking or notes a payment in your signed-in account. Charging cards stays in BookingKoala and Cotlet does not pay. Nothing changes until you say yes.

Ask your agent: "Reschedule the BookingKoala booking for Dana Whitfield to Friday at 10:00 and show me the change before saving. Do not charge anything."

#### How do I get an owner app for BookingKoala so I can change bookings from my phone?

Partly. BookingKoala's mobile app is for providers and owners ask for an admin app on its idea board. With Cotlet, you ask ChatGPT or Claude on your phone to check or change bookings in your signed-in account. Nothing changes until you say yes.

Ask your agent: "Show me today's BookingKoala bookings with provider and address, and move the 2 pm job to tomorrow if I say yes."

### Leads and quotes

#### Can AI create a quote in BookingKoala from a new lead and email the customer a personalized booking link?

Yes. BookingKoala has a Send a quote screen. With Cotlet, your agent reads the new lead, builds the quote in your signed-in account and drafts the email with the booking link. Nothing is sent until you say yes.

Ask your agent: "Read my newest BookingKoala lead, build a quote for the service they asked about and draft the email with the booking link. Do not send it."

As an API endpoint: Yes. Save the quote step as an endpoint in Cotlet and call it from a form tool, n8n, Make or Zapier for each new lead.

#### Can AI follow up with people who abandoned the BookingKoala booking form by text or email?

Yes. BookingKoala's Leads module has an Abandoned Cart (hot leads) funnel. With Cotlet, your agent reads those leads in your signed-in account and drafts a short text or email for each. Nothing is sent until you say yes.

Ask your agent: "List today's abandoned BookingKoala booking leads and draft a short follow-up text for each with a link to finish the booking."

As an API endpoint: Yes. Save the leads check as an endpoint in Cotlet and call it every morning from n8n, Make or Zapier.

#### How do I connect BookingKoala to GoHighLevel so new leads, customers and booking status move both ways?

Partly. BookingKoala has no native GoHighLevel link. With Cotlet, your agent copies new leads and customers between BookingKoala and GoHighLevel, signed in in the same Cloud Browser, and updates booking status. Nothing changes until you say yes.

Ask your agent: "Compare new BookingKoala customers with GoHighLevel contacts and list the ones missing in GoHighLevel. Show me before adding them."

As an API endpoint: Yes. Save the sync as an endpoint in Cotlet and call it every hour from n8n, Make or Zapier.

#### How do I embed the BookingKoala booking form and customer login into my WordPress or Wix site without the booking summary breaking?

Not on its own. BookingKoala has help pages for embedding its forms. Cotlet works in the signed-in apps and does not edit your website's code. Your agent can read your embed settings in BookingKoala and your page in WordPress or Wix, and tell you what differs.

Ask your agent: "Read my BookingKoala embed settings and the Wix page that holds the form and list what could make the booking summary not float."

### Texts, reviews and reports

#### How do I make BookingKoala text customers from my own Twilio or GoHighLevel number, and what do I need to register first (A2P 10DLC)?

Not on its own. BookingKoala uses your own Twilio account for texts. Cotlet does not send SMS itself and does not register numbers for you. Your agent can read your Twilio and BookingKoala settings and tell you which steps are missing. Nothing changes until you say yes.

Ask your agent: "Read my BookingKoala SMS settings and my Twilio console and list what is missing for texts to send, including A2P registration status."

#### Can I connect BookingKoala to OpenPhone or another business phone so I can text customers two ways from one inbox?

Not on its own. BookingKoala's help centre shows no two-way text inbox. With Cotlet, your agent can copy a customer's booking details into your phone app, signed in in the same Cloud Browser, and draft the text. Nothing is sent until you say yes.

Ask your agent: "Find the BookingKoala customer Dana Whitfield, read her next booking and draft a reminder text I can send from OpenPhone."

#### Can AI ask for a Google review after each completed BookingKoala job and thank 5-star customers?

Yes. BookingKoala has automatic reviews that turn an internal rating into an external review link. With Cotlet, your agent lists completed jobs and ratings in your signed-in account and drafts thank-you messages for 5-star customers. Nothing is sent until you say yes.

Ask your agent: "List BookingKoala jobs completed this week with their rating and draft a short thank-you for every 5-star customer with my Google review link."

As an API endpoint: Yes. Turn the review check into an endpoint in Cotlet and call it at the end of each day from n8n, Make or Zapier.

#### Can AI send me a weekly summary of revenue, tips, provider hours and declined charges from BookingKoala?

Yes. BookingKoala has Reports and Booking Time Logs. With Cotlet, your agent reads revenue, tips, provider hours and declined charges for the week in your signed-in account and writes one short summary for you.

Ask your agent: "Summarise last week in BookingKoala: revenue, tips, provider hours and declined charges. Point out anything unusual."

As an API endpoint: Yes. Save the summary as an endpoint in Cotlet and call it every Monday from n8n, Make or Zapier to email it to you.

#### How do I use Zapier or Make to add every new BookingKoala booking as a row in Google Sheets for payroll and reporting?

Yes. BookingKoala has Zapier and Make apps and a Google Sheets sync. With Cotlet, your agent reads the day's bookings in your signed-in account and adds one row per booking to your sheet, signed in in the same Cloud Browser. Nothing is added until you say yes.

Ask your agent: "Read today's BookingKoala bookings and add a row per booking to my Google Sheet with customer, provider, date, service and price."

As an API endpoint: Yes. Save the day's booking read as an endpoint in Cotlet and call it every evening from n8n, Make or Zapier.

### Accounting and provider pay

#### How do I connect BookingKoala to QuickBooks Online so invoices and payments land in my books without retyping?

Partly. BookingKoala has a QuickBooks overview and an Invoices module. With Cotlet, your agent reads invoices and payments in BookingKoala, compares them with QuickBooks, signed in in the same Cloud Browser, and lists what is missing. Nothing changes until you say yes.

Ask your agent: "Compare this month's BookingKoala invoices and payments with QuickBooks Online and list the ones missing in QuickBooks. Show me before adding any."

As an API endpoint: Yes. Save the comparison as an endpoint in Cotlet and call it every week from n8n, Make or Zapier.

#### How do I automate weekly cleaner pay from BookingKoala time logs and send the payouts?

Partly. BookingKoala has Booking Time Logs and a Provider payments section. With Cotlet, your agent totals each provider's hours and pay for the week in your signed-in account and gives you a table. Cotlet does not send the payouts, you do that in BookingKoala.

Ask your agent: "Total each provider's hours and pay in BookingKoala for last week from the Booking Time Logs and give me a table for payroll."

As an API endpoint: Yes. Save the weekly totals as an endpoint in Cotlet and call it every Monday from n8n, Make or Zapier.

### Exports and switching

#### How do I export all my customers and bookings from BookingKoala to CSV before I switch to another system?

Yes. BookingKoala exports customers and providers to CSV and has a bigger bookings CSV since its August 2026 release. With Cotlet, your agent pulls customers, providers and bookings from your signed-in account into one spreadsheet.

Ask your agent: "Export all my BookingKoala customers, providers and bookings into one spreadsheet with a sheet for each."

As an API endpoint: Yes. Save the export as an endpoint in Cotlet and call it every month from n8n, Make or Zapier to keep a backup in Google Sheets.

#### How do I import my customer list from ZenMaid or Launch27 into BookingKoala?

Yes. BookingKoala has a customer import tool for CSV files. With Cotlet, your agent reads the customers in your signed-in ZenMaid or Launch27, shapes them into the import columns and runs the import in BookingKoala. Nothing changes until you say yes.

Ask your agent: "Read my customers from ZenMaid, build a BookingKoala import file and show me the first ten rows before importing."

#### How do I move off BookingKoala without losing my domain, my Google ranking or my customer data?

Partly. Cotlet cannot transfer a domain or move Google rankings. With Cotlet, your agent exports customers, providers and bookings from your signed-in BookingKoala and lists the pages and forms on your site that point to it.

Ask your agent: "Export my BookingKoala customers and bookings and list the pages on my website that embed BookingKoala forms or link to it."

## Run it yourself

A **BookingKoala API** and a **BookingKoala MCP server** you run on your own computer, in Python, on the session of your own Google Chrome. 17 of the 18 BookingKoala tools we run in production at [Cotlet](https://cotlet.dev/integrations/bookingkoala-api-mcp-server?utm_source=github&utm_medium=readme&utm_campaign=bookingkoala&utm_content=intro): bookings, drafts and quotes, customers, providers and teams, charges, invoices and the store dashboard.

BookingKoala has no public API and no official MCP server. Its API key only connects Zapier and Make, which react to new events and can write back one thing, a lead. This repo gives you both:

- **MCP server** for Claude Code, Claude Desktop, Cursor, Codex and any MCP client, over stdio or HTTP. [Setup](#mcp-server)
- **REST API** on `http://127.0.0.1:8787/api/v1/bookingkoala`, with OpenAPI docs at `/docs`. [Setup](#rest-api-local-this-repo)
- **Python**: `call("list_bookings", status="unassigned")`, plus 12 ready scripts in [`examples/`](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/examples/).

Free for your own use, your own business included ([license](#license)).

[![BookingKoala MCP server](https://img.shields.io/badge/BookingKoala%20MCP-17%20tools-6d4aef)](#all-17-tools)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-141318)](#requirements)
[![License: Elastic 2.0](https://img.shields.io/badge/license-Elastic%202.0-141318)](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/LICENSE)
[![MCP Badge](https://lobehub.com/badge/mcp/cotletdev-bookingkoala-api-mcp-server)](https://lobehub.com/mcp/cotletdev-bookingkoala-api-mcp-server)

Also on Odel: https://odel.app/modules/cotlet/bookingkoala and mcpbeat: https://mcpbeat.com/mcp-servers/cotlet/bookingkoala/

```bash
uv tool install bookingkoala-api-mcp                  # or: pip install bookingkoala-api-mcp
bookingkoala-mcp connect                           # reads your BookingKoala session from Chrome
bookingkoala-mcp call list_bookings status=upcoming
claude mcp add bookingkoala -- uvx bookingkoala-api-mcp mcp
```

## Contents

- [Questions from BookingKoala users](#questions-from-bookingkoala-users)
- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Install](#install)
- [Connect your Chrome](#connect-your-chrome)
- [MCP server](#mcp-server)
- [REST API](#rest-api-local-this-repo)
- [Python and the example scripts](#python-and-the-example-scripts)
- [All 17 tools](#all-17-tools)
- [Configuration](#configuration)
- [Security and your BookingKoala account](#security-and-your-bookingkoala-account)
- [Errors](#errors)
- [Self-hosted or hosted](#self-hosted-or-hosted)
- [FAQ](#faq)
- [License](#license)

## Questions from BookingKoala users

**Does BookingKoala have an API?**

Not a public one (checked 22 Nov 2026). The API key in Settings > General > Apps and Integrations only connects Zapier and Make, and "Open API" is the most-voted request on BookingKoala's idea board. With Cotlet you build your own endpoints that work in your signed-in BookingKoala account.

**Can Zapier reschedule a BookingKoala booking or assign a provider?**

BookingKoala's Zapier app gives triggers such as new bookings, quotes and charges, not those actions. With Cotlet your AI reschedules bookings, assigns providers and sends quotes after your OK, and you can call them as your own endpoints from Zapier or Make.

**Is there an official BookingKoala MCP server or ChatGPT app?**

No. BookingKoala has no MCP server and no ChatGPT or Claude app. Cotlet is unofficial and works in the ChatGPT and Claude apps and in any MCP client.

**How do I connect BookingKoala to GoHighLevel?**

Build a `new-customers` endpoint and call it from a GoHighLevel workflow, n8n or Make on a schedule. Add `bookings-for-day` to bring booking status back into GoHighLevel.

**How do I add every BookingKoala booking to Google Sheets?**

BookingKoala's Zapier and Make triggers add new bookings as they come. For past bookings, changes and provider pay, build a `bookings-for-day` or `provider-pay` endpoint and call it from Google Sheets.

**Can AI send me a weekly summary of revenue, tips and provider pay?**

Yes. Your AI reads the dashboard and charges in your account and sends you revenue, tips, provider pay, bookings and declined charges for the week.

**Can AI ask for a Google review after each completed job?**

It lists yesterday's completed jobs and drafts a review request for each customer. Nothing goes out until you say yes.

**Can an AI agent stop double bookings?**

It checks the schedule per provider for overlapping jobs and tells you which ones to move. It moves a booking only after your OK.

**How do I export all my customers and bookings before I switch?**

Your AI downloads your customers, bookings, quotes and invoices from the screens your login opens, so you keep everything when you move.

**Is there an owner app for BookingKoala on my phone?**

BookingKoala's mobile app is for providers. With Cotlet, the ChatGPT and Claude apps on your phone can check and change bookings for you.

**Can I get a BookingKoala API key?**
BookingKoala's own key only connects Zapier and Make. With Cotlet you get your own API key that works with your BookingKoala store, for scripts, n8n, Make, Zapier or any HTTP client. This repo needs no key: it runs on your computer, on your own BookingKoala session.

**How do I connect BookingKoala to ChatGPT?**
Sign up at [cotlet.dev](https://cotlet.dev/signup?app=bookingkoala&utm_source=github&utm_medium=readme&utm_campaign=bookingkoala&utm_content=faq-chatgpt), sign in to BookingKoala once in your Cloud Browser there, and add Cotlet to ChatGPT, following the steps in your account. Then ask ChatGPT about your BookingKoala like you would ask an assistant. ChatGPT needs a server on the internet, so this repo alone, running on your computer, does not connect to ChatGPT.

**Can ChatGPT manage my BookingKoala bookings?**
Yes, with Cotlet. It lists today's and unassigned bookings, assigns providers, reschedules, drafts quotes and checks what is unpaid. It shows you every change first.

**Can I automate BookingKoala with Zapier, Make or n8n?**
BookingKoala's own key only connects Zapier and Make for new-event triggers and one action, Create Lead. With Cotlet, n8n, Make and Zapier can also read past bookings, assign providers and work with quotes and invoices.

**Can I use it from my phone?**
Yes, with Cotlet: once it is set up, the ChatGPT and Claude apps on your phone can use BookingKoala for you.

**Do I need to be technical?**
For Cotlet, no: you sign in to BookingKoala and add Cotlet to ChatGPT or Claude, with step-by-step instructions in your account. This repo is for people who are fine with Python and a terminal.

**Is my BookingKoala account safe?**
Yes. Neither Cotlet nor this repo sees or stores your BookingKoala password. You sign in yourself, the way you always do, and the AI works on that signed-in session. Anything that reaches other people asks for your OK first: in Cotlet by default, here through your MCP client.

**Is it free?**
This repo is free, also in your own business. Cotlet is free for 7 days with no card, then one-time credit packs from $29, no subscription. [Pricing](https://cotlet.dev/pricing?utm_source=github&utm_medium=readme&utm_campaign=bookingkoala&utm_content=faq-price).

**I manage BookingKoala for several accounts or clients. Does that work?**
Yes, with Cotlet. Each BookingKoala login gets its own connection. Write to [contact@cotlet.dev](mailto:contact@cotlet.dev) and tell us how many accounts you manage.

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

## REST API (local, this repo)

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

| | This repo | [Cotlet, hosted](https://cotlet.dev/integrations/bookingkoala-api-mcp-server?utm_source=github&utm_medium=readme&utm_campaign=bookingkoala&utm_content=compare) |
|---|---|---|
| Tools | 17 | 18, with `refund_charge` |
| Runs | on your computer, while it is on | in the cloud, 24/7 |
| BookingKoala session | your Chrome, cookies in a local file | your own Cloud Browser in the EU, profile encrypted with AES-256-GCM |
| When BookingKoala changes its app | `git pull` once we have fixed it | fixed for you, every tool tested daily |
| Approvals | your MCP client asks per call | assignments, quotes, invoices and refunds wait for your OK, switchable per tool |
| Works with | MCP clients on your machine, local scripts | Claude.ai and ChatGPT connectors, n8n, Make, Zapier, any HTTP client through your own endpoints (Custom API) |
| Who may use it | you and your own business | you, teams, businesses, agencies |
| Price | free | free 7-day trial, no card; then one-time packs from $29 for 5,000 credits |

On the hosted version a successful call uses 10 credits for most tools, failed calls are free, and the Cloud Browser uses 50 credits a day while it has an app enabled for agents. [Full pricing](https://cotlet.dev/pricing).

## FAQ

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
For your own cleaning business, yes, free. You may not offer it to others as a hosted or managed service. For client work, use [Cotlet](https://cotlet.dev?utm_source=github&utm_medium=readme&utm_campaign=bookingkoala&utm_content=faq-clients) or write to [contact@cotlet.dev](mailto:contact@cotlet.dev).

**Is it open source?**
The source is public under the Elastic License 2.0: free to use and change, also in your own business, but not to resell as a hosted service.

**A tool broke or I need another one.**
[Open an issue](https://github.com/cotletdev/bookingkoala-api-mcp-server/issues) with the tool name and the error message.

## License

[Elastic License 2.0](https://github.com/cotletdev/bookingkoala-api-mcp-server/blob/main/LICENSE). In short:

- **Allowed:** using it for yourself and in your own business, free. Changing the code and sharing it under the same license.
- **Not allowed:** offering it to others as a hosted or managed service, removing the license notices, getting around its limits.

---

<p>
  <a href="https://cotlet.dev">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/logo-white.svg">
      <img src="https://raw.githubusercontent.com/cotletdev/bookingkoala-api-mcp-server/main/assets/logo.svg" alt="Cotlet" width="120">
    </picture>
  </a>
</p>

Maintained by [Cotlet](https://cotlet.dev?utm_source=github&utm_medium=readme&utm_campaign=bookingkoala&utm_content=footer) ([@cotletdev](https://x.com/cotletdev)). BookingKoala is a trademark of its owner. This project is unofficial and not affiliated with, endorsed or sponsored by BookingKoala.
