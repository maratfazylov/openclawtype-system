from __future__ import annotations

from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv


DEFAULT_MODEL = "openrouter:tencent/hy3:free"
REPO_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(REPO_ROOT / ".env")


def _workspace_root() -> Path:
    return REPO_ROOT


def _backend():
    from deepagents.backends import FilesystemBackend

    return FilesystemBackend(root_dir=_workspace_root(), virtual_mode=True)


WORKSPACE_PROMPT = """\
You are OpenClaw at stage 02 Workspace.
Respond in the user's language; default to Russian.

This graph adds a real workspace backend to the Core graph.
Use filesystem tools such as ls, glob, grep, and read_file before making
claims about repository files.

Important boundary:
- _backend connects the Deep Agent harness to the local workspace;
- filesystem paths are virtualized inside the configured workspace;
- this stage uses FilesystemBackend, not shell;
- secrets remain unavailable to filesystem tools.
"""


agent = create_deep_agent(
    model=DEFAULT_MODEL,
    tools=[],
    system_prompt=WORKSPACE_PROMPT,
    backend=_backend(),
)
