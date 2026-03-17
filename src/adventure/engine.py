import yaml
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

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

    years = Prompt.ask("  [dim]Years in EA[/dim]", default="6")
    ctx.character_answers["years_in_ea"] = years

    cause = Prompt.ask(
        "  [dim]Cause areas most alive for you[/dim]",
        default="AI safety and animal welfare",
    )
    ctx.character_answers["cause_areas"] = cause
    ctx.cause_areas = [c.strip() for c in cause.replace(" and ", ", ").split(",") if c.strip()]

    background = Prompt.ask(
        "  [dim]How you've been contributing (ops, writing, research...)[/dim]",
        default="ops, writing, relationships",
    )
    ctx.character_answers["background"] = background
    ctx.background = [b.strip() for b in background.split(",") if b.strip()]

    blocker = Prompt.ask(
        "  [dim]What feels most in the way right now[/dim]",
        default="doubts about skill and fit",
    )
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
    numbered = [(i + 1, c) for i, c in enumerate(choices) if c.get("type") != "free_response"]
    has_free = any(c.get("type") == "free_response" for c in choices)

    # Print choices
    for num, choice in numbered:
        console.print(f"  [dim][{num}][/dim]  {choice['label']}")
    if has_free:
        console.print(f"  [dim][f][/dim]  or just tell me what's going on...")
    console.print(f"  [dim][g][/dim]  show my path so far")
    console.print(f"  [dim][q][/dim]  quit")
    console.print()

    while True:
        raw = Prompt.ask("  [dim]>[/dim]", default="").strip()

        if not raw:
            continue

        if raw.lower() in ("q", "quit", "exit"):
            return "_end"

        if raw.lower() == "g":
            show_graph_explorer(ctx.visited_nodes, ctx.insights, console, list(all_nodes.values()))
            # Reprint choices
            console.print()
            for num, choice in numbered:
                console.print(f"  [dim][{num}][/dim]  {choice['label']}")
            if has_free:
                console.print(f"  [dim][f][/dim]  or just tell me what's going on...")
            console.print()
            continue

        # Numeric choice
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(numbered):
                _, choice = numbered[idx]
                console.print()
                print("  ", end="")
                llm.commentary(choice["label"], ctx)
                console.print("\n")

                insight = llm.extract_insight(choice.get("next", ""), choice["label"], ctx)
                if insight:
                    ctx.insights.append(insight)

                return choice.get("next")
            else:
                console.print(f"  [dim]Enter a number between 1 and {len(numbered)}.[/dim]")
                continue

        # "f" key triggers free response prompt
        if raw.lower() == "f":
            raw = Prompt.ask("  [italic dim]Tell me[/italic dim]").strip()
            if not raw:
                continue

        # Free response (typed text or after pressing f)
        if has_free and len(raw) > 2 and not raw.isdigit():
            ctx.free_responses.append(raw)

            # Get available destination nodes (excluding free_response entries)
            available = [
                all_nodes[c["next"]]
                for c in choices
                if c.get("type") != "free_response"
                and c.get("next") in all_nodes
            ]

            if not available:
                available = [n for n in all_nodes.values()][:6]

            routing = llm.route_free_response(raw, available, ctx)

            if routing.get("follow_up"):
                console.print()
                console.print(f"  [dim]{routing['follow_up']}[/dim]")
                follow_up = Prompt.ask("  [dim]>[/dim]").strip()
                if follow_up:
                    ctx.free_responses.append(follow_up)

            if routing.get("insight"):
                ctx.insights.append(routing["insight"])

            next_id = routing.get("node_id")
            if next_id and next_id in all_nodes:
                console.print()
                return next_id

        console.print("  [dim]Enter a number, 'f' to speak freely, 'g' for map, or 'q' to quit.[/dim]")


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
