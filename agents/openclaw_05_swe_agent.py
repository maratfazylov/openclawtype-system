from __future__ import annotations

from pathlib import Path
from deepagents import create_deep_agent
from dotenv import load_dotenv
from agents.model_config import workshop_model
from connectors.jenkins import JENKINS_TOOLS
from connectors.vk import VK_TOOLS

REPO_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(REPO_ROOT / ".env")

def _workspace_root() -> Path:
    return REPO_ROOT


def _backend(*, require_shell: bool = False):
    from deepagents.backends import LocalShellBackend

    return LocalShellBackend(
        root_dir=_workspace_root(),
        virtual_mode=True,
        inherit_env=False,
        timeout=120,
        max_output_bytes=80_000,
    )

TOOLS = [*JENKINS_TOOLS, *VK_TOOLS]
SUBAGENTS = [
    {"name": "repo-researcher", "description": "Research repository facts before implementation.", "system_prompt": "Find relevant files, APIs, tests, and risks. Cite paths."},
    {"name": "patch-reviewer", "description": "Review concrete diffs and test coverage.", "system_prompt": "Review correctness, regressions, tests, and security. Expect the main agent to pass git diff and test results."},
]
SWE_PROMPT = """\
You are OpenClaw SWE agent. Respond in the user's language; default to Russian.
Follow this issue-resolution loop:
1. Reproduce or characterize the issue.
2. Localize relevant files and tests.
3. Patch the root cause.
4. Add or update regression coverage.
5. Run narrow tests first, then related checks.
6. Before delegating to patch-reviewer, run git diff for changed files and include the diff and test results in the reviewer task.
"""
swe_agent = create_deep_agent(
    model=workshop_model(),
    tools=TOOLS,
    system_prompt=SWE_PROMPT,
    subagents=SUBAGENTS,
    backend=_backend(require_shell=True),
)
