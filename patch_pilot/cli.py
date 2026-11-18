"""
Command-line interface for Patch Pilot.
"""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import PatchConfig
from .agent import PatchPilotAgent

console = Console()

BANNER = """[bold green]
   ___       _       __       ___  _ __      __ 
  / _ \\___ _/ /_____/ /  ____/ _ \\(_) /___  / /_
 / ___/ _ `/ __/ __/ _ \\/___/ ___/ / / _ \\/ __/
/_/   \\_,_/\\__/\\__/_//_/   /_/  /_/_/\\___/\\__/  
[/bold green]
[dim]🤖 Autonomous Test-Driven Code Healing & Bug Patching Agent powered by Gemini[/dim]
"""


def main():
    parser = argparse.ArgumentParser(
        description="Patch Pilot — Autonomous Test-Driven Bug Patching Agent"
    )
    parser.add_argument("issue", nargs="?", help="Description of the bug or issue to resolve.")
    parser.add_argument("--repo", "-r", type=str, default=".", help="Path to local git repo (default: current directory)")
    parser.add_argument("--test-cmd", "-t", type=str, default=None, help="Custom test command (e.g. 'pytest tests/test_auth.py')")
    parser.add_argument("--max-attempts", "-m", type=int, default=4, help="Max healing iterations (default: 4)")
    parser.add_argument("--model", type=str, default="gemini-2.5-flash", help="Gemini model identifier")
    parser.add_argument("--api-key", "-k", type=str, default=None, help="Gemini API Key override")
    parser.add_argument("--no-branch", action="store_true", help="Do not create a git branch")

    args = parser.parse_args()

    console.print(BANNER)

    issue = args.issue
    if not issue:
        issue = console.input("[bold yellow]Describe the bug to fix: [/bold yellow]").strip()

    if not issue:
        console.print("[red]Error: Bug description cannot be empty.[/red]")
        sys.exit(1)

    repo_path = Path(args.repo).resolve()
    if not repo_path.is_dir():
        console.print(f"[red]Error: Directory '{repo_path}' does not exist.[/red]")
        sys.exit(1)

    config = PatchConfig(
        api_key=args.api_key,
        model=args.model,
        max_healing_attempts=args.max_attempts,
        test_command=args.test_cmd,
        target_repo_dir=repo_path,
        create_branch=not args.no_branch,
    )

    try:
        config.validate()
    except ValueError as e:
        console.print(Panel(f"[bold red]Configuration Error:[/bold red]\n{str(e)}", border_style="red"))
        sys.exit(1)

    console.print(Panel(
        f"[bold white]Repo:[/bold white] {repo_path}\n"
        f"[bold white]Issue:[/bold white] {issue}\n"
        f"[bold white]Model:[/bold white] {config.model}",
        title="[bold green]Mission Activated[/bold green]",
        border_style="green"
    ))

    agent = PatchPilotAgent(config=config)

    with console.status("[bold green]Patch Pilot diagnosing and healing code...[/bold green]", spinner="dots") as status:
        def on_step(msg: str):
            status.update(f"[bold green]{msg}[/bold green]")
            console.print(f"  [dim]•[/dim] {msg}")

        try:
            result = agent.solve_issue(issue_text=issue, on_step=on_step)
        except Exception as e:
            console.print(f"\n[bold red]Execution error:[/bold red] {e}")
            sys.exit(1)

    # Display results
    table = Table(title="Patch Pilot Execution Summary", border_style="green")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    status_str = "[bold green]RESOLVED & VERIFIED[/bold green]" if result["success"] else "[bold red]FAILED[/bold red]"
    table.add_row("Outcome", status_str)
    table.add_row("Healing Attempts", str(result["attempts"]))
    table.add_row("Patched Files", ", ".join(result["patched_files"]) or "None")
    if result.get("branch"):
        table.add_row("Git Branch", result["branch"])
    if result.get("commit_message"):
        table.add_row("Git Commit", result["commit_message"])
    table.add_row("Test Suite", result["test_command"])

    console.print("\n")
    console.print(table)


if __name__ == "__main__":
    main()
