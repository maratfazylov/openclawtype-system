from __future__ import annotations

import os
from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv


DEFAULT_MODEL = "openrouter:tencent/hy3:free"


def _find_repo_root(start: Path | None = None) -> Path:
    root = (start or Path.cwd()).resolve()
    while root != root.parent and not (root / "pyproject.toml").exists():
        root = root.parent
    if not (root / "pyproject.toml").exists():
        raise RuntimeError("Could not find repository root with pyproject.toml")
    return root


REPO_ROOT = _find_repo_root()
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


MINIMAL_PROMPT = """You are OpenClaw at stage 01 before the real workspace backend is attached.
Respond in the user's language; default to Russian.
If the user asks about repository files, explain that this graph does not have access to the real repository workspace yet.
Do not guess repository structure from the prompt.
"""

FILESYSTEM_PROMPT = """You are OpenClaw at stage 01 with the real workspace backend attached.
Respond in the user's language; default to Russian.
You can inspect the repository through the filesystem tools: ls, glob, grep, and read_file.
For repository claims, first call filesystem tools and cite the files you inspected.
Do not say that the backend is disabled; this graph is the filesystem-enabled variant.
"""


agent = create_deep_agent(
    model=os.getenv("OPENCLAW_MODEL", DEFAULT_MODEL),
    tools=[],
    system_prompt=MINIMAL_PROMPT,
)

agent_with_filesystem = create_deep_agent(
    model=os.getenv("OPENCLAW_MODEL", DEFAULT_MODEL),
    tools=[],
    system_prompt=FILESYSTEM_PROMPT,
    backend=_backend(),
)
