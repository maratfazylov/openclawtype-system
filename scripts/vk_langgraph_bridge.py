"""VK → LangGraph polling bridge.

WHAT
    This script runs as a standalone daemon that polls VK for new messages
    and forwards them to a LangGraph assistant. The assistant processes the
    message and can reply back through VK tools.

WHY A SEPARATE SCRIPT?
    LangGraph itself cannot fetch VK messages — it only reacts when called.
    VK does not support webhooks for group/user messages without a public
    HTTPS server and VK Callback API setup. This bridge fills the gap with a
    simple polling loop.

HOW IT WORKS
    1. Calls VK API ``messages.getConversations(filter=unread)``
    2. Skips already-seen messages (tracked in a local JSON state file)
    3. Calls ``trigger_langgraph_run()`` which creates a LangGraph thread and run
    4. Optionally waits for the agent output and sends it back to VK
    5. Repeats every poll interval (default 5 seconds)

CONFIGURATION
    ``.env`` stores only credentials such as ``VK_ACCESS_TOKEN``. Runtime mode
    can be overridden per process with environment variables in the launch
    command, for example ``VK_BRIDGE_DRY_RUN=0``.

    ============================= =========== ==================================
    Var                           Default     Description
    ============================= =========== ==================================
    VK_ACCESS_TOKEN               —           VK API token (user or group)
    LANGGRAPH_URL                 local:2024  LangGraph server URL
    LANGGRAPH_ASSISTANT_ID        stage 04    Assistant graph id
    VK_BRIDGE_DRY_RUN             1           Preview only, no real runs
    VK_BRIDGE_REPLY_TO_VK         0           Send agent output back to VK
    VK_BRIDGE_WAIT_FOR_RUN        1           Wait for agent to finish
    VK_BRIDGE_POLL_SECONDS        5           Seconds between polls
    VK_BRIDGE_CONVERSATION_COUNT  10          Max conversations per poll
    VK_BRIDGE_STATE_PATH          ./.json     Path to seen-messages state
    VK_BRIDGE_ONCE                —           Single pass, then exit
    ============================= =========== ==================================

RUN
    Start LangGraph first::

        uv run langgraph dev --config langgraph.openclaw_path.json

    Run once in dry-run mode::

        VK_BRIDGE_ONCE=1 VK_BRIDGE_DRY_RUN=1 uv run python \\
            scripts/vk_langgraph_bridge.py

    Continuous live polling::

        VK_BRIDGE_DRY_RUN=0 uv run python scripts/vk_langgraph_bridge.py

    Background (recommended)::

        nohup uv run python scripts/vk_langgraph_bridge.py \\
            > /tmp/vk_bridge.log 2>&1 &
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from connectors.langgraph_bridge import trigger_langgraph_run
from connectors.vk import call_vk_api_method, send_vk_message


DEFAULT_STATE_PATH = ".openclaw_vk_bridge_state.json"


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, "").strip()
    return value or default


def _bool_env(name: str, default: bool = False) -> bool:
    value = _env(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"seen_message_ids": []}
    return json.loads(path.read_text())


def _save_state(path: Path, state: dict[str, Any]) -> None:
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")


def _conversation_items(count: int) -> list[dict[str, Any]]:
    result = call_vk_api_method.invoke(
        {
            "method": "messages.getConversations",
            "params": {
                "count": count,
                "filter": "unread",
                "extended": 0,
            },
            "dry_run": False,
        }
    )
    payload = json.loads(result)
    if not payload.get("ok"):
        raise RuntimeError(result)
    return payload["response"].get("response", {}).get("items", [])


def _extract_agent_text(output: Any) -> str:
    if isinstance(output, dict):
        messages = output.get("messages")
        if isinstance(messages, list) and messages:
            last = messages[-1]
            if isinstance(last, dict):
                content = last.get("content")
            else:
                content = getattr(last, "content", None)
            if isinstance(content, str) and content.strip():
                return content.strip()
    return json.dumps(output, ensure_ascii=False, default=str)


def process_once(state_path: Path) -> int:
    state = _load_state(state_path)
    seen = set(state.get("seen_message_ids", []))
    count = int(_env("VK_BRIDGE_CONVERSATION_COUNT", "10") or "10")
    dry_run = _bool_env("VK_BRIDGE_DRY_RUN", True)
    reply_to_vk = _bool_env("VK_BRIDGE_REPLY_TO_VK", False)
    wait = _bool_env("VK_BRIDGE_WAIT_FOR_RUN", True)

    processed = 0
    for item in _conversation_items(count):
        message = item.get("last_message") or {}
        message_id = str(message.get("id") or "")
        text = str(message.get("text") or "").strip()
        peer_id = str((message.get("peer_id") or ""))
        out = message.get("out")

        if not message_id or not text or out:
            continue
        if message_id in seen:
            continue

        result = trigger_langgraph_run(
            text,
            source="vk",
            metadata={
                "peer_id": peer_id,
                "vk_message_id": message_id,
                "from_id": message.get("from_id"),
            },
            wait=wait,
            dry_run=dry_run,
        )
        print(result)

        if reply_to_vk and not dry_run:
            payload = json.loads(result)
            reply = _extract_agent_text(payload.get("output"))
            print(
                send_vk_message.invoke(
                    {
                        "peer_id": peer_id,
                        "message": reply[:3500],
                        "dry_run": False,
                    }
                )
            )

        seen.add(message_id)
        processed += 1

    state["seen_message_ids"] = sorted(seen)[-500:]
    _save_state(state_path, state)
    return processed


def main() -> None:
    load_dotenv()
    state_path = Path(_env("VK_BRIDGE_STATE_PATH", DEFAULT_STATE_PATH) or DEFAULT_STATE_PATH)
    poll_seconds = float(_env("VK_BRIDGE_POLL_SECONDS", "5") or "5")
    once = _bool_env("VK_BRIDGE_ONCE", False)

    while True:
        processed = process_once(state_path)
        print(f"processed={processed}")
        if once:
            return
        time.sleep(poll_seconds)


if __name__ == "__main__":
    main()
