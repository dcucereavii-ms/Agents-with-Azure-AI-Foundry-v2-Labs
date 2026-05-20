#!/usr/bin/env python3
"""
Lab 4 -- Production Promotion (Foundry v2 starter).

Your job:
  1. Look up the agent VERSION by (name, version).
  2. Best-effort merge in promotion metadata
     (promoted=true, promoted_version, promoted_at, eval_status).
  3. Print the Foundry portal URL so the team can use the agent.
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
    return (
        "https://ai.azure.com/build/agents/"
        f"{quote(agent_name)}/versions/{quote(str(agent_version))}"
    )


def promote(agent_name: str, agent_version: str, tag: str) -> None:
    client = AIProjectClient(
        endpoint=os.environ["AIPROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    # TODO 1: fetch the agent version via client.agents.get_version(
    #     agent_name=agent_name, agent_version=agent_version).
    # TODO 2: build a metadata dict with promoted=true, promoted_version,
    #     promoted_at, eval_status, promoted_by.
    # TODO 3: best-effort call client.agents.update_version(
    #     agent_name=..., agent_version=..., metadata=...) inside a try/except
    #     (the SDK shape varies across releases).
    # TODO 4: print the portal URL via build_portal_url(...).

    raise NotImplementedError("Implement promote()")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-name", required=True)
    parser.add_argument("--agent-version", required=True)
    parser.add_argument("--version", default="v2-strong")
    args = parser.parse_args()

    promote(args.agent_name, args.agent_version, args.version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
