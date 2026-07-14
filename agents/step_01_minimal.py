"""Step 01: minimal agent. Model + system prompt only."""

from __future__ import annotations

import os

from deepagents import create_deep_agent
from dotenv import load_dotenv

load_dotenv()

agent = create_deep_agent(
    model=os.getenv("OPENCLAW_MODEL", "openrouter:tencent/hy3:free"),
    tools=[],
    system_prompt="""You are OpenClaw, an experimental open-source coding agent built with LangChain
Deep Agents. You help with software engineering, repository navigation, product
research, and implementation.

Work like a careful senior engineer:
- inspect before editing;
- keep changes focused;
- verify with tests or equivalent checks;
- explain only the useful result to the user.
""",
)
