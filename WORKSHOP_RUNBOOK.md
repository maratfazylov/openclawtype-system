# OpenClaw Workshop Runbook

## Перед началом

1. Проверить модель, credentials и dry-run connectors:

   ```bash
   uv run python scripts/preflight_openclaw_workshop.py
   ```

2. Проверить live read-only доступ к Jenkins/VK:

   ```bash
   OPENCLAW_PREFLIGHT_LIVE=1 uv run python scripts/preflight_openclaw_workshop.py
   ```

3. Подготовить SWE-демо:

   ```bash
   uv run python scripts/reset_swe_demo.py
   OPENCLAW_ENABLE_LOCAL_SHELL=1 uv run python scripts/preflight_openclaw_workshop.py
   ```

4. Открыть notebooks:

   ```bash
   uv run jupyter lab workshop_notebooks/openclaw_path
   ```

## Порядок live-demo

1. Выполнить notebook `01`.
2. Проверить, что сгенерированные graph targets существуют:

   ```bash
   OPENCLAW_PREFLIGHT_REQUIRE_GRAPHS=1 uv run python scripts/preflight_openclaw_workshop.py
   ```

3. Запустить Studio:

   ```bash
   uv run langgraph dev --config langgraph.openclaw_path.json
   ```

4. После каждого следующего notebook дождаться reload в Studio. Если graph не обновился, перезапустить `langgraph dev`.
5. На stage `03` запустить bridge во втором терминале. Bridge вызывает graph `openclaw_03`:

   ```bash
   LANGGRAPH_ASSISTANT_ID=openclaw_03 \
   VK_BRIDGE_DRY_RUN=0 \
   VK_BRIDGE_REPLY_TO_VK=1 \
   uv run python scripts/vk_langgraph_bridge.py
   ```

6. На финале переключить bridge на финальный graph `openclaw_05_swe`:

   ```bash
   LANGGRAPH_ASSISTANT_ID=openclaw_05_swe \
   VK_BRIDGE_DRY_RUN=0 \
   VK_BRIDGE_REPLY_TO_VK=1 \
   uv run python scripts/vk_langgraph_bridge.py
   ```

## Prompts

### 01

```text
Найди файл pyproject.toml и назови имя проекта и три зависимости. Если у тебя нет доступа к файлам, прямо скажи об этом.
```

### 02

Read:

```text
Проверь Jenkins job и назови статус последней сборки.
```

Write:

```text
Теперь запусти smoke build с OPENCLAW_SMOKE=true. Это реальный запуск.
```

### 03

Outbound from Studio:

```text
Отправь в VK сообщение: «OpenClaw stage 03: outbound connector работает». Это реальная отправка.
```

Inbound from VK:

```text
Коротко объясни, какие инструменты тебе доступны.
```

End-to-end from VK:

```text
Проверь последнюю Jenkins-сборку и пришли сюда номер и статус.
```

### 04

```text
Поручи repo-researcher проследить два потока: 1) Jenkins trigger от tool call до HTTP request; 2) VK message от Long Poll до LangGraph и обратно. Для каждого укажи конкретные файлы и точки отказа. Затем попроси analysis-reviewer проверить фактическую точность отчёта.
```

### 05

```text
VK connector должен разбивать сообщения длиннее 3500 символов на несколько частей. Реализуй acceptance criteria из notebook и добавь unit tests без реального VK API.
```

### 06

Из VK:

```text
Запусти smoke build и сообщи сюда, принял ли Jenkins запуск.
```

## Backup

- Держать backup model в `.env`.
- Если Jenkins недоступен, показать dry-run payload и объяснить network/VPN/firewall dependency.
- Если VK send падает, показать `send_vk_message` dry-run и output preflight.
