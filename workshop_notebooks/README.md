# OpenClaw Workshop Notebooks

These notebooks mirror `agent_workshop_steps.py`, but each layer is isolated in a runnable Jupyter notebook.

Suggested order:

0. `00_full_interactive_workshop.ipynb` — one combined notebook with real OpenRouter calls and saved outputs.
1. `01_minimal_agent.ipynb` — model + prompt + `create_deep_agent`.
2. `02_filesystem_backend.ipynb` — workspace-scoped backend and shell opt-in.
3. `03_demo_connector.ipynb` — keyless demo issue connector.
4. `04_telegram_connector.ipynb` — Telegram connector with safe dry-run.
5. `05_subagents_skills_memory.ipynb` — subagents, local skills, memory.
6. `06_swe_mode.ipynb` — stricter SWE graph with write/edit interrupts.

Open any `.ipynb` in VS Code, PyCharm, JupyterLab, or another notebook app and
select the project virtual environment:

```text
Python 3 (.venv)
```

If the app asks for an interpreter path, choose:

```text
/Users/ken/work/openclaw clone/.venv/bin/python
```

Each notebook bootstraps the repository root onto `sys.path`, so imports like
`connectors.demo` work when the notebook is opened directly from this folder.

If the kernel is missing, register it once from the repository root:

```bash
.venv/bin/python -m ipykernel install --prefix .venv --name python3 --display-name "Python 3 (.venv)"
```

CLI fallback:

```bash
uv sync
uv run jupyter lab workshop_notebooks
```

`00_full_interactive_workshop.ipynb` intentionally contains saved outputs from
real OpenRouter calls. The other notebooks are smaller chapter-by-chapter
variants for live editing.
