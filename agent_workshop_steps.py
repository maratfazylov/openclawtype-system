"""Workshop-friendly OpenClaw agent.

Use this file for a live demo where the agent grows one layer at a time.

How to run:
1. Pick a value for WORKSHOP_STEP below.
2. Restart `uv run langgraph dev`.
3. Open assistant `openclaw_steps` in Studio or Deep Agents UI.

During the workshop you can uncomment the next WORKSHOP_STEP line, restart the
server, and show which capability appeared.
"""

from __future__ import annotations

import os
from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# Step selector
# ---------------------------------------------------------------------------
# Start tiny, then uncomment the next line for each workshop chapter.
# You can also override it without editing the file:
# OPENCLAW_WORKSHOP_STEP=3 uv run langgraph dev

# WORKSHOP_STEP = 1  # Minimal chat/coding agent, no custom tools.
# WORKSHOP_STEP = 2  # Add workspace-scoped filesystem backend.
# WORKSHOP_STEP = 3  # Add demo issue-tracker connector.
# WORKSHOP_STEP = 4  # Add Telegram connector in safe dry-run mode.
# WORKSHOP_STEP = 5  # Add subagents, skills, and durable memory.
WORKSHOP_STEP = 6  # Final version: also expose stricter SWE mode.


# ---------------------------------------------------------------------------
# Step 1: model + base prompt
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "openrouter:tencent/hy3:free"
DEFAULT_MINIMAX_BASE_URL = "https://api.minimaxi.chat/v1"
DEFAULT_MINIMAX_MODEL = "MiniMax-M2"
DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"

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


load_dotenv()


def _workshop_step() -> int:
    raw_step = os.getenv("OPENCLAW_WORKSHOP_STEP", str(WORKSHOP_STEP))
    try:
        step = int(raw_step)
    except ValueError as exc:
        raise ValueError("OPENCLAW_WORKSHOP_STEP must be an integer from 1 to 6") from exc

    if step < 1 or step > 6:
        raise ValueError("OPENCLAW_WORKSHOP_STEP must be between 1 and 6")

    return step


def _model():
    provider = os.getenv("OPENCLAW_PROVIDER")
    if provider == "minimax":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=os.getenv("MINIMAX_MODEL", DEFAULT_MINIMAX_MODEL),
            api_key=os.getenv("MINIMAX_API_KEY"),
            base_url=os.getenv("MINIMAX_BASE_URL", DEFAULT_MINIMAX_BASE_URL),
            temperature=0,
        )

    if provider == "deepseek":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=os.getenv("DEEPSEEK_MODEL", DEFAULT_DEEPSEEK_MODEL),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", DEFAULT_DEEPSEEK_BASE_URL),
            temperature=0,
        )

    return os.getenv("OPENCLAW_MODEL", DEFAULT_MODEL)


# ---------------------------------------------------------------------------
# Step 2: backend
# ---------------------------------------------------------------------------


def _workspace_root() -> Path:
    return Path(os.getenv("OPENCLAW_WORKSPACE", ".")).expanduser().resolve()


def _backend():
    """Return the backend used from Step 2 onward.

    Local shell execution stays opt-in because it can run commands on the host.
    Without OPENCLAW_ENABLE_LOCAL_SHELL=1 the agent only gets workspace-scoped
    file operations, which is safer for a live workshop.
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


# ---------------------------------------------------------------------------
# Step 3 and 4: connectors
# ---------------------------------------------------------------------------


def _connector_tools(step: int):
    if step < 3:
        return []

    if step >= 6:
        from connectors import CONNECTOR_TOOLS

        return CONNECTOR_TOOLS

    from connectors.demo import DEMO_TOOLS

    tools = [*DEMO_TOOLS]

    if step >= 4:
        from connectors.telegram import TELEGRAM_TOOLS

        tools.extend(TELEGRAM_TOOLS)

    return tools


# ---------------------------------------------------------------------------
# Step 5: subagents, skills, memory
# ---------------------------------------------------------------------------


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


def _agent_kwargs(step: int, *, swe_mode: bool = False) -> dict:
    kwargs = {
        "model": _model(),
        "tools": _connector_tools(step),
        "system_prompt": SWE_PROMPT if swe_mode else BASE_PROMPT,
    }

    if step >= 2:
        kwargs["backend"] = _backend()
        kwargs["interrupt_on"] = {"execute": True}

    if step >= 5:
        kwargs["subagents"] = SUBAGENTS
        kwargs["skills"] = ["/skills/swe-resolution"]
        kwargs["memory"] = ["/AGENTS.md"]
        if not swe_mode:
            kwargs["skills"].append("/skills/product-research")

    if swe_mode:
        kwargs["interrupt_on"] = {"execute": True, "write_file": True, "edit_file": True}

    return kwargs


# ---------------------------------------------------------------------------
# Runnable graphs
# ---------------------------------------------------------------------------

_STEP = _workshop_step()

# The main workshop graph. In LangGraph Studio / Deep Agents UI use:
# Assistant ID: openclaw_steps
agent = create_deep_agent(**_agent_kwargs(_STEP))

# Step 6 exposes the strict SWE variant too. Before Step 6 it is intentionally
# the same graph as `agent`, so `langgraph dev` can still import this module.
swe_agent = (
    create_deep_agent(**_agent_kwargs(_STEP, swe_mode=True))
    if _STEP >= 6
    else agent
)
