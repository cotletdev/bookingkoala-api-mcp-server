# AGENTS.md

You are an AI agent in a clone of this repo. It is a self-hosted BookingKoala API and MCP server: 17 tools that work in the user's own BookingKoala store admin, through the session of their own Google Chrome. Your usual job is one of three: set it up for the user, use its tools for them, or change its code. Human docs: `README.md`.

## Before you start

- The license allows personal use by one person only (`LICENSE`). Running a BookingKoala store for a business is business use. If the user is setting this up for a company, a team or clients, say so and point to the hosted version at https://cotlet.dev/integrations/bookingkoala-api-mcp-server. Do not continue the setup for that use.
- Every tool acts as the user in their store. Tools with access `write` assign providers (BookingKoala tells the provider), email quotes and invoices to customers, add customers (BookingKoala emails them an invitation), and cancel or move bookings. Real people see the result.

## Set it up for the user

Do the steps yourself. Ask the user only for what needs their hands in Chrome.

1. Check Python: `python3 --version` must be 3.11 or newer.
2. Install in the repo root:

   ```bash
   python3 -m venv .venv && .venv/bin/pip install -e .
   .venv/bin/bookingkoala-mcp --version
   ```

   On Windows the path is `.venv\Scripts\bookingkoala-mcp`. With uv: `uv venv && uv pip install -e .`.
3. Ask the user to do two things in Chrome. You cannot open `chrome://` pages for them.
   - Open `chrome://inspect/#remote-debugging` and switch remote debugging on.
   - Be signed in to their store admin at `https://<their store>.bookingkoala.com/admin`.
4. Run `.venv/bin/bookingkoala-mcp connect`. Tell the user to click **Allow** when Chrome asks about the connection. Success prints `Signed in to BookingKoala as <name> (<email>), <store>`.
5. Check: `.venv/bin/bookingkoala-mcp status`, then `.venv/bin/bookingkoala-mcp call dashboard`.
6. Add the MCP server to the user's client. Use the absolute path of `.venv/bin/bookingkoala-mcp`:
   - Claude Code: `claude mcp add bookingkoala -- <abs path>/.venv/bin/bookingkoala-mcp mcp`
   - Claude Desktop, Cursor, Codex: the config blocks in `README.md`, section "MCP server".
   - Add `--read-only` after `mcp` if the user only wants to read.
   The client loads new MCP servers on its next start. Tell the user.

If step 4 fails:

| Message | What to do |
|---|---|
| `Chrome remote debugging is off` | Step 3 is not done, or Chrome is Beta, Canary or a custom profile: pass `--profile-dir "<profile folder>"`. |
| `Could not connect to Chrome` | The user did not click Allow, or Chrome is closed. Run `connect` again. |
| `This Chrome is not signed in to BookingKoala` | The user signs in to the store admin in that Chrome, then run `connect` again. |
| No Chrome on this machine (a server) | The user copies the `IRON_GATEWAY_CTX` cookie from Chrome DevTools (Application, Cookies, `https://<store>.bookingkoala.com`) and runs `bookingkoala-mcp connect --token` themselves. It asks for the store name, then the value. Never ask them to paste the value into the chat. |

## Use the tools

- With the MCP server added, call its tools. Without it: `.venv/bin/bookingkoala-mcp call <tool> key=value ...`, or one JSON object as the argument.
- `.venv/bin/bookingkoala-mcp tools` lists every tool with access and route. `tools --json` adds the input schemas.
- Start with `dashboard` or `list_bookings`. Ids come from the list tools: `booking_id` from `list_bookings`, `customer_id` from `list_customers`, `provider_id` from `list_providers`, `draft_id` from `list_drafts`, `invoice_id` from `list_invoices`.
- Lists return `next_cursor`. Pass it back as `cursor` for the next page. Keep `limit` at 20 or less: a larger page can come back empty. A page can repeat the last item of the page before it, so drop repeats by id. `scripting.paginate` does both.
- Before a `write` tool, show the user what you will send and to whom, and get their OK. `notify` on `cancel_booking` and `reschedule_booking` emails the customer and providers: set it only when the user asks.
- For a script or a cron job, use `bookingkoala_api_mcp.scripting` (`call`, `paginate`, `write_rows`) and the scripts in `examples/` as models.
- For a REST API (n8n, other languages): `.venv/bin/bookingkoala-mcp serve`, routes under `http://127.0.0.1:8787/api/v1/bookingkoala`, docs at `/docs`.

Errors come as `<code>: <message>`. `auth_expired` means BookingKoala signed the session out: the user signs in again in Chrome and you run `connect`. `target_error` carries BookingKoala's own reason, such as a provider who is not available at that time. More codes: `README.md`, section "Errors".

## Keep secrets out

- `~/.config/bookingkoala-api-mcp/session.json` and `BOOKINGKOALA_AUTH_TOKEN` give full access to the user's store admin. Never print, log, commit or copy their content.
- `serve` listens on 127.0.0.1. Never start it on another address without `BOOKINGKOALA_MCP_TOKEN`.

## Change the code

| Path | What | Edit? |
|---|---|---|
| `bookingkoala_api_mcp/bookingkoala/` | the BookingKoala tools, one file per tool in `tools/`, request signing (bearer token, csrf, per-request header) in `client.py` | Yes for a local fix, but the next `git pull` brings our version of these files. Report the bug at https://github.com/cotletdev/bookingkoala-api-mcp-server/issues |
| `bookingkoala_api_mcp/app.py` | app name, domains, session cookie, account paths, REST prefix | Rarely |
| `bookingkoala_api_mcp/core/` | `@tool` declaration, errors, the HTTP client with the session (`context.py`), the account guard, the profile tools read | Yes |
| `bookingkoala_api_mcp/session.py` | reading cookies and the time zone from Chrome over CDP, the session file | Yes |
| `bookingkoala_api_mcp/runner.py`, `api.py`, `mcp_server.py`, `cli.py` | tool registry, REST API, MCP server, command line | Yes |
| `examples/` | scripts for common jobs | Yes |

A new tool is a new file in `bookingkoala_api_mcp/bookingkoala/tools/` with a `@tool(...)` declaration (name, access, input schema, `route`). The registry finds it, and the REST API, the MCP server and the CLI show it without other changes. Never add a tool that refunds, charges or changes the user's own BookingKoala plan.

There is no test suite. After a change, run `.venv/bin/bookingkoala-mcp tools` and one read tool against the user's store.
