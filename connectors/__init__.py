"""Connector tools exposed to the OpenClaw agent."""

from connectors.demo import DEMO_TOOLS
from connectors.jenkins import JENKINS_TOOLS
from connectors.telegram import TELEGRAM_TOOLS
from connectors.vk import VK_TOOLS

CONNECTOR_TOOLS = [*DEMO_TOOLS, *TELEGRAM_TOOLS, *JENKINS_TOOLS, *VK_TOOLS]

__all__ = ["CONNECTOR_TOOLS"]
