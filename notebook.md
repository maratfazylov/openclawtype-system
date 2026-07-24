# Как запускать workshop notebooks

Эта инструкция для ветки `workshop_notebooks/openclaw_path`.

## 1. Подготовить окружение

Из корня репозитория:

```bash
uv sync
```

Если Jupyter не видит kernel, зарегистрировать его один раз:

```bash
.venv/bin/python -m ipykernel install --user --name openclaw-workshop --display-name "OpenClaw Workshop (.venv)"
```

Открыть notebooks:

```bash
uv run jupyter lab workshop_notebooks/openclaw_path
```

В Jupyter выбрать kernel:

```text
OpenClaw Workshop (.venv)
```

## 1.1. Модель

По умолчанию stages используют fallback:

```text
openrouter:tencent/hy3:free
```

Если хочешь прогонять workshop через OmniRoute, сначала запусти OmniRoute
отдельным процессом, затем добавь ключ в `.env`:

```dotenv
OMNIROUTE_API_KEY=...
```

После этого entrypoints автоматически используют OpenAI-compatible endpoint:

```text
http://127.0.0.1:20128/v1
model=auto
```

Проверить выбранный provider:

```bash
uv run python scripts/preflight_openclaw_workshop.py
```

## 2. Как устроен запуск

Notebooks генерируют Python entrypoints в `agents/` и регистрируют graph IDs в:

```text
langgraph.openclaw_path.json
```

Главные graph IDs:

```text
openclaw_01_core
openclaw_02_workspace
openclaw_03_jenkins
openclaw_04_vk_bridge
openclaw_05_swe
```

Config cumulative: LangGraph импортирует все graph targets из файла. Поэтому
если в config есть `openclaw_03_jenkins`, но файла
`agents/openclaw_03_jenkins_tools.py` нет, сервер упадет даже при попытке
показать только `openclaw_01_core`.

## 3. Рекомендуемый порядок

1. Открыть `00_from_claude_code_to_openclaw.ipynb`.
2. Для презентационного режима использовать RISE/JupyterLab slideshow.
3. Выполнить `01_core_deep_agent.ipynb` до ячейки, которая пишет:

   ```text
   agents/openclaw_01_core.py
   ```

4. Выполнить `02_workspace_filesystem.ipynb` до ячейки, которая пишет:

   ```text
   agents/openclaw_02_workspace.py
   ```

5. Если хочешь сразу запускать общий cumulative config, убедиться, что все
   entrypoints существуют:

   ```bash
   ls agents/openclaw_*.py
   ```

6. Запустить LangGraph:

   ```bash
   uv run langgraph dev --config langgraph.openclaw_path.json
   ```

7. Открыть Studio UI из вывода команды.

Обычно это:

```text
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

## 4. Если надо показать только stage 01

Если cumulative config еще ссылается на не созданные graph files, можно
временно запустить только `01` через отдельный минимальный config.

Создать `langgraph.01.json`:

```json
{
  "dependencies": ["."],
  "graphs": {
    "openclaw_01_core": "./agents/openclaw_01_core.py:agent"
  },
  "env": ".env"
}
```

Запустить:

```bash
uv run langgraph dev --config langgraph.01.json
```

## 5. Проверка перед LangGraph

Проверить, что graph targets существуют:

```bash
OPENCLAW_PREFLIGHT_REQUIRE_GRAPHS=1 uv run python scripts/preflight_openclaw_workshop.py
```

Проверить credentials и dry-run connectors:

```bash
uv run python scripts/preflight_openclaw_workshop.py
```

Live read-only проверка Jenkins/VK:

```bash
OPENCLAW_PREFLIGHT_LIVE=1 uv run python scripts/preflight_openclaw_workshop.py
```

## 6. Stage 05

`05_swe_agent.ipynb` использует `LocalShellBackend` прямо в graph entrypoint,
потому что этот этап должен запускать pytest.

Перед stage 05:

```bash
uv run python scripts/preflight_openclaw_workshop.py
uv run python scripts/reset_swe_demo.py
```

## 7. VK bridge

LangGraph должен быть уже запущен.

Для stage 04:

```bash
LANGGRAPH_ASSISTANT_ID=openclaw_04_vk_bridge \
VK_BRIDGE_DRY_RUN=0 \
VK_BRIDGE_REPLY_TO_VK=1 \
uv run python scripts/vk_langgraph_bridge.py
```

Для финала:

```bash
LANGGRAPH_ASSISTANT_ID=openclaw_05_swe \
VK_BRIDGE_DRY_RUN=0 \
VK_BRIDGE_REPLY_TO_VK=1 \
uv run python scripts/vk_langgraph_bridge.py
```

## 8. Частые ошибки

### `FileNotFoundError: agents/openclaw_03_jenkins_tools.py`

Причина: `langgraph.openclaw_path.json` cumulative и импортирует все graphs.

Что сделать:

```bash
ls agents/openclaw_*.py
OPENCLAW_PREFLIGHT_REQUIRE_GRAPHS=1 uv run python scripts/preflight_openclaw_workshop.py
```

Если файлов нет, выполнить соответствующие notebooks `02-05` или восстановить
entrypoints из notebook-ячейки `ENTRYPOINT`.

### Jupyter не видит kernel

```bash
.venv/bin/python -m ipykernel install --user --name openclaw-workshop --display-name "OpenClaw Workshop (.venv)"
```

После этого перезапустить JupyterLab.

### `uv` ругается на cache

Можно использовать локальный cache внутри репозитория:

```bash
UV_CACHE_DIR=.uv-cache uv run python scripts/preflight_openclaw_workshop.py
```
