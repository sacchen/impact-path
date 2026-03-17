"""First-run API key setup — saved to ~/.config/choose-adventure/key."""

import os
from getpass import getpass
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()

CONFIG_DIR = Path.home() / ".config" / "choose-adventure"
KEY_FILE = CONFIG_DIR / "key"


def get_api_key() -> str:
    """Return API key from env, config file, or prompt on first run."""
    # 1. Environment variable wins
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key

    # 2. Saved config
    if KEY_FILE.exists():
        key = KEY_FILE.read_text().strip()
        if key:
            return key

    # 3. First-run prompt
    return _prompt_and_save()


def _prompt_and_save() -> str:
    console.print()
    console.print(
        Panel(
            "This game uses the Anthropic API.\n\n"
            "Get a free key at [bold]console.anthropic.com[/bold] → API Keys.\n"
            "Your key will be saved to [dim]~/.config/choose-adventure/key[/dim].",
            title="[bold]API Key Required[/bold]",
            border_style="yellow",
            padding=(1, 2),
        )
    )
    console.print()

    while True:
        key = getpass("  Paste your API key (sk-ant-..., hidden): ").strip()
        if key.startswith("sk-ant-") and len(key) > 20:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            KEY_FILE.write_text(key)
            KEY_FILE.chmod(0o600)
            console.print("  [green]Saved.[/green]\n")
            return key
        console.print("  [red]Doesn't look right — should start with sk-ant-[/red]")
