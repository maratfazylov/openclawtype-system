# OpenClaw Workshop Runbook

## Before Starting

1. Check model and connectors:

   ```bash
   uv run python scripts/preflight_openclaw_workshop.py
   ```

2. For stage 05, verify shell and SWE demo state:

   ```bash
   OPENCLAW_ENABLE_LOCAL_SHELL=1 uv run python scripts/preflight_openclaw_workshop.py
   uv run python scripts/reset_swe_demo.py
   ```

3. Open notebooks:

   ```bash
   uv run jupyter lab workshop_notebooks/openclaw_path
   ```

4. After running stages 01-05, start LangGraph:

   ```bash
   uv run langgraph dev --config langgraph.openclaw_path.json
   ```

5. At stage 03, start the VK bridge in a second terminal:

   ```bash
   VK_BRIDGE_DRY_RUN=0 VK_BRIDGE_REPLY_TO_VK=1 uv run python scripts/vk_langgraph_bridge.py
   ```

## Stage Prompts

### 01

```text
Найди файл pyproject.toml и назови имя проекта и три зависимости. Если у тебя нет доступа к файлам, прямо скажи об этом.
```

### 02

```text
Сначала проверь Jenkins job и назови статус последней сборки. Затем запусти smoke build с параметром OPENCLAW_SMOKE=true. Это реальный запуск.
```

### 03

```text
Отправь в VK сообщение: «OpenClaw stage 03: outbound connector работает». Это реальная отправка.
```

Then from VK:

```text
Коротко объясни, какие инструменты тебе доступны.
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

From VK:

```text
Проверь последнюю сборку Jenkins и отправь сюда короткий статус с номером и результатом.
```

## Backup Notes

- Keep a backup model in `.env` and test it before the event.
- If Jenkins network fails, show dry-run payload and explain network/VPN/firewall dependency.
- If VK send fails, show `send_vk_message` dry-run and token preflight output.
