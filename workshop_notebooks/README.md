# OpenClaw Workshop Notebooks

These notebooks mirror `agent_workshop_steps.py`, but each layer is isolated in a runnable Jupyter notebook.

Suggested order:

1. `01_minimal_agent.ipynb` — model + prompt + `create_deep_agent`.
2. `02_filesystem_backend.ipynb` — workspace-scoped backend and shell opt-in.
3. `03_demo_connector.ipynb` — keyless demo issue connector.
4. `04_telegram_connector.ipynb` — Telegram connector with safe dry-run.
5. `05_subagents_skills_memory.ipynb` — subagents, local skills, memory.
6. `06_swe_mode.ipynb` — stricter SWE graph with write/edit interrupts.

Run from the repository root so imports like `connectors.demo` resolve correctly.

```bash
uv sync
uv run jupyter lab workshop_notebooks
```

The notebooks are kept without outputs so diffs stay readable.
