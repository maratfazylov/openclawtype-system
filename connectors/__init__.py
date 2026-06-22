"""Connector tools exposed to the OpenClaw agent."""

from connectors.demo import DEMO_TOOLS
from connectors.telegram import TELEGRAM_TOOLS

CONNECTOR_TOOLS = [*DEMO_TOOLS, *TELEGRAM_TOOLS]

__all__ = ["CONNECTOR_TOOLS"]
