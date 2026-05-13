#!/usr/bin/env python3
"""
Lab 4 — Production Promotion (starter).

Your job:
  1. Look up the agent by ID.
  2. Merge new metadata onto it (version, promoted_at, eval_status).
  3. Print the Foundry Playground URL so the team can use the agent.
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


def build_playground_url(agent_id: str) -> str:
    return f"https://ai.azure.com/build/agents/{quote(agent_id)}/playground"


def promote(agent_id: str, version: str) -> None:
    client = AIProjectClient(
        endpoint=os.environ["AIPROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    # TODO 1: fetch the agent and copy its existing metadata.
    # TODO 2: merge in promoted=true, promoted_version, promoted_at, eval_status.
    # TODO 3: call client.agents.update_agent(agent_id=..., metadata=...).
    # TODO 4: print the playground URL.

    raise NotImplementedError("Implement promote()")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--version", default="v2-strong")
    args = parser.parse_args()

    promote(args.agent_id, args.version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
