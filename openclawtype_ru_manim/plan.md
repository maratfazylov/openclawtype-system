# Deep Agents Workshop — СберХаб Петербург

## Overview
- **Topic**: практический воркшоп по deep agents на LangGraph
- **Hook**: агент не просто отвечает, а планирует, управляет браузером и останавливается перед опасным действием
- **Target Audience**: разработчики и data/AI engineers, которым нужен production-паттерн агентных систем
- **Estimated Length**: 40-50 секунд для презентационного ролика
- **Key Insight**: Deep Agent = LLM + Tools + State + Loop + Human checkpoint
- **Resolution**: 480p default
- **Aspect Ratio**: 16:9

## Narrative Arc
Ролик начинает с события и обещания: живой browser-controlling агент вместо tutorial-кода.
Затем объясняет, зачем нужны deep agents, показывает архитектуру демо-агента,
раскладывает часовую программу и заканчивает конкретными артефактами, которые участники унесут.

---

## Scene 1: Обложка
**Duration**: ~7 seconds
**Purpose**: представить воркшоп, спикера, формат и стек

### Visual Elements
- Большой заголовок "Deep Agents Workshop"
- Подзаголовок "СберХаб Петербург"
- Чипы: Demo, Code, 60 минут, LangGraph, Playwright, OpenRouter, LangSmith

### Voiceover
- **Text**: "Deep Agents Workshop в СберХабе: живое демо, разбор кода и четыре кукбука."

---

## Scene 2: Зачем deep agents
**Duration**: ~8 seconds
**Purpose**: показать эволюцию от RAG к deep agent

### Visual Elements
- Три уровня: Чатбот/RAG, Tool-calling агент, Deep Agent
- Формула: LLM + Tools + State + Loop + Human checkpoint

### Voiceover
- **Text**: "Чатбот отвечает, tool-calling вызывает API, deep agent итерирует и сам ведёт задачу через состояние."

---

## Scene 3: Архитектура демо-агента
**Duration**: ~10 seconds
**Purpose**: визуализировать State → LLM node → Tools → loop и HITL

### Visual Elements
- Панели STATE, LLM NODE, TOOLS
- Стрелки между ними и loop-back
- Красный HITL checkpoint на save_report

### Voiceover
- **Text**: "LangGraph хранит state, модель планирует и вызывает tools, а перед записью срабатывает human checkpoint."

---

## Scene 4: Живое демо
**Duration**: ~9 seconds
**Purpose**: показать три сценария демо

### Visual Elements
- Три карточки: успех, human-in-the-loop, ошибка → trace
- Подписи: cbr.ru, email/рассылка, несуществующий сайт

### Voiceover
- **Text**: "В демо будут успех, остановка перед опасным действием и ошибка, которую разбираем в LangSmith."

---

## Scene 5: Кукбуки и observability
**Duration**: ~9 seconds
**Purpose**: показать 4 notebooks и LangSmith workflow

### Visual Elements
- Четыре notebook-карточки
- Правая панель LangSmith: nodes, tool calls, token cost, latency

### Voiceover
- **Text**: "Участники получают четыре Jupyter кукбука и видят, как читать trace реального запуска."

---

## Scene 6: Что участники унесут
**Duration**: ~7 seconds
**Purpose**: закончить ценностью воркшопа

### Visual Elements
- Список outcomes
- Финальная строка "Готов к подтверждению участия"

### Voiceover
- **Text**: "На выходе — рабочие кукбуки, ментальная модель, HITL, checkpointing, LangSmith и шаблон агента."

---

## Transitions & Flow
Фон тёмный, карточки с тонкой рамкой. Синий — runtime и orchestration, зелёный — agent loop,
жёлтый — ключевые артефакты, красный — safety/HITL.

## Shared Elements
- Панели с короткими тезисами, чтобы текст читался на экране
- Повторяющаяся формула deep agent как визуальный якорь
- Стрелки и loop как главный мотив

## Color Palette
- Primary: cyan - UI/tools
- Secondary: green - agent loop
- Accent: yellow - кукбуки и takeaway
- Safety: red - HITL
- Background: deep navy
