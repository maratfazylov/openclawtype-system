from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def find_repo_root(start: Path | None = None) -> Path:
    root = (start or Path.cwd()).resolve()
    while root != root.parent and not (root / "pyproject.toml").exists():
        root = root.parent
    if not (root / "pyproject.toml").exists():
        raise RuntimeError("Could not find repository root with pyproject.toml")
    return root


REPO_ROOT = find_repo_root()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

load_dotenv(REPO_ROOT / ".env")

DEFAULT_MODEL = "openrouter:tencent/hy3:free"
CONFIG_PATH = REPO_ROOT / "langgraph.openclaw_path.json"


def model_name() -> str:
    return os.getenv("OPENCLAW_MODEL", DEFAULT_MODEL)


def workspace_root() -> Path:
    return Path(os.getenv("OPENCLAW_WORKSPACE", str(REPO_ROOT))).expanduser().resolve()


def write_text(path: str, content: str) -> Path:
    target = REPO_ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    return target


def read_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"dependencies": ["."], "graphs": {}, "env": ".env"}
    return json.loads(CONFIG_PATH.read_text())


def register_graphs(graphs: dict[str, str]) -> Path:
    config = read_config()
    config.setdefault("dependencies", ["."])
    config.setdefault("graphs", {})
    config.setdefault("env", ".env")
    config["graphs"].update(graphs)
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n")
    return CONFIG_PATH


def print_stage_context(*, require_shell: bool = False) -> None:
    print(f"Repo root: {REPO_ROOT}")
    print(f"Agent workspace: {workspace_root()}")
    print(f"Model: {model_name()}")
    shell_enabled = os.getenv("OPENCLAW_ENABLE_LOCAL_SHELL") == "1"
    print(f"Local shell enabled: {shell_enabled}")
    if require_shell and not shell_enabled:
        raise RuntimeError("This stage requires OPENCLAW_ENABLE_LOCAL_SHELL=1 for pytest")
