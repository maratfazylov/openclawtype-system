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
    model=os.getenv("OPENCLAW_MODEL", DEFAULT_MODEL),
    tools=TOOLS,
    system_prompt=SWE_PROMPT,
    subagents=SUBAGENTS,
    backend=_backend(require_shell=True),
)
