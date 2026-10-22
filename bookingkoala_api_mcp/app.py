"""Everything the server knows about BookingKoala outside `bookingkoala/`: names, domains and the session cookie.

The rest of the package reads these values and never names the app itself.
"""

from __future__ import annotations

NAME = "BookingKoala"
SLUG = "bookingkoala"
# The command and the prefix of every environment variable (BOOKINGKOALA_AUTH_TOKEN, BOOKINGKOALA_MCP_TOKEN ...).
CLI = "bookingkoala-mcp"
ENV = "BOOKINGKOALA"
# Requests may reach only these hosts and their subdomains (every store is <store>.bookingkoala.com).
# Their cookies are read from Chrome.
DOMAINS = ("bookingkoala.com",)
# Present only while signed in. The first is the cookie a pasted token sets. The app writes it on the store's
# own host at sign-in and deletes it at sign-out.
SESSION_COOKIES = ("IRON_GATEWAY_CTX",)
# The host a pasted token's cookie belongs to. {store} is the store name, asked for with the token.
COOKIE_DOMAIN = "{store}.bookingkoala.com"
# localStorage keys of the app's pages that also hold the session, read at connect from open tabs of the app.
LOCAL_STORAGE_KEYS = ("currentUser",)
LOGIN_URL = "https://www.bookingkoala.com/login"
# A final URL with one of these means the app signed the session out.
LOGGED_OUT_MARKERS = ("/login",)
# Paths the tools may only read: sign-in, sign-out, impersonation, password, the merchant's own billing.
ACCOUNT_PATHS = (
    r"^/api/v\d+/auth/",
    r"^/api/v\d+/sessions/",
    r"^/api/v\d+/merchant/",
    r"^/api/v\d+/merchant-(setup-intent|coupon)",
    r"^/api/v\d+/users/\d+/password",
    r"^/bkaffiliates/v\d+/promoters/login-token",
)
# A 401 or 403 whose body has one of these asks for a fresh sign-in before the action. BookingKoala has none.
RELOGIN_MARKERS: tuple[str, ...] = ()
# REST routes live under this path, the same as on cotlet.dev.
API_PREFIX = "/api/v1/bookingkoala"
# Prepended to the MCP server's instructions: where an agent starts.
AGENT_START = (
    "Start with dashboard or list_bookings: their booking, customer and provider ids are what the other tools take."
)
