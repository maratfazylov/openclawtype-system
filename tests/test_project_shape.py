from pathlib import Path

from connectors.demo import get_demo_issue, list_demo_issues
from connectors.telegram import send_telegram_message


def test_langgraph_config_exposes_expected_assistants() -> None:
    config = Path("langgraph.json").read_text()

    assert '"openclaw"' in config
    assert '"openclaw_swe"' in config
    assert '"openclaw_steps"' in config
    assert '"openclaw_steps_swe"' in config


def test_agent_file_keeps_local_shell_opt_in() -> None:
    agent_source = Path("agent.py").read_text()

    assert "OPENCLAW_ENABLE_LOCAL_SHELL" in agent_source
    assert '!= "1"' in agent_source


def test_workshop_agent_is_split_into_uncommentable_steps() -> None:
    source = Path("agent_workshop_steps.py").read_text()

    assert "# WORKSHOP_STEP = 1" in source
    assert "WORKSHOP_STEP = 6" in source
    assert "OPENCLAW_WORKSHOP_STEP" in source
    assert "OPENCLAW_ENABLE_LOCAL_SHELL" in source


def test_demo_connector_exposes_issue_data() -> None:
    issues = list_demo_issues.invoke({})
    issue = get_demo_issue.invoke({"issue_id": "DEMO-101"})

    assert "DEMO-101" in issues
    assert "connector" in issue.lower()


def test_telegram_connector_dry_run_does_not_require_credentials() -> None:
    result = send_telegram_message.invoke(
        {"message": "OpenClaw connectors are working.", "dry_run": True}
    )

    assert '"dry_run": true' in result
    assert "OpenClaw connectors are working." in result


def test_manim_presentation_targets_3b1b_manim_gl() -> None:
    source = Path("presentation/openclawtype_manim.py").read_text()

    assert "from manimlib import *" in source
    assert "class ArchitectureScene" in source
    assert "class TelegramConnectorScene" in source
