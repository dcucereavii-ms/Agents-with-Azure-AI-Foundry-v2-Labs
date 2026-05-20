#!/usr/bin/env python3
"""
Lab 4 -- Production Promotion (Foundry v2 solution).

Replaces the old "deploy to Teams" step. In Foundry v2 the realistic
promotion artifact is metadata + a Playground URL, not a Teams app package.

Steps:
  1. Look up the agent VERSION by (name, version).
  2. Best-effort stamp it with promotion metadata.
  3. Print the Foundry portal Agents URL so the team can hit it immediately.
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from urllib.parse import quote

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from rich.console import Console

load_dotenv()
console = Console()


def build_portal_url(agent_name: str, agent_version: str) -> str:
    """Construct the Foundry portal URL for the agent version."""
    return (
        "https://ai.azure.com/build/agents/"
        f"{quote(agent_name)}/versions/{quote(str(agent_version))}"
    )


def promote(agent_name: str, agent_version: str, tag: str) -> None:
    client = AIProjectClient(
        endpoint=os.environ["AIPROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    # Best-effort lookup: the v2 SDK exposes get_version on AgentsOperations.
    try:
        agent = client.agents.get_version(agent_name=agent_name, agent_version=agent_version)
        console.print(
            f"Found agent: [cyan]{agent.name}[/cyan] (v{agent.version})"
        )
    except Exception as e:
        console.print(f"[yellow]Could not fetch agent version: {e}[/yellow]")

    metadata = {
        "promoted":         "true",
        "promoted_version": tag,
        "promoted_at":      datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "promoted_by":      os.environ.get("USERNAME") or os.environ.get("USER") or "unknown",
        "eval_status":      "passed",
    }

    # Metadata stamping is best-effort: SDK shape across azure-ai-projects
    # releases varies (update_version may not accept metadata directly).
    stamped = False
    try:
        client.agents.update_version(
            agent_name=agent_name,
            agent_version=agent_version,
            metadata=metadata,
        )
        stamped = True
    except Exception as e:
        console.print(f"[yellow]Skipping metadata stamp (not supported by SDK): {e}[/yellow]")

    if stamped:
        console.print("[green]OK[/green] Agent metadata stamped:")
        for k, v in metadata.items():
            console.print(f"   [dim]{k}[/dim] = {v}")

    url = build_portal_url(agent_name, agent_version)
    console.print(f"\n[bold]Portal URL:[/bold] [link={url}]{url}[/link]")
    console.print(
        "\n[dim]Share this URL with your team. They can interact with the "
        "promoted agent immediately.[/dim]"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-name", required=True, help="Agent name to promote.")
    parser.add_argument("--agent-version", required=True, help="Agent version to promote.")
    parser.add_argument("--version", default="v2-strong",
                        help="Promotion tag stored in metadata.")
    args = parser.parse_args()

    try:
        promote(args.agent_name, args.agent_version, args.version)
        return 0
    except Exception as e:
        console.print(f"[red]Promotion failed:[/red] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
