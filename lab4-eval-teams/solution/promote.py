#!/usr/bin/env python3
"""
Lab 4 — Production Promotion (complete solution).

Replaces the old "deploy to Teams" step. In Foundry v2 the realistic
promotion artifact is metadata + a Playground URL, not a Teams app package.

Steps:
  1. Look up the agent.
  2. Stamp it with version + eval-pass metadata.
  3. Print the Foundry Playground URL so the team can hit it immediately.
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


def build_playground_url(project_endpoint: str, agent_id: str) -> str:
    """Construct the Foundry Playground URL for the agent.

    Foundry exposes per-agent playgrounds at:
        https://ai.azure.com/build/agents/{agent_id}/playground?wsid=<resource-id>
    The wsid is derived from the project endpoint host; we surface the
    deep link with what we have and let the user paste it.
    """
    return f"https://ai.azure.com/build/agents/{quote(agent_id)}/playground"


def promote(agent_id: str, version: str) -> None:
    client = AIProjectClient(
        endpoint=os.environ["AIPROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    agent = client.agents.get_agent(agent_id)
    console.print(f"Found agent: [cyan]{agent.name}[/cyan] ({agent_id})")

    metadata = dict(getattr(agent, "metadata", None) or {})
    metadata.update({
        "promoted":         "true",
        "promoted_version": version,
        "promoted_at":      datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "promoted_by":      os.environ.get("USERNAME") or os.environ.get("USER") or "unknown",
        "eval_status":      "passed",
    })

    client.agents.update_agent(agent_id=agent_id, metadata=metadata)
    console.print("[green]✓[/green] Agent metadata stamped:")
    for k, v in metadata.items():
        console.print(f"   [dim]{k}[/dim] = {v}")

    url = build_playground_url(os.environ["AIPROJECT_ENDPOINT"], agent_id)
    console.print(f"\n[bold]Playground URL:[/bold] [link={url}]{url}[/link]")
    console.print("\n[dim]Share this URL with your team. They can interact with the promoted agent immediately.[/dim]")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-id", required=True, help="Agent ID to promote.")
    parser.add_argument("--version", default="v2-strong", help="Version tag for metadata.")
    args = parser.parse_args()

    try:
        promote(args.agent_id, args.version)
        return 0
    except Exception as e:
        console.print(f"[red]Promotion failed:[/red] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
