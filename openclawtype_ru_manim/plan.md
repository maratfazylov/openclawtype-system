# OpenClawtype: агентная система на Deep Agents

## Overview
- **Topic**: как устроен OpenClawtype и как в него добавляются коннекторы
- **Hook**: агентная система становится понятной, когда видно её состояние и границы
- **Target Audience**: разработчики на воркшопе, знакомые с LLM tools и GitHub
- **Estimated Length**: 35-45 секунд
- **Key Insight**: новая функциональность добавляется через тонкий connector-tool слой
- **Resolution**: 480p default, можно перерендерить в 1080p
- **Aspect Ratio**: 16:9

## Narrative Arc
Сначала показываем не продуктовую обложку, а рабочую архитектуру: UI, LangGraph,
Deep Agents и инструменты. Затем приближаемся к главной идее воркшопа: коннектор
это маленький адаптер, который агент видит как tool. В конце показываем Telegram
как реальный пример внешней системы с безопасным dry-run режимом.

---

## Scene 1: Вступление
**Duration**: ~6 seconds
**Purpose**: задать тему и связать название проекта с демонстрацией

### Visual Elements
- Большой заголовок OpenClawtype
- Четыре чипа: Deep Agents, LangGraph, UI, Connectors

### Content
Появляется название и набор строительных блоков системы.

### Voiceover
- **Text**: "OpenClawtype — это маленькая агентная система, которую удобно показывать живьём."
- **Sync Points**: "строительные блоки" → появляются чипы

---

## Scene 2: Архитектура
**Duration**: ~8 seconds
**Purpose**: объяснить, где живут состояние, UI и агент

### Visual Elements
- Панели: Пользователь, UI, LangGraph, OpenClawtype
- Стрелки слева направо

### Content
Показываем основной поток: пользователь говорит с UI, UI обращается к LangGraph,
LangGraph запускает агента, агент использует tools.

### Voiceover
- **Text**: "Главная идея: всё важное проходит через видимый runtime и inspectable state."

---

## Scene 3: Добавление коннектора
**Duration**: ~8 seconds
**Purpose**: показать расширение системы без форка runtime

### Visual Elements
- Три панели: connector.py, tools=CONNECTOR_TOOLS, поведение агента
- Подпись "без форка runtime"

### Content
Показываем, что connector это код на границе внешней системы, а не отдельный
агентный фреймворк.

### Voiceover
- **Text**: "Чтобы добавить возможность, мы описываем внешний сервис как tool."

---

## Scene 4: Telegram
**Duration**: ~8 seconds
**Purpose**: показать более реальный connector с безопасным режимом

### Visual Elements
- Dry-run панель
- Telegram Bot API панель
- Реальная отправка с token/chat id

### Content
Telegram connector можно демонстрировать без токена, а потом включить реальную
отправку через переменные окружения.

### Voiceover
- **Text**: "Telegram хорош для воркшопа: dry-run показывает payload, но ничего не отправляет."

---

## Scene 5: Поток воркшопа
**Duration**: ~7 seconds
**Purpose**: закончить практическим сценарием

### Visual Elements
- Вертикальные шаги: запустить, открыть UI, спросить, добавить connector, увидеть tool calls
- Финальная фраза

### Voiceover
- **Text**: "Демо становится архитектурой: мы меняем код, перезапускаем, и видим новый tool в агенте."

---

## Transitions & Flow
Сцены используют один тёмный фон и цветные панели. Переходы простые: появление,
стрелки, акцентные подписи.

## Shared Elements
- Цветовые роли: синий для runtime, зелёный для агента, жёлтый для connector
- Панели с тонкой рамкой и короткими bullet-like строками

## Color Palette
- Primary: cyan - UI и tool boundary
- Secondary: green - агент и безопасный путь
- Accent: yellow - connector/ключевой шаг
- Background: почти чёрный с холодным оттенком
