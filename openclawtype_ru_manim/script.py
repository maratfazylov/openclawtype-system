from manim import *


BG = "#0B1020"
INK = "#E8EEF8"
MUTED = "#A9B4C8"
CYAN = "#45D0FF"
GREEN = "#49D17D"
YELLOW = "#FFD166"
RED = "#FF6B6B"
PURPLE = "#B084F5"
BLUE = "#3A86FF"


def title(text: str, subtitle: str | None = None, size: int = 42) -> VGroup:
    head = Text(text, font="Arial", font_size=size, weight=BOLD, color=INK)
    if not subtitle:
        return VGroup(head)
    sub = Text(subtitle, font="Arial", font_size=21, color=MUTED)
    return VGroup(head, sub).arrange(DOWN, buff=0.22)


def chip(text: str, color: str = CYAN, width: float = 2.4) -> VGroup:
    box = RoundedRectangle(width=width, height=0.52, corner_radius=0.08)
    box.set_stroke(color, 2)
    box.set_fill(color, opacity=0.13)
    label = Text(text, font="Arial", font_size=18, color=INK).move_to(box)
    return VGroup(box, label)


def panel(label: str, lines: list[str], color: str = CYAN, width: float = 3.15, height: float = 2.1) -> VGroup:
    box = RoundedRectangle(width=width, height=height, corner_radius=0.12)
    box.set_stroke(color, 2)
    box.set_fill(color, opacity=0.11)
    head = Text(label, font="Arial", font_size=22, weight=BOLD, color=color)
    body = VGroup(*[Text(line, font="Arial", font_size=15.5, color=INK) for line in lines])
    body.arrange(DOWN, aligned_edge=LEFT, buff=0.09)
    content = VGroup(head, body).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
    content.move_to(box)
    return VGroup(box, content)


def fit_to_width(mob: Mobject, width: float = 12.35) -> Mobject:
    if mob.width > width:
        mob.set(width=width)
    return mob


def arrow_between(left: Mobject, right: Mobject, color: str = CYAN) -> Arrow:
    return Arrow(left.get_right(), right.get_left(), buff=0.12, color=color, stroke_width=4)


class DeckScene(Scene):
    def setup(self):
        self.camera.background_color = BG

    def show_header(self, text: str, subtitle: str | None = None) -> VGroup:
        header = title(text, subtitle, size=34).to_edge(UP, buff=0.35)
        self.play(FadeIn(header, shift=DOWN))
        return header


class Scene1_Intro(DeckScene):
    def construct(self):
        self.add_subcaption(
            "Deep Agents Workshop в СберХабе: живое демо, разбор кода и четыре кукбука.",
            duration=4,
        )
        header = title("Deep Agents Workshop", "СберХаб Петербург · демо + разбор кода", size=44)
        self.play(Write(header[0]), FadeIn(header[1], shift=UP))

        meta = VGroup(
            chip("60 минут", YELLOW, width=2.0),
            chip("Спикер: Ник", PURPLE, width=2.35),
            chip("Data Engineer / AI Developer", GREEN, width=4.1),
        ).arrange(RIGHT, buff=0.2)
        meta.next_to(header, DOWN, buff=0.6)

        stack = VGroup(
            chip("LangGraph", BLUE, width=2.1),
            chip("Playwright", CYAN, width=2.1),
            chip("OpenRouter", GREEN, width=2.25),
            chip("LangSmith", YELLOW, width=2.15),
        ).arrange(RIGHT, buff=0.2)
        stack.next_to(meta, DOWN, buff=0.25)

        self.play(LaggedStart(*[FadeIn(c, shift=UP) for c in meta], lag_ratio=0.08))
        self.add_subcaption("Стек: LangGraph, Playwright, OpenRouter и LangSmith.", duration=3)
        self.play(LaggedStart(*[FadeIn(c, shift=UP) for c in stack], lag_ratio=0.08))
        self.wait(0.7)


class Scene2_WhyDeepAgents(DeckScene):
    def construct(self):
        self.show_header("Зачем deep agents", "от ответа к действию и циклу")

        rag = panel("Чатбот / RAG", ["отвечает", "читает базу", "не действует"], PURPLE, width=3.05)
        tool = panel("Tool-calling", ["вызывает API", "пишет в БД", "нет длинного цикла"], CYAN, width=3.25)
        deep = panel("Deep Agent", ["планирует", "итерирует", "управляет браузером"], GREEN, width=3.35)
        row = VGroup(rag, tool, deep).arrange(RIGHT, buff=0.45).shift(DOWN * 0.1)
        fit_to_width(row)

        self.add_subcaption(
            "Чатбот отвечает, tool-calling вызывает API, deep agent ведёт задачу через состояние.",
            duration=5,
        )
        self.play(FadeIn(rag, shift=LEFT))
        self.play(Create(arrow_between(rag, tool, MUTED)), FadeIn(tool, shift=UP))
        self.play(Create(arrow_between(tool, deep, MUTED)), FadeIn(deep, shift=RIGHT))

        formula = Text("Deep Agent = LLM + Tools + State + Loop + Human checkpoint", font="Arial", font_size=24, color=YELLOW)
        formula.next_to(row, DOWN, buff=0.45)
        self.add_subcaption("Ключевая формула: LLM, инструменты, состояние, цикл и human checkpoint.", duration=3)
        self.play(Write(formula))
        self.wait(0.7)


class Scene3_AgentArchitecture(DeckScene):
    def construct(self):
        self.show_header("Архитектура демо-агента", "State → LLM node → Tools → loop")

        state = panel("STATE", ["messages", "plan", "pending_action", "browser_context", "result"], BLUE, width=3.15, height=2.55)
        llm = panel("LLM NODE", ["OpenRouter", "plan → tool_calls", "response"], GREEN, width=3.25, height=2.55)
        tools = panel("TOOLS", ["browser_navigate", "browser_click", "browser_read_page", "bash(readonly)", "save_report ⚠"], CYAN, width=3.45, height=2.55)
        row = VGroup(state, llm, tools).arrange(RIGHT, buff=0.62).shift(DOWN * 0.05)
        fit_to_width(row)

        self.add_subcaption(
            "LangGraph хранит state, модель планирует, tools выполняют действие.",
            duration=4,
        )
        self.play(FadeIn(state, shift=LEFT))
        self.play(Create(arrow_between(state, llm, BLUE)), FadeIn(llm, shift=UP))
        self.play(Create(arrow_between(llm, tools, GREEN)), FadeIn(tools, shift=RIGHT))

        loop = CurvedArrow(tools.get_bottom() + LEFT * 0.25, state.get_bottom() + RIGHT * 0.25, angle=-TAU / 4, color=YELLOW)
        hitl = Text("interrupt_before=['save_report'] → ждём [y/n]", font="Arial", font_size=21, color=RED)
        hitl.next_to(row, DOWN, buff=0.45)
        self.add_subcaption("Перед записью отчёта агент останавливается и ждёт подтверждение человека.", duration=4)
        self.play(Create(loop), Write(hitl))
        self.wait(0.8)


class Scene4_LiveDemo(DeckScene):
    def construct(self):
        self.show_header("Живое демо агента", "три сценария подряд")

        success = panel("1. Успех", ["cbr.ru", "ключевая ставка", "отчёт после OK"], GREEN, width=3.35)
        hitl = panel("2. HITL", ["email директора", "рассылка", "стоп перед действием"], RED, width=3.35)
        error = panel("3. Ошибка", ["несуществующий сайт", "retry", "structured error"], YELLOW, width=3.35)
        row = VGroup(success, hitl, error).arrange(RIGHT, buff=0.45).shift(DOWN * 0.05)
        fit_to_width(row)

        self.add_subcaption(
            "В демо будут успех, human-in-the-loop и ошибка с разбором trace.",
            duration=5,
        )
        self.play(LaggedStart(*[FadeIn(card, shift=UP) for card in row], lag_ratio=0.15))

        bottom = VGroup(
            chip("streaming токенов", CYAN, width=2.65),
            chip("браузер на экране", BLUE, width=2.8),
            chip("итоговый файл", GREEN, width=2.35),
            chip("LangSmith trace", YELLOW, width=2.75),
        ).arrange(RIGHT, buff=0.18)
        bottom.next_to(row, DOWN, buff=0.45)
        self.add_subcaption("Показываем терминал, браузер, файл и trace запуска.", duration=3)
        self.play(LaggedStart(*[FadeIn(c, shift=UP) for c in bottom], lag_ratio=0.08))
        self.wait(0.7)


class Scene5_CookbooksObservability(DeckScene):
    def construct(self):
        self.show_header("Кукбуки и observability", "код можно забрать и запустить")

        books = VGroup(
            chip("01 graph basics", BLUE, width=3.0),
            chip("02 browser agent", CYAN, width=3.1),
            chip("03 HITL safety", RED, width=2.9),
            chip("04 observability", YELLOW, width=3.2),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        books.shift(LEFT * 3.05 + DOWN * 0.05)

        smith = panel("LangSmith trace", ["путь по нодам", "tool calls", "token cost", "latency", "ошибки tools"], GREEN, width=4.1, height=2.9)
        smith.shift(RIGHT * 2.55 + DOWN * 0.05)

        self.add_subcaption(
            "Участники получают четыре Jupyter кукбука и учатся читать trace реального запуска.",
            duration=5,
        )
        self.play(LaggedStart(*[FadeIn(b, shift=RIGHT) for b in books], lag_ratio=0.1))
        self.play(FadeIn(smith, shift=LEFT))

        line = Text("Не построчное чтение, а разбор production-паттернов", font="Arial", font_size=22, color=YELLOW)
        line.next_to(VGroup(books, smith), DOWN, buff=0.42)
        self.add_subcaption("Фокус — conditional edges, checkpointer и interrupt.", duration=3)
        self.play(Write(line))
        self.wait(0.7)


class Scene6_Takeaways(DeckScene):
    def construct(self):
        self.show_header("Что участники унесут", "готово к подтверждению участия")

        left = VGroup(
            chip("4 рабочих кукбука", YELLOW, width=3.25),
            chip("ментальная модель", CYAN, width=3.25),
            chip("HITL + checkpointing", RED, width=3.45),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        right = VGroup(
            chip("LangSmith workflow", GREEN, width=3.35),
            chip("structured errors", PURPLE, width=3.15),
            chip("шаблон browser agent", BLUE, width=3.65),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        grid = VGroup(left, right).arrange(RIGHT, buff=0.7).shift(DOWN * 0.05)
        fit_to_width(grid)

        self.add_subcaption(
            "На выходе — кукбуки, production-паттерны, LangSmith workflow и шаблон агента.",
            duration=5,
        )
        self.play(LaggedStart(*[FadeIn(item, shift=UP) for item in [*left, *right]], lag_ratio=0.08))

        closing = Text("Deep Agents Workshop · СберХаб Петербург", font="Arial", font_size=27, weight=BOLD, color=INK)
        closing.next_to(grid, DOWN, buff=0.5)
        self.add_subcaption("Готов к подтверждению участия.", duration=2)
        self.play(Write(closing))
        self.wait(0.8)
