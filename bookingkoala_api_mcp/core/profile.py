"""What tools read about the browser the session came from: its cookies, localStorage and time zone.

The hosted service keeps a whole browser profile; here it is built from the saved session (`session.py`).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Cookie:
    name: str
    value: str
    domain: str
    path: str = "/"


@dataclass(frozen=True)
class BrowserProfile:
    # A new id for every HTTP client (ToolContext): tools key per-client state on it, such as a csrf token that
    # is only valid together with the cookie this client received.
    browser_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    timezone: str | None = None
    cookies: tuple[Cookie, ...] = ()
    # Origin -> {key: value}, read at connect from the app's open tabs.
    local_storage: dict[str, dict[str, str]] = field(default_factory=dict)
