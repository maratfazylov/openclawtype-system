"""Telegram Bot API connector tools.

The connector is safe for workshops by default: `send_telegram_message` runs in
dry-run mode unless explicitly told otherwise.
"""

from __future__ import annotations

import json
import os
from typing import Any

import httpx
from langchain_core.tools import tool


TELEGRAM_API_BASE = "https://api.telegram.org"
TELEGRAM_TIMEOUT = 15.0


def _telegram_token() -> str | None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    return token or None


def _default_chat_id() -> str | None:
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    return chat_id or None


def _telegram_url(method: str, token: str) -> str:
    return f"{TELEGRAM_API_BASE}/bot{token}/{method}"


def _json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


@tool
def send_telegram_message(message: str, chat_id: str | None = None, dry_run: bool = True) -> str:
    """Send a message through Telegram Bot API, or preview it when dry_run is true.

    Args:
        message: Text to send.
        chat_id: Telegram chat id. If omitted, TELEGRAM_CHAT_ID is used.
        dry_run: When true, return the prepared payload without sending.
    """
    resolved_chat_id = (chat_id or _default_chat_id() or "").strip()
    payload = {
        "chat_id": resolved_chat_id or "<missing TELEGRAM_CHAT_ID>",
        "text": message,
        "disable_web_page_preview": True,
    }

    if dry_run:
        return _json({"dry_run": True, "method": "sendMessage", "payload": payload})

    token = _telegram_token()
    if not token:
        return "TELEGRAM_BOT_TOKEN is not set. Set it in .env or call with dry_run=True."
    if not resolved_chat_id:
        return "Telegram chat_id is missing. Pass chat_id or set TELEGRAM_CHAT_ID in .env."

    response = httpx.post(
        _telegram_url("sendMessage", token),
        json=payload,
        timeout=TELEGRAM_TIMEOUT,
    )
    if response.is_error:
        return _json(
            {
                "ok": False,
                "status_code": response.status_code,
                "response": response.text,
            }
        )
    return _json(response.json())


@tool
def get_telegram_updates(limit: int = 5) -> str:
    """Read recent Telegram Bot API updates for the configured bot token."""
    token = _telegram_token()
    if not token:
        return "TELEGRAM_BOT_TOKEN is not set. Add it to .env to read updates."

    bounded_limit = max(1, min(limit, 20))
    response = httpx.get(
        _telegram_url("getUpdates", token),
        params={"limit": bounded_limit},
        timeout=TELEGRAM_TIMEOUT,
    )
    if response.is_error:
        return _json(
            {
                "ok": False,
                "status_code": response.status_code,
                "response": response.text,
            }
        )
    return _json(response.json())


TELEGRAM_TOOLS = [send_telegram_message, get_telegram_updates]
