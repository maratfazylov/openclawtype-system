# OpenClaw Deep Agents Prototype

Minimal OpenClaw-like coding agent built on LangChain Deep Agents and compatible
with `langchain-ai/deep-agents-ui`.

## What This Is

This repo is intentionally small:

- `agent.py` defines two LangGraph assistants:
  - `openclaw`: general coding/research agent
  - `openclaw_swe`: stricter SWE flow for issue localization, patching, and tests
- `langgraph.json` exposes both assistants to `langgraph dev`
- `connectors/` shows how external systems become agent tools
- `AGENTS.md` and `skills/` provide durable working instructions
- `agent.json` is a starting point for later `deepagents deploy` experiments

## Run Locally

```bash
uv sync
cp .env.example .env
uv run langgraph dev
```

Open Deep Agents UI separately:

```bash
git clone https://github.com/langchain-ai/deep-agents-ui.git
cd deep-agents-ui
yarn install
yarn dev
```

In the UI use:

- Deployment URL: `http://127.0.0.1:2024`
- Assistant ID: `openclaw` or `openclaw_swe`

## Workshop Step: Add a Connector

A connector is a small adapter that exposes an external system as LangChain
tools. The demo connector is local and keyless, so it is safe to show live:

- `connectors/demo.py` contains a fake issue tracker
- `connectors/telegram.py` contains a Telegram Bot API connector
- `CONNECTOR_TOOLS` exports issue-tracker and Telegram tools
- `agent.py` passes those tools into both Deep Agents

Try this prompt in Studio or Deep Agents UI:

```text
Use the demo issue connector. List the issues, then fetch DEMO-101 and explain
what implementation step we should do next.
```

To add a real connector, follow the same pattern:

1. Create `connectors/<name>.py`.
2. Wrap integration calls with `@tool`.
3. Export them through `CONNECTOR_TOOLS`.
4. Add credentials to `.env`, never to source files.

Telegram connector demo prompt:

```text
Use the Telegram connector in dry-run mode. Prepare a short workshop message
that says OpenClaw connectors are working.
```

To send real Telegram messages, create a bot with BotFather, get a chat id, and
set:

```bash
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

Then ask the agent to call `send_telegram_message` with `dry_run=false`.

## Shell Mode

By default, the agent does not get local shell execution. To experiment with a
Claude Code/OpenClaw-like local coding loop, set:

```bash
OPENCLAW_ENABLE_LOCAL_SHELL=1
OPENCLAW_WORKSPACE=/absolute/path/to/a/safe/test/repo
```

Only enable this in a disposable or trusted workspace. Deep Agents' local shell
backend executes commands directly on your machine.

## Useful References

- Deep Agents Python: https://github.com/langchain-ai/deepagents
- Deep Agents JS: https://github.com/langchain-ai/deepagentsjs
- Deep Agents UI: https://github.com/langchain-ai/deep-agents-ui
