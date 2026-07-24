# OpenClaw Workshop Runbook

## Перед началом

1. Если используешь OmniRoute как model gateway, запустить его отдельно и
   положить ключ endpoint в `.env`:

   ```dotenv
   OMNIROUTE_API_KEY=...
   ```

   Workshop автоматически переключится на:

   ```text
   http://127.0.0.1:20128/v1
   model=auto
   ```

2. Проверить модель, credentials и dry-run connectors:

   ```bash
   uv run python scripts/preflight_openclaw_workshop.py
   ```

3. Проверить live read-only доступ к Jenkins/VK:

   ```bash
   OPENCLAW_PREFLIGHT_LIVE=1 uv run python scripts/preflight_openclaw_workshop.py
   ```

4. Подготовить SWE-демо:

   ```bash
   uv run python scripts/reset_swe_demo.py
   uv run python scripts/preflight_openclaw_workshop.py
   ```

5. Открыть notebooks:

   ```bash
   uv run jupyter lab workshop_notebooks/openclaw_path
   ```

## Порядок live-demo

1. Выполнить notebook `01_core_deep_agent.ipynb`.
2. Выполнить notebook `02_workspace_filesystem.ipynb`.
3. Проверить, что сгенерированные graph targets существуют:

   ```bash
   OPENCLAW_PREFLIGHT_REQUIRE_GRAPHS=1 uv run python scripts/preflight_openclaw_workshop.py
   ```

4. Запустить Studio:

   ```bash
   uv run langgraph dev --config langgraph.openclaw_path.json
   ```

5. После каждого следующего notebook дождаться reload в Studio. Если graph не обновился, перезапустить `langgraph dev`.
6. На stage `04` запустить bridge во втором терминале. Bridge вызывает graph `openclaw_04_vk_bridge`:

   ```bash
   LANGGRAPH_ASSISTANT_ID=openclaw_04_vk_bridge \
   VK_BRIDGE_DRY_RUN=0 \
   VK_BRIDGE_REPLY_TO_VK=1 \
   uv run python scripts/vk_langgraph_bridge.py
   ```

7. На финале переключить bridge на финальный graph `openclaw_05_swe`:

   ```bash
   LANGGRAPH_ASSISTANT_ID=openclaw_05_swe \
   VK_BRIDGE_DRY_RUN=0 \
   VK_BRIDGE_REPLY_TO_VK=1 \
   uv run python scripts/vk_langgraph_bridge.py
   ```

## Prompts

### 01 Core

```text
Найди файл pyproject.toml и назови имя проекта и три зависимости. Если у тебя нет доступа к файлам, прямо скажи об этом.
```

### 02 Workspace

```text
Найди файл pyproject.toml и назови имя проекта и три зависимости. Не угадывай: сначала используй filesystem tools.
```

### 03 Jenkins

Read:

```text
Проверь Jenkins job и назови статус последней сборки. Используй Jenkins tools, не shell/curl/env.
```

Write:

```text
Теперь запусти smoke build с OPENCLAW_SMOKE=true. Это реальный запуск.
```

Copy:

```text
Скопируй Jenkins job test01 в папке marat в новую job test02. Это реальное действие, используй dry_run=false.
```

### 04 VK Bridge

Outbound from Studio:

```text
Отправь в VK сообщение: «OpenClaw stage 04: outbound connector работает». Это реальная отправка.
```

Inbound from VK:

```text
Коротко объясни, какие инструменты тебе доступны.
```

End-to-end from VK:

```text
Проверь последнюю Jenkins-сборку через Jenkins tools. Не используй shell, curl или env. Пришли сюда номер job, имя job и статус.
```

### 05 SWE Loop

```text
VK connector должен разбивать сообщения длиннее 3500 символов на несколько частей. Реализуй acceptance criteria из notebook и добавь unit tests без реального VK API.
```

### 06 Final

Из VK:

```text
Запусти smoke build и сообщи сюда, принял ли Jenkins запуск.
```

## Backup

- Если OmniRoute недоступен, убрать `OMNIROUTE_API_KEY` из `.env`: stages
  вернутся к OpenRouter fallback.
- Если Jenkins недоступен, показать dry-run payload и объяснить network/VPN/firewall dependency.
- Если VK send падает, показать `send_vk_message` dry-run и output preflight.
