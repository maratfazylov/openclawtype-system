# OpenClaw Workshop Notebooks

The canonical workshop path is now `openclaw_path/`: five notebooks that follow
the presentation story and then build the OpenClaw clone layer by layer.

Main order:

0. `openclaw_path/00_from_claude_code_to_openclaw.ipynb` — no-code technical
   lecture: LLM as a function, Claude Code, OpenClaw, security/operations
   problems, and the workshop promise.
1. `openclaw_path/01_agent_and_filesystem.ipynb` — first agent: state, tools,
   filesystem, and the contrast between no workspace and workspace access.
2. `openclaw_path/02_jenkins_tools.ipynb` — from analysis to action: Jenkins
   as a controlled Python tool contract.
3. `openclaw_path/03_vk_channel_and_bridge.ipynb` — VK as outbound capability
   and inbound transport through the polling bridge.
4. `openclaw_path/04_subagents.ipynb` — delegation: hierarchical agent with
   researcher and reviewer roles.
5. `openclaw_path/05_swe_agent.ipynb` — SWE workflow: issue, research, edit,
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
.venv/bin/python -m ipykernel install --prefix .venv --name python3 --display-name "Python 3 (.venv)"
```

CLI fallback:

```bash
uv sync
uv run jupyter lab workshop_notebooks/openclaw_path
```

The active notebooks generate `agents/openclaw_path_*.py` and update
`langgraph.openclaw_path.json` as they progress.
