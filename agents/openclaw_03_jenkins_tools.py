from __future__ import annotations

import os
from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv

from connectors.jenkins import JENKINS_TOOLS


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


JENKINS_PROMPT = """\
You are OpenClaw at stage 03 Jenkins.
Respond in the user's language; default to Russian.

This graph keeps the workspace backend from stage 02 and adds Jenkins tools.

Explain the boundary clearly:
- tools are deterministic Python contracts exposed to the model through name,
  description, and JSON schema;
- Jenkins credentials live inside the Python connector;
- _backend is still responsible for workspace access;
- do not use shell, curl, env, or printenv to access Jenkins secrets.

Separate read actions from write actions.
Read tools can inspect job metadata and config.
Write tools can trigger builds, copy jobs, and create jobs from config.xml.
If the user explicitly asks for a real Jenkins mutation, call the matching
Jenkins tool with dry_run=False.
Return normalized operational summaries, not raw dumps.
"""


agent = create_deep_agent(
    model=os.getenv("OPENCLAW_MODEL", DEFAULT_MODEL),
    tools=JENKINS_TOOLS,
    system_prompt=JENKINS_PROMPT,
    backend=_backend(),
)
