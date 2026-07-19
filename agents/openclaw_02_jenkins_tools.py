from __future__ import annotations

import os
from pathlib import Path
from deepagents import create_deep_agent
from dotenv import load_dotenv
from connectors.jenkins import JENKINS_TOOLS

load_dotenv()
DEFAULT_MODEL = "openrouter:tencent/hy3:free"

def _workspace_root() -> Path:
    return Path(os.getenv("OPENCLAW_WORKSPACE", ".")).expanduser().resolve()


def _backend(*, require_shell: bool = False):
    root = _workspace_root()
    shell_enabled = os.getenv("OPENCLAW_ENABLE_LOCAL_SHELL") == "1"
    if require_shell and not shell_enabled:
        raise RuntimeError("OPENCLAW_ENABLE_LOCAL_SHELL=1 is required for this stage")
    if shell_enabled:
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

BASE_PROMPT = """\
You are OpenClaw at stage 02 with Jenkins tools. Respond in the user's language; default to Russian.
Separate read actions from write actions.
Read tools can inspect job metadata and config.
Write tools can trigger builds, copy jobs, and create jobs from config.xml.
If the user explicitly asks for a real Jenkins mutation, call the matching Jenkins tool with dry_run=False.
Return normalized operational summaries, not raw dumps.
"""
agent = create_deep_agent(
    model=os.getenv("OPENCLAW_MODEL", DEFAULT_MODEL),
    tools=JENKINS_TOOLS,
    system_prompt=BASE_PROMPT,
    backend=_backend(),
)
