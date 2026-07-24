from __future__ import annotations

from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv

from agents.model_config import workshop_model
from connectors.jenkins import JENKINS_TOOLS


REPO_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(REPO_ROOT / ".env")


def _workspace_root() -> Path:
    return REPO_ROOT


def _backend():
    from deepagents.backends import FilesystemBackend

    return FilesystemBackend(root_dir=_workspace_root(), virtual_mode=True)


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
    model=workshop_model(),
    tools=JENKINS_TOOLS,
    system_prompt=JENKINS_PROMPT,
    backend=_backend(),
)
