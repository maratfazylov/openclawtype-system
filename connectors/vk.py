"""VK API connector tools.

The connector keeps mutating operations in dry-run mode by default. Store the
real token in ``VK_ACCESS_TOKEN`` and never in source files.
"""

from __future__ import annotations

import json
import os
import random
from typing import Any

import httpx
from langchain_core.tools import tool

from connectors.langgraph_bridge import trigger_langgraph_run


VK_API_BASE = "https://api.vk.com/method"
DEFAULT_VK_API_VERSION = "5.199"
VK_TIMEOUT = 20.0


def _env(name: str) -> str | None:
    value = os.getenv(name, "").strip()
    return value or None


def _access_token() -> str | None:
    return _env("VK_ACCESS_TOKEN")


def _api_version() -> str:
    return _env("VK_API_VERSION") or DEFAULT_VK_API_VERSION


def _json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def _mask_secret(secret: str | None) -> str:
    if not secret:
        return "<missing>"
    if len(secret) <= 8:
        return "<set>"
    return f"{secret[:4]}...{secret[-4:]}"


def _method_url(method: str) -> str:
    normalized = method.strip().lstrip("/")
    return f"{VK_API_BASE}/{normalized}"


def _request_payload(params: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {key: value for key, value in (params or {}).items() if value is not None}
    payload["v"] = _api_version()
    token = _access_token()
    if token:
        payload["access_token"] = token
    return payload


def _preview_payload(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dict(payload)
    preview["access_token"] = _mask_secret(_access_token())
    return preview


@tool
def call_vk_api_method(
    method: str,
    params: dict[str, Any] | None = None,
    dry_run: bool = True,
) -> str:
    """Call a VK API method, or preview the request when dry_run is true.

    Args:
        method: VK API method name, for example users.get.
        params: Method parameters without access_token or v.
        dry_run: When true, return the prepared request without calling VK.
    """
    payload = _request_payload(params)
    preview = {
        "method": method.strip(),
        "url": _method_url(method),
        "uses_access_token": bool(_access_token()),
        "payload": _preview_payload(payload),
    }

    if dry_run:
        return _json({"dry_run": True, **preview})

    if not _access_token():
        return "VK_ACCESS_TOKEN is not set. Add it to .env or call with dry_run=True."

    try:
        response = httpx.post(_method_url(method), data=payload, timeout=VK_TIMEOUT)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        return _json({"ok": False, **preview, "error": str(exc)})

    data = response.json()
    if "error" in data:
        return _json({"ok": False, **preview, "response": data})
    return _json({"ok": True, **preview, "response": data})


@tool
def get_vk_current_user(dry_run: bool = False) -> str:
    """Read the VK profile visible to the configured access token."""
    return call_vk_api_method.invoke(
        {
            "method": "users.get",
            "params": {"fields": "screen_name,photo_100"},
            "dry_run": dry_run,
        }
    )


@tool
def send_vk_message(
    peer_id: str,
    message: str,
    random_id: int | None = None,
    dry_run: bool = True,
) -> str:
    """Send a VK message, or preview it when dry_run is true.

    Args:
        peer_id: VK peer id, user id, chat id, or group conversation peer id.
        message: Message text.
        random_id: Optional VK random_id for idempotency. Generated when omitted.
        dry_run: When true, return the prepared payload without sending.
    """
    resolved_random_id = random_id if random_id is not None else random.randint(1, 2_147_483_647)
    return call_vk_api_method.invoke(
        {
            "method": "messages.send",
            "params": {
                "peer_id": peer_id,
                "message": message,
                "random_id": resolved_random_id,
            },
            "dry_run": dry_run,
        }
    )


@tool
def trigger_langgraph_from_vk_message(
    peer_id: str,
    message: str,
    vk_message_id: str | None = None,
    assistant_id: str | None = None,
    langgraph_url: str | None = None,
    wait: bool = True,
    dry_run: bool = True,
) -> str:
    """Trigger a LangGraph assistant run from a VK message.

    Args:
        peer_id: VK peer id where the message came from.
        message: VK message text to pass to the agent.
        vk_message_id: Optional VK message id for traceability.
        assistant_id: LangGraph assistant id. Defaults to LANGGRAPH_ASSISTANT_ID.
        langgraph_url: LangGraph API URL. Defaults to LANGGRAPH_URL.
        wait: Wait for the run result before returning.
        dry_run: When true, preview the LangGraph request without starting a run.
    """
    return trigger_langgraph_run(
        message,
        source="vk",
        metadata={
            "peer_id": peer_id,
            "vk_message_id": vk_message_id,
        },
        assistant=assistant_id,
        url=langgraph_url,
        wait=wait,
        dry_run=dry_run,
    )


# Runtime tools exposed to the agent. Inbound bridge helpers stay importable for
# tests and channel workers, but the agent should not recursively start another
# LangGraph run from inside its own run.
VK_TOOLS = [
    get_vk_current_user,
    send_vk_message,
]
