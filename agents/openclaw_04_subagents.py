from __future__ import annotations

import os
from pathlib import Path
from deepagents import create_deep_agent
from dotenv import load_dotenv
from connectors.jenkins import JENKINS_TOOLS
from connectors.vk import VK_TOOLS

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

TOOLS = [*JENKINS_TOOLS, *VK_TOOLS]
SUBAGENTS = [
    {
        "name": "repo-researcher",
        "description": "Trace repository flows and find factual code locations for integration analysis.",
        "system_prompt": "You find facts in the repository. Read/search files, cite exact paths, and avoid edits or unsupported claims.",
    },
    {
        "name": "analysis-reviewer",
        "description": "Check factual accuracy, missing components, contradictions, and operational risks in analysis reports.",
        "system_prompt": "You verify architecture analysis. Check cited paths, missing components, contradictions, and operational risks. Do not rewrite the whole solution.",
    },
]
BASE_PROMPT = """\
You are OpenClaw at stage 04. Respond in the user's language; default to Russian.
For repository integration analysis, delegate to repo-researcher first, then ask analysis-reviewer to check factual accuracy before finalizing.
In this demo, subagent roles are separated by prompt and context; production systems can assign separate tool sets and permissions.
"""
agent = create_deep_agent(
    model=os.getenv("OPENCLAW_MODEL", DEFAULT_MODEL),
    tools=TOOLS,
    system_prompt=BASE_PROMPT,
    subagents=SUBAGENTS,
    backend=_backend(),
)
