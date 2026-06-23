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


def title(text: str, subtitle: str | None = None) -> VGroup:
    head = Text(text, font="Arial", font_size=44, weight=BOLD, color=INK)
    if not subtitle:
        return VGroup(head)
    sub = Text(subtitle, font="Arial", font_size=22, color=MUTED)
    return VGroup(head, sub).arrange(DOWN, buff=0.22)


def chip(text: str, color: str = CYAN, width: float = 2.7) -> VGroup:
    box = RoundedRectangle(width=width, height=0.58, corner_radius=0.09)
    box.set_stroke(color, 2)
    box.set_fill(color, opacity=0.13)
    label = Text(text, font="Arial", font_size=20, color=INK).move_to(box)
    return VGroup(box, label)


def panel(label: str, lines: list[str], color: str = CYAN, width: float = 3.0) -> VGroup:
    box = RoundedRectangle(width=width, height=2.25, corner_radius=0.12)
    box.set_stroke(color, 2)
    box.set_fill(color, opacity=0.11)
    head = Text(label, font="Arial", font_size=23, weight=BOLD, color=color)
    body = VGroup(*[Text(line, font="Arial", font_size=17, color=INK) for line in lines])
    body.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    content = VGroup(head, body).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    content.move_to(box)
    return VGroup(box, content)


def fit_to_width(mob: Mobject, width: float = 12.2) -> Mobject:
    if mob.width > width:
        mob.set(width=width)
    return mob


def arrow_between(left: Mobject, right: Mobject, color: str = CYAN) -> Arrow:
    return Arrow(left.get_right(), right.get_left(), buff=0.14, color=color, stroke_width=4)


class DeckScene(Scene):
    def setup(self):
        self.camera.background_color = BG

    def show_header(self, text: str, subtitle: str | None = None) -> VGroup:
        header = title(text, subtitle).to_edge(UP, buff=0.45)
        self.play(FadeIn(header, shift=DOWN))
        return header


class Scene1_Intro(DeckScene):
    def construct(self):
        self.add_subcaption(
            "OpenClawtype — маленькая агентная система для живого воркшопа.",
            duration=3,
        )
        header = title("OpenClawtype", "Deep Agents, UI и коннекторы в одном демо")
        self.play(Write(header[0]), FadeIn(header[1], shift=UP))

        chips = VGroup(
            chip("Deep Agents", GREEN),
            chip("LangGraph", BLUE),
            chip("UI", CYAN, width=1.45),
            chip("Connectors", YELLOW),
        ).arrange(RIGHT, buff=0.22)
        chips.next_to(header, DOWN, buff=0.75)
        self.add_subcaption("Система собирается из нескольких понятных блоков.", duration=3)
        self.play(LaggedStart(*[FadeIn(c, shift=UP) for c in chips], lag_ratio=0.12))
        self.wait(0.8)


class Scene2_Architecture(DeckScene):
    def construct(self):
        self.show_header("Форма системы", "UI, runtime, агент и видимое состояние")

        user = panel("Пользователь", ["ставит задачу", "проверяет ответ"], PURPLE, width=2.75)
        ui = panel("Deep Agents UI", ["чат", "файлы", "tool calls"], CYAN, width=3.0)
        graph = panel("LangGraph", ["threads", "runs", "state"], BLUE, width=2.75)
        agent = panel("OpenClawtype", ["skills", "subagents", "tools"], GREEN, width=3.0)
        row = VGroup(user, ui, graph, agent).arrange(RIGHT, buff=0.36).shift(DOWN * 0.15)
        fit_to_width(row)
        arrows = VGroup(
            arrow_between(user, ui, PURPLE),
            arrow_between(ui, graph, CYAN),
            arrow_between(graph, agent, BLUE),
        )

        self.add_subcaption("Пользователь работает через UI, а LangGraph хранит ход выполнения.", duration=4)
        self.play(LaggedStart(*[FadeIn(p, shift=UP) for p in row], lag_ratio=0.12))
        self.play(LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.18))

        note = Text("Главное: состояние можно увидеть и обсудить", font="Arial", font_size=25, color=YELLOW)
        note.next_to(row, DOWN, buff=0.45)
        self.add_subcaption("Это удобно для воркшопа: мы видим не только ответ, но и процесс.", duration=3)
        self.play(Write(note))
        self.wait(0.8)


class Scene3_Connector(DeckScene):
    def construct(self):
        self.show_header("Как добавляется функциональность", "коннектор становится tool")

        source = panel(
            "connector.py",
            ["@tool", "вызов API", "нормальный payload"],
            YELLOW,
            width=3.35,
        )
        wiring = panel(
            "agent.py",
            ["tools=CONNECTOR_TOOLS", "без форка runtime", "без новой магии"],
            GREEN,
            width=3.55,
        )
        result = panel(
            "Агент",
            ["видит tool", "выбирает действие", "пишет результат"],
            CYAN,
            width=3.35,
        )
        row = VGroup(source, wiring, result).arrange(RIGHT, buff=0.45).shift(DOWN * 0.1)
        fit_to_width(row)

        self.add_subcaption("Коннектор — это тонкая граница между агентом и внешней системой.", duration=4)
        self.play(FadeIn(source, shift=LEFT))
        self.play(Create(arrow_between(source, wiring, YELLOW)), FadeIn(wiring, shift=UP))
        self.play(Create(arrow_between(wiring, result, GREEN)), FadeIn(result, shift=RIGHT))

        note = Text("Новая возможность = новый tool", font="Arial", font_size=28, color=INK)
        note.next_to(row, DOWN, buff=0.45)
        self.add_subcaption("Так мы расширяем систему маленькими шагами.", duration=3)
        self.play(Write(note))
        self.wait(0.8)


class Scene4_Telegram(DeckScene):
    def construct(self):
        self.show_header("Telegram connector", "реальный API, безопасный dry-run")

        dry = panel("dry_run=True", ["готовим payload", "ничего не отправляем", "токен не нужен"], GREEN)
        api = panel("Bot API", ["sendMessage", "getUpdates", "обычный HTTP"], CYAN)
        real = panel("dry_run=False", ["BOT_TOKEN", "CHAT_ID", "реальная отправка"], RED)
        row = VGroup(dry, api, real).arrange(RIGHT, buff=0.5).shift(DOWN * 0.05)
        fit_to_width(row)

        self.add_subcaption("Для демо Telegram можно показать без отправки сообщений.", duration=4)
        self.play(LaggedStart(*[FadeIn(p, shift=UP) for p in row], lag_ratio=0.12))
        self.play(Create(arrow_between(dry, api, GREEN)), Create(arrow_between(api, real, CYAN)))

        prompt = Text(
            "Промпт: подготовь сообщение в Telegram в dry-run режиме",
            font="Arial",
            font_size=23,
            color=YELLOW,
        )
        prompt.next_to(row, DOWN, buff=0.45)
        self.add_subcaption("А потом можно включить настоящий токен и отправить сообщение.", duration=3)
        self.play(Write(prompt))
        self.wait(0.8)


class Scene5_WorkshopFlow(DeckScene):
    def construct(self):
        self.show_header("Сценарий воркшопа", "собрали, запустили, расширили")

        steps = VGroup(
            chip("1. Запустить LangGraph", BLUE, width=3.4),
            chip("2. Открыть UI", CYAN, width=2.4),
            chip("3. Спросить агента", GREEN, width=3.0),
            chip("4. Добавить connector", YELLOW, width=3.25),
            chip("5. Увидеть tool calls", PURPLE, width=3.2),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        steps.move_to(ORIGIN).shift(LEFT * 0.15)

        self.add_subcaption("Воркшоп устроен как цикл: меняем код и сразу видим поведение.", duration=4)
        for step in steps:
            self.play(FadeIn(step, shift=RIGHT), run_time=0.32)

        box = SurroundingRectangle(steps, buff=0.28, color=CYAN, stroke_width=2)
        self.play(Create(box))

        closing = Text("Демо и есть архитектура", font="Arial", font_size=30, weight=BOLD, color=INK)
        closing.next_to(box, DOWN, buff=0.4)
        self.add_subcaption("Демо и есть архитектура.", duration=2)
        self.play(Write(closing))
        self.wait(0.9)
