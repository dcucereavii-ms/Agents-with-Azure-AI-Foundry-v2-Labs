#!/usr/bin/env python3
"""
Lab 2 -- MCP Agent (Foundry v2 + Microsoft Agent Framework starter).

TODO: complete the three TODOs below so a Foundry v2 agent talks to an MCP
server natively via MCPTool, and is invoked through MAF's FoundryAgent.
"""

import asyncio
import os
import sys
import warnings

# MAF 1.5 surfaces ExperimentalWarning for MemoryStore / SkillResource the
# first time agent_framework is imported. They're informational and noisy
# in a workshop console; silence them up front.
warnings.filterwarnings("ignore", message=r".*is experimental.*")

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool
from azure.identity import DefaultAzureCredential
from rich.console import Console
from rich.panel import Panel

from agent_framework.foundry import FoundryAgent

load_dotenv()
console = Console()

DEFAULT_MCP_URL = "https://learn.microsoft.com/api/mcp"


async def run_agent_with_mcp(queries: list[str]) -> int:
    mcp_url = os.environ.get("MCP_SERVER_URL", DEFAULT_MCP_URL)
    console.print(f"[dim]Attaching MCP server:[/dim] [cyan]{mcp_url}[/cyan]")

    endpoint = os.environ["AIPROJECT_ENDPOINT"]
    credential = DefaultAzureCredential()
    project_client = AIProjectClient(endpoint=endpoint, credential=credential)

    # TODO 1: build an MCPTool with server_label="workshop_mcp",
    #         server_url=mcp_url, require_approval="never"
    mcp_tool = ...  # replace

    # TODO 2: create a Foundry v2 agent via project_client.agents.create_version(...)
    #         with a PromptAgentDefinition that includes [mcp_tool].
    agent_details = ...  # replace

    console.print(
        f"Created agent: [green]{agent_details.name}[/green] (v{agent_details.version})"
    )

    # TODO 3: wrap the hosted agent in a MAF FoundryAgent (project_endpoint,
    #         agent_name, agent_version, credential), then await mcp_agent.run(query).
    mcp_agent = ...  # replace with FoundryAgent(...)

    try:
        for query in queries:
            console.print(f"\n[bold blue]Query:[/bold blue] {query}")
            # result = await mcp_agent.run(query)
            # console.print(Panel(result.text or "(no text)", title="Response"))
    finally:
        try:
            await mcp_agent.client.close()  # type: ignore[attr-defined]
        except Exception:
            pass
        console.print(
            f"[dim]Agent {agent_details.name} (v{agent_details.version}) left in project "
            f"(visit Foundry portal -> Agents)[/dim]"
        )
    return 0


if __name__ == "__main__":
    queries = ["What is Azure AI Foundry? Use a tool to find the answer."]
    sys.exit(asyncio.run(run_agent_with_mcp(queries)))
