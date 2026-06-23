"""Animated workshop presentation for OpenClawtype.

Run with 3b1b ManimGL:

    manimgl presentation/openclawtype_manim.py TitleScene -w

The script intentionally avoids LaTeX so the presentation is easier to render
on workshop machines.
"""

from manimlib import *


BG = "#0B1020"
INK = "#E8EEF8"
MUTED = "#9AA7BD"
CYAN = "#45D0FF"
GREEN = "#49D17D"
YELLOW = "#FFD166"
RED = "#FF6B6B"
PURPLE = "#B084F5"
BLUE = "#3A86FF"


def title(text, subtitle=None):
    group = VGroup()
    head = Text(text, font="Arial", font_size=58, weight=BOLD)
    head.set_color(INK)
    group.add(head)
    if subtitle:
        sub = Text(subtitle, font="Arial", font_size=26)
        sub.set_color(MUTED)
        sub.next_to(head, DOWN, buff=0.35)
        group.add(sub)
    group.arrange(DOWN, buff=0.35)
    return group


def chip(text, color=CYAN, width=3.2):
    box = RoundedRectangle(width=width, height=0.72, corner_radius=0.12)
    box.set_stroke(color, 2)
    box.set_fill(color, opacity=0.12)
    label = Text(text, font="Arial", font_size=24)
    label.set_color(INK)
    label.move_to(box)
    return VGroup(box, label)


def panel(label, lines, color=CYAN, width=4.25, height=2.6):
    box = RoundedRectangle(width=width, height=height, corner_radius=0.16)
    box.set_stroke(color, 2)
    box.set_fill(color, opacity=0.1)

    head = Text(label, font="Arial", font_size=27, weight=BOLD)
    head.set_color(color)
    body = VGroup(*[Text(line, font="Arial", font_size=20).set_color(INK) for line in lines])
    body.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
    content = VGroup(head, body).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
    content.move_to(box).shift(0.1 * DOWN)
    return VGroup(box, content)


def arrow_between(left, right, color=CYAN):
    arrow = Arrow(left.get_right(), right.get_left(), buff=0.18)
    arrow.set_color(color)
    arrow.set_stroke(width=4)
    return arrow


def fit_to_frame(mob, max_width=13.1):
    if mob.get_width() > max_width:
        mob.set_width(max_width)
    return mob


class DeckScene(Scene):
    def setup(self):
        self.camera.background_color = BG

    def show_title(self, text, subtitle=None):
        mob = title(text, subtitle)
        self.play(Write(mob[0]), FadeIn(mob[1:], UP) if len(mob) > 1 else Wait(0))
        self.wait(0.8)
        return mob


class TitleScene(DeckScene):
    def construct(self):
        t = self.show_title(
            "OpenClawtype",
            "Deep Agents + connectors + live workshop loop",
        )
        stack = VGroup(
            chip("LangGraph runtime", BLUE),
            chip("Deep Agents harness", GREEN),
            chip("Deep Agents UI", CYAN),
            chip("Connectors", YELLOW),
        )
        stack.arrange(RIGHT, buff=0.22)
        stack.next_to(t, DOWN, buff=1.05)
        self.play(LaggedStartMap(FadeIn, stack, shift=UP, lag_ratio=0.12))
        self.wait(1.2)


class ArchitectureScene(DeckScene):
    def construct(self):
        header = title("The shape of the system", "Small pieces, visible state, swappable edges")
        header.to_edge(UP)
        self.play(FadeIn(header, DOWN))

        user = panel("User", ["asks for work", "reviews output"], PURPLE, width=3.2)
        ui = panel("Deep Agents UI", ["chat", "files", "tool calls"], CYAN, width=3.6)
        graph = panel("LangGraph", ["threads", "runs", "state"], BLUE, width=3.5)
        agent = panel("OpenClawtype", ["skills", "subagents", "tools"], GREEN, width=3.7)

        row = VGroup(user, ui, graph, agent).arrange(RIGHT, buff=0.42)
        fit_to_frame(row)
        row.shift(0.25 * DOWN)
        arrows = VGroup(
            arrow_between(user, ui, PURPLE),
            arrow_between(ui, graph, CYAN),
            arrow_between(graph, agent, BLUE),
        )

        self.play(LaggedStartMap(FadeIn, row, shift=UP, lag_ratio=0.15))
        self.play(LaggedStartMap(ShowCreation, arrows, lag_ratio=0.2))

        state = Text("Everything important becomes inspectable state", font="Arial", font_size=30)
        state.set_color(YELLOW)
        state.next_to(row, DOWN, buff=0.75)
        self.play(Write(state))
        self.wait(1.2)


class ConnectorStepScene(DeckScene):
    def construct(self):
        header = title("Adding functionality", "A connector is just a tool boundary")
        header.to_edge(UP)
        self.play(FadeIn(header, DOWN))

        code = panel(
            "connectors/demo.py",
            [
                "@tool list_demo_issues",
                "@tool get_demo_issue",
                "CONNECTOR_TOOLS = [...]",
            ],
            YELLOW,
            width=4.8,
            height=2.7,
        )
        agent = panel(
            "agent.py",
            [
                "tools=CONNECTOR_TOOLS",
                "skills=[...]",
                "subagents=[...]",
            ],
            GREEN,
            width=4.3,
            height=2.7,
        )
        behavior = panel(
            "Agent behavior",
            [
                "can list issues",
                "can fetch details",
                "can plan next step",
            ],
            CYAN,
            width=4.2,
            height=2.7,
        )
        row = VGroup(code, agent, behavior).arrange(RIGHT, buff=0.5)
        fit_to_frame(row)
        row.shift(0.1 * DOWN)
        arrows = VGroup(arrow_between(code, agent, YELLOW), arrow_between(agent, behavior, GREEN))

        self.play(FadeIn(code, LEFT))
        self.play(ShowCreation(arrows[0]), FadeIn(agent, UP))
        self.play(ShowCreation(arrows[1]), FadeIn(behavior, RIGHT))

        note = Text("No runtime fork. No special agent magic.", font="Arial", font_size=30)
        note.set_color(INK)
        note.next_to(row, DOWN, buff=0.7)
        self.play(Write(note))
        self.wait(1.2)


class TelegramConnectorScene(DeckScene):
    def construct(self):
        header = title("A real connector: Telegram", "Workshop-safe by default")
        header.to_edge(UP)
        self.play(FadeIn(header, DOWN))

        dry = panel(
            "dry_run=True",
            [
                "prepare payload",
                "show what would be sent",
                "no token needed",
            ],
            GREEN,
            width=4.1,
        )
        real = panel(
            "dry_run=False",
            [
                "TELEGRAM_BOT_TOKEN",
                "TELEGRAM_CHAT_ID",
                "sendMessage API",
            ],
            RED,
            width=4.45,
        )
        tools = panel(
            "Telegram tools",
            [
                "send_telegram_message",
                "get_telegram_updates",
                "plain Bot API",
            ],
            CYAN,
            width=4.55,
        )
        row = VGroup(dry, tools, real).arrange(RIGHT, buff=0.45)
        fit_to_frame(row)
        self.play(LaggedStartMap(FadeIn, row, shift=UP, lag_ratio=0.12))
        self.play(ShowCreation(arrow_between(dry, tools, GREEN)))
        self.play(ShowCreation(arrow_between(tools, real, CYAN)))

        prompt = Text(
            "Prompt: Use Telegram connector in dry-run mode.",
            font="Arial",
            font_size=29,
        )
        prompt.set_color(YELLOW)
        prompt.next_to(row, DOWN, buff=0.7)
        self.play(Write(prompt))
        self.wait(1.2)


class WorkshopFlowScene(DeckScene):
    def construct(self):
        header = title("Workshop flow", "Build, inspect, extend, repeat")
        header.to_edge(UP)
        self.play(FadeIn(header, DOWN))

        steps = VGroup(
            chip("1. Run LangGraph", BLUE, width=3.7),
            chip("2. Open UI", CYAN, width=2.8),
            chip("3. Ask agent", GREEN, width=3.0),
            chip("4. Add connector", YELLOW, width=3.5),
            chip("5. Watch tools", PURPLE, width=3.2),
        )
        steps.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        steps.move_to(ORIGIN).shift(0.3 * LEFT)

        for step in steps:
            self.play(FadeIn(step, RIGHT), run_time=0.35)
        box = SurroundingRectangle(steps, buff=0.35)
        box.set_stroke(CYAN, 2)
        self.play(ShowCreation(box))

        closing = Text("The demo is the architecture.", font="Arial", font_size=34, weight=BOLD)
        closing.set_color(INK)
        closing.next_to(box, DOWN, buff=0.6)
        self.play(Write(closing))
        self.wait(1.4)
