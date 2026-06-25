# OpenClaw Deep Agents Prototype

Minimal OpenClaw-like coding agent built on LangChain Deep Agents and compatible
with `langchain-ai/deep-agents-ui`.

## What This Is

This repo is intentionally small:

- `agent.py` defines two LangGraph assistants:
  - `openclaw`: general coding/research agent
  - `openclaw_swe`: stricter SWE flow for issue localization, patching, and tests
- `agent_workshop_steps.py` contains the same agent split into uncommentable
  workshop steps
- `workshop_notebooks/` contains the same flow as runnable Jupyter notebooks
- `langgraph.json` exposes both assistants to `langgraph dev`
- `connectors/` shows how external systems become agent tools
- `presentation/` contains a ManimGL workshop deck
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

## Workshop Step-by-Step Agent

Use `agent_workshop_steps.py` when you want to build the agent live during the
workshop instead of showing the final `agent.py` immediately.

The top of the file has uncommentable step lines:

```python
# WORKSHOP_STEP = 1  # Minimal chat/coding agent, no custom tools.
# WORKSHOP_STEP = 2  # Add workspace-scoped filesystem backend.
# WORKSHOP_STEP = 3  # Add demo issue-tracker connector.
# WORKSHOP_STEP = 4  # Add Telegram connector in safe dry-run mode.
# WORKSHOP_STEP = 5  # Add subagents, skills, and durable memory.
WORKSHOP_STEP = 6  # Final version: also expose stricter SWE mode.
```

For a live walkthrough:

1. Uncomment `WORKSHOP_STEP = 1`, restart `uv run langgraph dev`, and use
   assistant `openclaw_steps`.
2. Move to Step 2 to show workspace file access with safe filesystem tools.
3. Move to Step 3 to add the local issue-tracker connector.
4. Move to Step 4 to add Telegram as an external connector.
5. Move to Step 5 to add subagents, skills, and memory.
6. Move to Step 6 and switch to `openclaw_steps_swe` for the stricter SWE flow.

You can also switch steps without editing the file:

```bash
OPENCLAW_WORKSHOP_STEP=3 uv run langgraph dev
```

Suggested prompts:

```text
Step 2: Inspect the workspace files and summarize what this project does.
```

```text
Step 3: Use the demo issue connector. List issues, fetch DEMO-101, and propose
the next implementation step.
```

```text
Step 4: Use the Telegram connector in dry-run mode. Prepare a short workshop
message that says OpenClaw connectors are working.
```

```text
Step 6: In SWE mode, inspect the project shape test and explain what behavior
it protects.
```

## Workshop Notebooks

The same step-by-step flow also exists as Jupyter notebooks in
`workshop_notebooks/`.

For external notebook apps, open any `.ipynb` and select the kernel:

```text
OpenClaw Workshop (.venv)
```

If the kernel is not visible yet, register it once:

```bash
.venv/bin/python -m ipykernel install --user --name openclaw-workshop --display-name "OpenClaw Workshop (.venv)"
```

CLI fallback:

```bash
uv run jupyter lab workshop_notebooks
```

Use them when the workshop format is more notebook-driven than UI-driven:

- `00_full_interactive_workshop.ipynb`
- `01_minimal_agent.ipynb`
- `02_filesystem_backend.ipynb`
- `03_demo_connector.ipynb`
- `04_telegram_connector.ipynb`
- `05_subagents_skills_memory.ipynb`
- `06_swe_mode.ipynb`

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

## ManimGL Presentation

The workshop deck lives in `presentation/openclawtype_manim.py` and targets the
original 3Blue1Brown ManimGL project (`pip install manimgl`, import
`manimlib`).

Render one scene:

```bash
manimgl presentation/openclawtype_manim.py ArchitectureScene -w
```

See `presentation/README.md` for all scene names.

## Russian ManimCE Presentation

The Russian workshop presentation built with `Yusuke710/manim-skill` lives in
`openclawtype_ru_manim/`.

- `plan.md` contains the narrative plan
- `script.py` contains Manim Community Edition scenes
- `concat.txt` defines the final scene order
- `final.mp4` is the rendered presentation
- `thumbnail.png` is a quick preview frame

Render from that folder:

```bash
manim -ql script.py Scene1_Intro Scene2_Architecture Scene3_Connector Scene4_Telegram Scene5_WorkshopFlow
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy final.mp4
```

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
