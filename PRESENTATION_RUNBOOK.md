# OpenClaw Presentation Runbook

## One-Sentence Positioning

OpenClaw is a small LangGraph/Deep Agents prototype that shows how a coding
agent can be assembled from a model, guarded workspace tools, domain-specific
instructions, subagents, and external-system connectors.

## What To Present

Do not present this as a finished autonomous IDE. Present it as a working
architecture prototype and workshop kit:

- the agent can be served through `langgraph dev`;
- Deep Agents UI can connect to assistants from `langgraph.json`;
- safe dry-run connectors work without credentials;
- real Telegram, Jenkins, and VK actions require environment variables;
- shell execution is intentionally disabled unless explicitly enabled.

## Demo Path

### 1. Start With The Shape

Show these files first:

- `agent.py` - final agent and SWE-mode assistant;
- `agent_workshop_steps.py` - same agent built in workshop-sized layers;
- `connectors/` - external systems exposed as LangChain tools;
- `skills/` and `AGENTS.md` - durable behavior and project instructions;
- `tests/test_project_shape.py` - regression checks for the prototype shape.

Message to say:

> This is intentionally small. The point is not a giant app; the point is the
> composition pattern for an engineering agent.

### 2. Show The Safe Connector Demo

Use assistant `openclaw` or `openclaw_steps` and prompt:

```text
Use the demo issue connector. List the issues, then fetch DEMO-101 and explain
what implementation step we should do next.
```

This should work without external credentials.

### 3. Show Dry-Run External Actions

Use Telegram or VK in dry-run mode:

```text
Use the Telegram connector in dry-run mode. Prepare a short workshop message
that says OpenClaw connectors are working.
```

```text
Use the VK connector in dry-run mode. Prepare a message payload for peer_id 123
that says OpenClaw VK connector is configured.
```

The point is to show the request payload and guardrails before real mutation.

### 4. Show SWE Mode

Switch to assistant `openclaw_swe` or `openclaw_steps_swe` and prompt:

```text
Inspect the project tests and explain what behavior they protect. Then suggest
one useful regression test for the connector layer.
```

Message to say:

> SWE mode is the same base agent with stricter instructions and additional
> write/edit interrupts.

### 5. Optional Real Jenkins Smoke

Only do this when credentials are configured and a real build is acceptable:

```text
Use the Jenkins connector. Check the configured job info, then trigger a real
smoke build for the marat job with OPENCLAW_SMOKE=true.
```

If you do not want a real build, force dry-run:

```text
Use the Jenkins connector in dry-run mode with parameter OPENCLAW_SMOKE=true.
Show me the request that would be sent.
```

## What Works Without Secrets

- importing both LangGraph assistants;
- project shape tests;
- demo issue connector;
- Telegram dry-run send payload;
- VK dry-run API/message payload;
- Jenkins dry-run trigger payload.

## What Requires Secrets Or Network

- model calls through OpenRouter/OpenAI/Anthropic;
- reading Telegram updates;
- sending real Telegram messages;
- calling real VK methods;
- reading Jenkins job metadata;
- triggering a real Jenkins build.

## Known Prototype Boundaries

- The repo does not contain a custom frontend; it expects Deep Agents UI.
- The workshop `.env` stores keys and credentials only; backend choices are
  fixed in the stage entrypoints.
- Connectors are intentionally thin examples, not full production integrations.
- The project demonstrates orchestration and guardrails more than benchmarked
  coding performance.

## Fast Local Verification

```bash
uv run pytest
OPENAI_API_KEY=dummy uv run python -c 'import agent; print(type(agent.agent).__name__); print(type(agent.swe_agent).__name__)'
```

Expected result:

- tests pass;
- both assistants import as compiled LangGraph graphs.
