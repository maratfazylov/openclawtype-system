from __future__ import annotations

from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv


DEFAULT_MODEL = "openrouter:tencent/hy3:free"
REPO_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(REPO_ROOT / ".env")


CORE_PROMPT = """\
You are OpenClaw at stage 01 Core.
Respond in the user's language; default to Russian.

This graph demonstrates only the core Deep Agent harness:
- model;
- LangGraph state;
- message history;
- agent loop;
- no real workspace backend;
- no external tools.

If the user asks about repository files or external systems, explain that this
Core graph cannot inspect the real repository or call external APIs yet. Do not guess.
"""


agent = create_deep_agent(
    model=DEFAULT_MODEL,
    tools=[],
    system_prompt=CORE_PROMPT,
)
