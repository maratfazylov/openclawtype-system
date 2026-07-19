# OpenClaw Workshop Notebooks

For the concrete launch sequence, common LangGraph errors, and terminal
commands, see [`../notebook.md`](../notebook.md).

The canonical workshop path is now `openclaw_path/`: six notebooks that follow
the presentation story and then build the OpenClaw clone layer by layer.

Main order:

0. `openclaw_path/00_from_claude_code_to_openclaw.ipynb` — no-code technical
   lecture: LLM as a function, Claude Code, OpenClaw, security/operations
   problems, and the workshop promise.
1. `openclaw_path/01_core_deep_agent.ipynb` — Core: Deep Agent + LangGraph
   state, without a real workspace or external capabilities.
2. `openclaw_path/02_workspace_filesystem.ipynb` — Workspace: `_backend`,
   filesystem access, virtual paths, and workspace instructions.
3. `openclaw_path/03_jenkins_tools.ipynb` — Jenkins: DevOps capabilities as
   controlled Python tools, not shell/curl.
4. `openclaw_path/04_vk_bridge.ipynb` — VK Bridge: outbound VK tool, inbound
   channel worker, and `peer_id → thread_id` mapping.
5. `openclaw_path/05_swe_agent.ipynb` — SWE Loop: issue, research, edit,
   test, review, summary.
6. `openclaw_path/06_final_architecture.ipynb` — final architecture, primitive
   map, what exists, and what is intentionally out of scope.

Each chapter follows the same rhythm:

```text
What the agent cannot do yet
→ capability added
→ primitives involved
→ code assembly
→ LangGraph Studio check
→ new limitation
```

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
.venv/bin/python -m ipykernel install --user --name openclaw-workshop --display-name "OpenClaw Workshop (.venv)"
```

CLI fallback:

```bash
uv sync
uv run jupyter lab workshop_notebooks/openclaw_path
```

The active notebooks generate `agents/openclaw_*.py` and update
`langgraph.openclaw_path.json` as they progress. The config is cumulative:
running later stages keeps earlier graph IDs available in LangGraph Studio.

Preflight before rehearsal or live demo:

```bash
uv run python scripts/preflight_openclaw_workshop.py
```

Stage 05 needs local shell for pytest:

```bash
OPENCLAW_ENABLE_LOCAL_SHELL=1 uv run python scripts/preflight_openclaw_workshop.py
uv run python scripts/reset_swe_demo.py
```
