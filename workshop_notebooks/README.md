# OpenClaw Workshop Notebooks

The canonical workshop path is now `openclaw_path/`: five notebooks that follow
the presentation story and then build the OpenClaw clone layer by layer.

Main order:

0. `openclaw_path/00_openclaw_intro.ipynb` — small no-code presentation:
   OpenClaw's UX, security problems, `messages` API, LangChain → LangGraph →
   Deep Agents, and what a Deep Agent is.
1. `openclaw_path/01_minimal_and_filesystem.ipynb` — start from `messages`,
   create a minimal Deep Agent, then add filesystem backend and shell gate.
2. `openclaw_path/02_real_jenkins_connector.ipynb` — add real Jenkins:
   dry-run preview, read-only metadata, and gated build trigger.
3. `openclaw_path/03_vk_connector_and_bridge.ipynb` — add VK connector and
   explain the polling/cron bridge into LangGraph.
4. `openclaw_path/04_subagents_and_swe.ipynb` — add subagents, skills-shaped
   instructions, and a stricter SWE assistant.

Legacy/reference notebooks still live in this folder. They are useful for
isolated experiments, but they are no longer the main workshop sequence.

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
uv run jupyter lab workshop_notebooks/openclaw_path
```

The active notebooks generate `agents/openclaw_path_*.py` and update
`langgraph.openclaw_path.json` as they progress.
