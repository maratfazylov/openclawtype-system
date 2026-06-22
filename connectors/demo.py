"""Demo connectors for workshop scenarios.

Real connectors follow the same shape: keep integration code small, expose
well-described LangChain tools, then pass those tools into `create_deep_agent`.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from langchain_core.tools import tool


@dataclass(frozen=True)
class DemoIssue:
    id: str
    title: str
    status: str
    priority: str
    owner: str
    summary: str


DEMO_ISSUES = [
    DemoIssue(
        id="DEMO-101",
        title="Add connector onboarding flow",
        status="ready",
        priority="high",
        owner="workshop",
        summary=(
            "Show how a connector becomes an agent tool without changing the "
            "Deep Agents runtime."
        ),
    ),
    DemoIssue(
        id="DEMO-102",
        title="Enable local shell mode guardrails",
        status="backlog",
        priority="medium",
        owner="platform",
        summary="Document the risks and add an approval checklist before enabling shell mode.",
    ),
]


def _issue_payload(issue: DemoIssue) -> str:
    return json.dumps(asdict(issue), ensure_ascii=False, indent=2)


@tool
def list_demo_issues() -> str:
    """List issues from the demo issue tracker connector."""
    return json.dumps([asdict(issue) for issue in DEMO_ISSUES], ensure_ascii=False, indent=2)


@tool
def get_demo_issue(issue_id: str) -> str:
    """Fetch one issue from the demo issue tracker connector by id, for example DEMO-101."""
    normalized_id = issue_id.strip().upper()
    for issue in DEMO_ISSUES:
        if issue.id == normalized_id:
            return _issue_payload(issue)
    known_ids = ", ".join(issue.id for issue in DEMO_ISSUES)
    return f"Unknown issue id {issue_id!r}. Known ids: {known_ids}"


DEMO_TOOLS = [list_demo_issues, get_demo_issue]
