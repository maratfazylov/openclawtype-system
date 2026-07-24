import ast
import json
from pathlib import Path

from connectors.demo import get_demo_issue, list_demo_issues
from connectors.jenkins import JENKINS_TOOLS, copy_jenkins_job, trigger_jenkins_job
from connectors.telegram import send_telegram_message
from connectors.vk import send_vk_message, trigger_langgraph_from_vk_message


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
    assert "CONNECTOR_TOOLS" in source


def test_workshop_notebooks_are_present_and_valid() -> None:
    expected = [
        "00_full_interactive_workshop.ipynb",
        "01_minimal_agent.ipynb",
        "02_filesystem_backend.ipynb",
        "03_demo_connector.ipynb",
        "04_telegram_connector.ipynb",
        "05_subagents_skills_memory.ipynb",
        "06_swe_mode.ipynb",
        "07_jenkins_connector.ipynb",
        "08_single_notebook_langgraph_project.ipynb",
    ]

    notebook_dir = Path("workshop_notebooks")
    actual = sorted(path.name for path in notebook_dir.glob("*.ipynb"))

    assert actual == expected

    for notebook_path in notebook_dir.glob("*.ipynb"):
        notebook = json.loads(notebook_path.read_text())
        assert notebook["nbformat"] == 4
        assert notebook["metadata"]["kernelspec"]["name"] == "python3"
        assert notebook["metadata"]["kernelspec"]["display_name"] == "Python 3 (.venv)"
        assert "sk-or-" not in notebook_path.read_text()
        for index, cell in enumerate(notebook["cells"], start=1):
            if cell["cell_type"] == "code":
                ast.parse("".join(cell["source"]), filename=f"{notebook_path}:cell-{index}")


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


def test_jenkins_connector_dry_run_masks_job_token(monkeypatch) -> None:
    token = "abcd1234TOKENVALUEwxyz9876"
    monkeypatch.setenv("JENKINS_JOB_TOKEN", token)

    result = trigger_jenkins_job.invoke({"dry_run": True})

    assert '"dry_run": true' in result
    assert "https://devops.brojs.ru/job/marat/" in result
    assert "abcd...9876" in result
    assert token not in result


def test_jenkins_tools_include_job_management_tools() -> None:
    tool_names = {tool.name for tool in JENKINS_TOOLS}

    assert "get_jenkins_job_info" in tool_names
    assert "trigger_jenkins_job" in tool_names
    assert "get_jenkins_job_config" in tool_names
    assert "copy_jenkins_job" in tool_names
    assert "create_jenkins_job_from_config" in tool_names


def test_jenkins_copy_job_dry_run_builds_copy_request() -> None:
    result = copy_jenkins_job.invoke(
        {
            "new_job_name": "test02",
            "source_job_url": "https://devops.brojs.ru/job/marat/job/test01/",
            "dry_run": True,
        }
    )

    assert '"dry_run": true' in result
    assert '"mode": "copy"' in result
    assert '"source_full_name": "marat/test01"' in result
    assert "https://devops.brojs.ru/job/marat/" in result
    assert '"new_job_name": "test02"' in result


def test_vk_connector_dry_run_masks_access_token(monkeypatch) -> None:
    token = "vk1.a.syntheticACCESS_TOKENvalue"
    monkeypatch.setenv("VK_ACCESS_TOKEN", token)

    result = send_vk_message.invoke(
        {
            "peer_id": "123",
            "message": "OpenClaw VK connector is configured.",
            "random_id": 42,
            "dry_run": True,
        }
    )

    assert '"dry_run": true' in result
    assert "messages.send" in result
    assert "OpenClaw VK connector is configured." in result
    assert "vk1....alue" in result
    assert token not in result


def test_vk_connector_can_preview_langgraph_trigger() -> None:
    result = trigger_langgraph_from_vk_message.invoke(
        {
            "peer_id": "123",
            "message": "OpenClaw VK bridge demo.",
            "vk_message_id": "demo-1",
            "dry_run": True,
        }
    )

    assert '"dry_run": true' in result
    assert "openclaw_04_vk_bridge" in result
    assert "OpenClaw VK bridge demo." in result
    assert '\\"source\\": \\"vk\\"' in result


def test_manim_presentation_targets_3b1b_manim_gl() -> None:
    source = Path("presentation/openclawtype_manim.py").read_text()

    assert "from manimlib import *" in source
    assert "class ArchitectureScene" in source
    assert "class TelegramConnectorScene" in source
