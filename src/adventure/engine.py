import yaml
from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel

from .context import SessionContext
from . import claude as llm
from .graph import show_graph_explorer

console = Console()

ROUTES_DIR = Path(__file__).parent.parent.parent / "routes"


def load_nodes() -> dict[str, dict]:
    nodes = {}
    for yaml_file in sorted(ROUTES_DIR.glob("*.yaml")):
        data = yaml.safe_load(yaml_file.read_text())
        for node in data.get("nodes", []):
            nodes[node["id"]] = node
    return nodes


def gather_context(ctx: SessionContext):
    console.print()
    console.print(
        Panel(
            "Before we begin — a few quick questions.",
            border_style="dim",
            padding=(0, 2),
        )
    )
    console.print()

    console.print(
        "  [dim]Sonnet[/dim] handles this well — short, contextual narration is its sweet spot.\n"
        "  [dim]Opus[/dim] goes deeper on nuance and subtext, worth it if you want to really\n"
        "  sit with it or are demoing to someone."
    )
    console.print()
    model_choice = questionary.select(
        "Model",
        choices=[
            questionary.Choice("Sonnet  (default, fast, handles this well)", value="sonnet"),
            questionary.Choice("Opus    (slower, goes deeper on nuance)", value="opus"),
        ],
        instruction="(use arrow keys)",
    ).ask()
    llm.MODEL = "claude-opus-4-6" if model_choice == "opus" else "claude-sonnet-4-6"
    console.print()

    years = questionary.text("Years in EA").ask() or ""
    ctx.character_answers["years_in_ea"] = years

    cause = questionary.text("Cause areas most alive for you").ask() or ""
    ctx.character_answers["cause_areas"] = cause
    ctx.cause_areas = [c.strip() for c in cause.replace(" and ", ", ").split(",") if c.strip()]

    background = questionary.text("How you've been contributing (ops, writing, research...)").ask() or ""
    ctx.character_answers["background"] = background
    ctx.background = [b.strip() for b in background.split(",") if b.strip()]

    blocker = questionary.text("What feels most in the way right now").ask() or ""
    ctx.character_answers["blocker"] = blocker
    ctx.stated_blocker = blocker

    console.print()


def render_node(node: dict, ctx: SessionContext):
    console.rule(f"[dim]{node['id']}[/dim]")
    console.print()
    print("  ", end="")
    llm.narrate(node["narrative"], node.get("claude_hint", ""), ctx)
    console.print("\n")


def get_next_node(node: dict, ctx: SessionContext, all_nodes: dict) -> str | None:
    choices = node.get("choices", [])
    named_choices = [c for c in choices if c.get("type") != "free_response"]
    has_free = any(c.get("type") == "free_response" for c in choices)

    def print_choices():
        console.print()
        for i, c in enumerate(named_choices, 1):
            console.print(f"  [dim][{i}][/dim]  {c['label']}")
        hints = []
        if has_free:
            hints.append("or just type what's on your mind")
        hints.append("[dim][g][/dim] map  [dim][q][/dim] quit")
        console.print(f"  {'  ·  '.join(hints)}")
        console.print()

    while True:
        print_choices()
        raw = questionary.text("").ask()

        if raw is None:
            return "_end"
        raw = raw.strip()

        if not raw:
            continue

        if raw.lower() in ("q", "quit", "exit"):
            return "_end"

        if raw.lower() == "g":
            show_graph_explorer(ctx.visited_nodes, ctx.insights, console, list(all_nodes.values()))
            continue

        # Numeric choice
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(named_choices):
                choice = named_choices[idx]
                console.print()
                print("  ", end="")
                llm.commentary(choice["label"], ctx)
                console.print("\n")

                insight = llm.extract_insight(choice.get("next", ""), choice["label"], ctx)
                if insight:
                    ctx.insights.append(insight)

                return choice.get("next")
            else:
                console.print(f"  [dim]Enter a number between 1 and {len(named_choices)}.[/dim]")
                continue

        # Free response — any non-numeric text
        if has_free and len(raw) > 2:
            ctx.free_responses.append(raw)

            available = [
                all_nodes[c["next"]]
                for c in choices
                if c.get("type") != "free_response"
                and c.get("next") in all_nodes
            ]
            if not available:
                available = list(all_nodes.values())[:6]

            routing = llm.route_free_response(raw, available, ctx)

            if routing.get("follow_up"):
                console.print()
                console.print(f"  [dim]{routing['follow_up']}[/dim]")
                follow_up = questionary.text("").ask()
                if follow_up and follow_up.strip():
                    ctx.free_responses.append(follow_up.strip())

            if routing.get("insight"):
                ctx.insights.append(routing["insight"])

            next_id = routing.get("node_id")
            if next_id and next_id in all_nodes:
                console.print()
                return next_id

        console.print("  [dim]Enter a number or type what's on your mind.[/dim]")


def run():
    ctx = SessionContext()
    nodes = load_nodes()

    console.print()
    console.print(
        Panel(
            "[bold]Impact Clarity[/bold]\n\n"
            "A choose-your-own-adventure for figuring out where you're at.\n\n"
            "[dim]Numbers to choose · f to speak freely · g for your map · q to quit[/dim]",
            border_style="cyan",
            padding=(1, 3),
        )
    )

    gather_context(ctx)

    current_id = "start"

    while current_id and current_id != "_end":
        node = nodes.get(current_id)
        if not node:
            console.print(f"[red]  Node '{current_id}' not found.[/red]")
            break

        ctx.visited_nodes.append(current_id)
        render_node(node, ctx)

        next_id = get_next_node(node, ctx, nodes)

        if next_id is None or next_id == "_end":
            break

        # Leaf nodes that loop back to start
        if next_id == "start":
            current_id = "start"
            continue

        current_id = next_id

    console.print()
    console.rule("[dim]End of session[/dim]")
    show_graph_explorer(ctx.visited_nodes, ctx.insights, console, list(nodes.values()))
