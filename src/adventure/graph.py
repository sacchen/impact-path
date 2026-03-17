import networkx as nx
from rich.console import Console
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
    node_labels = {n["id"]: n.get("narrative", n["id"])[:55].strip() for n in all_nodes}
    G = build_graph(all_nodes)

    console.print()
    console.rule("[bold cyan]Your Path[/bold cyan]")
    console.print()

    # Path flow: visited nodes with arrows + unexplored branches at each step
    if visited_nodes:
        visited_set = set(visited_nodes)

        for i, node_id in enumerate(visited_nodes):
            is_last = i == len(visited_nodes) - 1
            indent = "  " * i

            # Node box
            label = node_labels.get(node_id, node_id)
            marker = "◉" if is_last else "●"
            color = "bold yellow" if i == 0 else ("bold cyan" if is_last else "cyan")
            console.print(f"{indent}[{color}]{marker} {node_id}[/{color}]  [dim]{label}...[/dim]")

            if not is_last:
                # Show the edge label (choice taken)
                next_id = visited_nodes[i + 1]
                edge_label = G.edges.get((node_id, next_id), {}).get("label", "")
                if edge_label:
                    console.print(f"{indent}[dim]│  ╰─ chose: {edge_label}[/dim]")

                # Show unexplored branches at this node
                neighbors = list(G.successors(node_id))
                unexplored = [n for n in neighbors if n not in visited_set and n != next_id]
                for branch in unexplored:
                    branch_label = node_labels.get(branch, branch)
                    b_edge = G.edges.get((node_id, branch), {}).get("label", "")
                    console.print(
                        f"{indent}[dim]│  ╰╌ {branch}  {branch_label}...[/dim]"
                        if not b_edge else
                        f"{indent}[dim]│  ╰╌ {b_edge} → {branch}[/dim]"
                    )

                console.print(f"{indent}[dim]↓[/dim]")

        # Unexplored from final node
        final = visited_nodes[-1]
        final_neighbors = list(G.successors(final))
        unexplored_final = [n for n in final_neighbors if n not in visited_set]
        if unexplored_final:
            final_indent = "  " * (len(visited_nodes) - 1)
            console.print(f"{final_indent}[dim]  Paths not taken from here:[/dim]")
            for branch in unexplored_final:
                b_edge = G.edges.get((final, branch), {}).get("label", "")
                branch_label = node_labels.get(branch, branch)
                console.print(
                    f"{final_indent}  [dim]╰╌ {b_edge} → {branch}[/dim]"
                    if b_edge else
                    f"{final_indent}  [dim]╰╌ {branch}  {branch_label}...[/dim]"
                )

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
