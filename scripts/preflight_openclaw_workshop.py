"""Preflight checks for the OpenClaw workshop live demo."""

from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def ok(label: str, detail: str = "") -> None:
    print(f"✓ {label}{': ' + detail if detail else ''}")


def warn(label: str, detail: str = "") -> None:
    print(f"! {label}{': ' + detail if detail else ''}")


def require(label: str, condition: bool, detail: str = "") -> bool:
    if condition:
        ok(label, detail)
        return True
    warn(label, detail)
    return False


def main() -> int:
    load_dotenv(ROOT / ".env")
    failures = 0

    failures += not require("pyproject.toml found", (ROOT / "pyproject.toml").exists(), str(ROOT))
    failures += not require("OPENCLAW_MODEL set", bool(os.getenv("OPENCLAW_MODEL")), os.getenv("OPENCLAW_MODEL", ""))

    for module_name in ("deepagents", "langgraph_sdk", "connectors.jenkins", "connectors.vk"):
        try:
            importlib.import_module(module_name)
            ok(f"import {module_name}")
        except Exception as exc:  # pragma: no cover - CLI diagnostics
            warn(f"import {module_name}", str(exc))
            failures += 1

    from connectors.jenkins import get_jenkins_job_info, trigger_jenkins_job
    from connectors.vk import get_vk_current_user, send_vk_message

    jenkins_preview = trigger_jenkins_job.invoke(
        {"parameters": {"OPENCLAW_SMOKE": "true"}, "dry_run": True}
    )
    ok("Jenkins trigger dry-run", jenkins_preview.splitlines()[0])

    if os.getenv("JENKINS_JOB_TOKEN") or (
        os.getenv("JENKINS_USERNAME") and os.getenv("JENKINS_API_TOKEN")
    ):
        ok("Jenkins credentials present")
        if os.getenv("OPENCLAW_PREFLIGHT_LIVE") == "1":
            print(get_jenkins_job_info.invoke({}))
    else:
        warn("Jenkins credentials missing", "real build will not start")

    vk_preview = send_vk_message.invoke(
        {
            "peer_id": os.getenv("VK_PEER_ID", "123"),
            "message": "OpenClaw workshop preflight",
            "random_id": 42,
            "dry_run": True,
        }
    )
    ok("VK send dry-run", vk_preview.splitlines()[0])

    if os.getenv("VK_ACCESS_TOKEN"):
        ok("VK token present")
        if os.getenv("OPENCLAW_PREFLIGHT_LIVE") == "1":
            print(get_vk_current_user.invoke({"dry_run": False}))
    else:
        warn("VK token missing", "real VK send/bridge will not work")

    failures += not require("VK_PEER_ID set", bool(os.getenv("VK_PEER_ID")), os.getenv("VK_PEER_ID", ""))
    ok("LANGGRAPH_URL", os.getenv("LANGGRAPH_URL", "http://127.0.0.1:2024"))
    ok("LANGGRAPH_ASSISTANT_ID", os.getenv("LANGGRAPH_ASSISTANT_ID", "openclaw_03/openclaw_05_swe"))

    if os.getenv("OPENCLAW_ENABLE_LOCAL_SHELL") == "1":
        ok("local shell enabled for stage 05")
    else:
        warn("local shell disabled", "stage 05 cannot run pytest")

    config = ROOT / "langgraph.openclaw_path.json"
    if config.exists():
        graphs = json.loads(config.read_text()).get("graphs", {})
        ok("LangGraph config", ", ".join(sorted(graphs)) or "no graphs yet")
        missing_targets = []
        for target in graphs.values():
            module_path = target.split(":", 1)[0]
            path = ROOT / module_path.lstrip("./")
            if not path.exists():
                missing_targets.append(module_path)
        if missing_targets:
            warn("generated agent files missing", ", ".join(missing_targets))
            if os.getenv("OPENCLAW_PREFLIGHT_REQUIRE_GRAPHS") == "1":
                failures += 1
    else:
        warn("LangGraph config missing", "run notebooks 01-05 first")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
