from __future__ import annotations

import os
from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv


DEFAULT_MODEL = "openrouter:tencent/hy3:free"
REPO_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(REPO_ROOT / ".env")


def _workspace_root() -> Path:
    return Path(os.getenv("OPENCLAW_WORKSPACE", str(REPO_ROOT))).expanduser().resolve()


def _backend():
    root = _workspace_root()
    if os.getenv("OPENCLAW_ENABLE_LOCAL_SHELL") == "1":
        from deepagents.backends import LocalShellBackend

        return LocalShellBackend(
            root_dir=root,
            virtual_mode=True,
            inherit_env=False,
            timeout=120,
            max_output_bytes=80_000,
        )

    from deepagents.backends import FilesystemBackend

    return FilesystemBackend(root_dir=root, virtual_mode=True)


WORKSPACE_PROMPT = """\
You are OpenClaw at stage 02 Workspace.
Respond in the user's language; default to Russian.

This graph adds a real workspace backend to the Core graph.
Use filesystem tools such as ls, glob, grep, and read_file before making
claims about repository files.

Important boundary:
- _backend connects the Deep Agent harness to the local workspace;
- filesystem paths are virtualized inside the configured workspace;
- shell is available only when OPENCLAW_ENABLE_LOCAL_SHELL=1;
- shell does not inherit secrets from .env.
"""


agent = create_deep_agent(
    model=os.getenv("OPENCLAW_MODEL", DEFAULT_MODEL),
    tools=[],
    system_prompt=WORKSPACE_PROMPT,
    backend=_backend(),
)
