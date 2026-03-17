import networkx as nx
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel


def build_graph(all_nodes: list[dict]) -> nx.DiGraph:
    G = nx.DiGraph()
    for node in all_nodes:
        G.add_node(node["id"])
        for choice in node.get("choices", []):
            if choice.get("type") == "free_response":
                continue
            next_id = choice.get("next")
            if next_id and next_id not in ("_end",):
                G.add_edge(node["id"], next_id, label=choice["label"][:40])
    return G


def show_graph_explorer(
    visited_nodes: list[str],
    insights: list[str],
    console: Console,
    all_nodes: list[dict],
):
    node_labels = {n["id"]: n.get("narrative", n["id"])[:60].strip() for n in all_nodes}

    console.print()
    console.rule("[bold cyan]Your Path[/bold cyan]")
    console.print()

    # Path tree
    if visited_nodes:
        tree = Tree(f"[bold yellow]{visited_nodes[0]}[/bold yellow]")
        branch = tree
        for node_id in visited_nodes[1:]:
            label = node_labels.get(node_id, node_id)
            branch = branch.add(
                f"[cyan]{node_id}[/cyan]  [dim]{label}...[/dim]"
            )
        console.print(tree)
        console.print()

    # Insights
    if insights:
        console.print(
            Panel(
                "\n".join(f"  • {i}" for i in insights),
                title="[bold green]What emerged[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        )
        console.print()

    # Stats
    G = build_graph(all_nodes)
    total = G.number_of_nodes()
    explored = len(set(visited_nodes))
    pct = int(explored / total * 100) if total else 0

    console.print(
        Panel(
            f"  Nodes explored: [bold]{explored}[/bold] of {total} ([cyan]{pct}%[/cyan])\n"
            f"  Total paths in graph: [bold]{G.number_of_edges()}[/bold]\n\n"
            f"  [dim]Run again to explore different branches.[/dim]",
            title="[dim]Adventure map[/dim]",
            border_style="dim",
            padding=(1, 2),
        )
    )
    console.print()
