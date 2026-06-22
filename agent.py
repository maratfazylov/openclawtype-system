"""LangGraph entrypoints for an OpenClaw-like Deep Agents prototype."""

from __future__ import annotations

import os
from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv

from connectors import CONNECTOR_TOOLS


DEFAULT_MODEL = "openai:gpt-5.3-codex"


load_dotenv()


def _model() -> str:
    return os.getenv("OPENCLAW_MODEL", DEFAULT_MODEL)


def _workspace_root() -> Path:
    return Path(os.getenv("OPENCLAW_WORKSPACE", ".")).expanduser().resolve()


def _backend():
    """Return a backend.

    The local shell backend intentionally stays opt-in. It executes commands on
    the host machine, so the default backend only exposes workspace-scoped file
    operations for UI and prompt experiments.
    """
    root_dir = _workspace_root()

    if os.getenv("OPENCLAW_ENABLE_LOCAL_SHELL") != "1":
        from deepagents.backends import FilesystemBackend

        return FilesystemBackend(root_dir=root_dir, virtual_mode=True)

    from deepagents.backends import LocalShellBackend

    return LocalShellBackend(
        root_dir=root_dir,
        virtual_mode=True,
        inherit_env=True,
        timeout=120,
        max_output_bytes=80_000,
    )


BASE_PROMPT = """\
You are OpenClaw, an experimental open-source coding agent built with LangChain
Deep Agents. You help with software engineering, repository navigation, product
research, and implementation.

Work like a careful senior engineer:
- inspect before editing;
- keep changes focused;
- verify with tests or equivalent checks;
- explain only the useful result to the user.

If local shell execution is unavailable, use filesystem tools and clearly state
which verification would require shell access.
"""


SWE_PROMPT = BASE_PROMPT + """\

You are running in SWE mode. Optimize for issue resolution:
- reproduce or characterize the failure first;
- localize the root cause before patching;
- add regression coverage where practical;
- run the narrowest useful verification before broad checks;
- keep a clear chain from issue to patch to test.
"""


SUBAGENTS = [
    {
        "name": "repo-researcher",
        "description": "Map repository structure, APIs, tests, and likely change locations.",
        "system_prompt": (
            "You research codebases. Inspect files, identify relevant modules, "
            "and return concise findings with file paths and rationale."
        ),
    },
    {
        "name": "reviewer",
        "description": "Review proposed patches for bugs, missing tests, and regressions.",
        "system_prompt": (
            "You are a code reviewer. Focus on correctness, edge cases, tests, "
            "security, and maintainability. Be specific and concise."
        ),
    },
]


agent = create_deep_agent(
    model=_model(),
    tools=CONNECTOR_TOOLS,
    system_prompt=BASE_PROMPT,
    subagents=SUBAGENTS,
    skills=["/skills/swe-resolution", "/skills/product-research"],
    memory=["/AGENTS.md"],
    backend=_backend(),
    interrupt_on={"execute": True},
)

swe_agent = create_deep_agent(
    model=_model(),
    tools=CONNECTOR_TOOLS,
    system_prompt=SWE_PROMPT,
    subagents=SUBAGENTS,
    skills=["/skills/swe-resolution"],
    memory=["/AGENTS.md"],
    backend=_backend(),
    interrupt_on={"execute": True, "write_file": True, "edit_file": True},
)
