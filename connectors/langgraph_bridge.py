"""LangGraph SDK helpers used by external connector bridges."""

from __future__ import annotations

import json
import os
from typing import Any

from langgraph_sdk import get_sync_client


DEFAULT_LANGGRAPH_URL = "http://127.0.0.1:2024"
DEFAULT_ASSISTANT_ID = "openclaw_04_vk_bridge"


def _env(name: str) -> str | None:
    value = os.getenv(name, "").strip()
    return value or None


def _json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def langgraph_url(url: str | None = None) -> str:
    return url or _env("LANGGRAPH_URL") or DEFAULT_LANGGRAPH_URL


def assistant_id(assistant: str | None = None) -> str:
    return assistant or _env("LANGGRAPH_ASSISTANT_ID") or DEFAULT_ASSISTANT_ID


def build_agent_input(message: str, *, source: str, metadata: dict[str, Any] | None = None) -> dict:
    context = {
        "source": source,
        **(metadata or {}),
    }
    return {
        "messages": [
            {
                "role": "user",
                "content": f"External message context: {json.dumps(context, ensure_ascii=False)}\n\n{message}",
            }
        ]
    }


def _resolve_assistant_uuid(client: Any, assistant_name: str) -> str:
    """Resolve an assistant graph name (e.g. 'openclaw_notebook') to its UUID."""
    import uuid

    try:
        uuid.UUID(assistant_name)
        return assistant_name
    except ValueError:
        pass

    results = client.assistants.search(graph_id=assistant_name)
    if results:
        return results[0]["assistant_id"]

    msg = f"Assistant '{assistant_name}' not found on the LangGraph server. "
    msg += "Check LANGGRAPH_ASSISTANT_ID and the server config (langgraph.json vs langgraph.notebook.json)."
    raise ValueError(msg)


def trigger_langgraph_run(
    message: str,
    *,
    source: str,
    metadata: dict[str, Any] | None = None,
    thread_id: str | None = None,
    assistant: str | None = None,
    url: str | None = None,
    wait: bool = True,
    dry_run: bool = True,
) -> str:
    """Trigger a LangGraph assistant run from an external message."""
    resolved_url = langgraph_url(url)
    resolved_assistant = assistant_id(assistant)
    agent_input = build_agent_input(message, source=source, metadata=metadata)

    preview = {
        "langgraph_url": resolved_url,
        "assistant_id": resolved_assistant,
        "input": agent_input,
        "thread_id": thread_id,
        "wait": wait,
    }

    if dry_run:
        return _json({"dry_run": True, **preview})

    client = get_sync_client(url=resolved_url)
    assistant_uuid = _resolve_assistant_uuid(client, resolved_assistant)

    def _create_thread() -> str:
        thread = client.threads.create(
            metadata={
                "source": source,
                **(metadata or {}),
            }
        )
        return thread["thread_id"]

    resolved_thread_id = thread_id or _create_thread()

    result: dict[str, Any] = {
        "ok": True,
        **preview,
        "thread_id": resolved_thread_id,
    }

    def _run(target_thread_id: str) -> tuple[Any, str]:
        if wait:
            run_meta: dict[str, str] = {}

            def _capture(meta):
                run_meta["run_id"] = meta["run_id"]

            output = client.runs.wait(
                target_thread_id,
                assistant_uuid,
                input=agent_input,
                multitask_strategy="enqueue",
                on_run_created=_capture,
            )
            return output, run_meta.get("run_id", "")

        run = client.runs.create(
            target_thread_id,
            assistant_uuid,
            input=agent_input,
            stream_mode="values",
            multitask_strategy="enqueue",
        )
        return None, run["run_id"]

    try:
        output, run_id = _run(resolved_thread_id)
    except Exception as exc:
        stale_thread = thread_id is not None and (
            "404" in str(exc) or "not found" in str(exc).lower()
        )
        if not stale_thread:
            raise
        resolved_thread_id = _create_thread()
        result["thread_id"] = resolved_thread_id
        result["recreated_thread"] = True
        output, run_id = _run(resolved_thread_id)

    if wait:
        result["output"] = output
    result["run_id"] = run_id

    return _json(result)
