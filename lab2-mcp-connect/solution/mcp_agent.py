#!/usr/bin/env python3
"""
Lab 2 -- MCP Agent (Foundry v2 + Microsoft Agent Framework complete solution).

Attaches a Microsoft Foundry agent to an MCP server *natively* via MCPTool --
the Foundry runtime handles tool discovery, invocation, and result routing.
Then we invoke the hosted agent through MAF's `FoundryAgent`, so the call is
wrapped in MAF middleware + OpenTelemetry instrumentation.

Default MCP server: Microsoft Learn's public MCP endpoint (no auth).
Override with the MCP_SERVER_URL env var to point at your own server.

The agent appears in the NEW Foundry portal "Agents" page, and every MCP tool
call is captured under Observability -> Tracing.
"""

import asyncio
import os
import sys
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

    # 1. Provision the agent in Foundry (visible in the portal Agents page).
    project_client = AIProjectClient(endpoint=endpoint, credential=credential)

    mcp_tool = MCPTool(
        server_label="workshop_mcp",
        server_url=mcp_url,
        require_approval="never",
    )
    agent_details = project_client.agents.create_version(
        agent_name="MCPConnectedAgent",
        description="Foundry v2 agent connected to an MCP server (Lab 2).",
        definition=PromptAgentDefinition(
            model=os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
            instructions=(
                "You are a helpful assistant with access to tools provided by an MCP server. "
                "Use the available tools to answer questions accurately. "
                "Always cite which tool you used and what data it returned."
            ),
            tools=[mcp_tool],
        ),
    )
    console.print(
        f"Created agent: [green]{agent_details.name}[/green] (version [cyan]{agent_details.version}[/cyan])"
    )

    # 2. Invoke the hosted agent through MAF's FoundryAgent.
    mcp_agent = FoundryAgent(
        project_endpoint=endpoint,
        agent_name=agent_details.name,
        agent_version=agent_details.version,
        credential=credential,
        name="mcp_agent",
    )

    try:
        for query in queries:
            console.print(f"\n[bold blue]Query:[/bold blue] {query}")
            result = await mcp_agent.run(query)
            console.print(Panel(result.text or "(no text output)", title="Response"))
    finally:
        try:
            await mcp_agent.client.close()  # type: ignore[attr-defined]
        except Exception:
            pass

        # Agent intentionally LEFT in the project so attendees can browse it
        # in the Foundry portal -> Agents tab during the workshop.
        #
        # >>> AFTER LAB COMPLETION: uncomment to clean up. <<<
        # project_client.agents.delete_version(
        #     agent_name=agent_details.name, agent_version=agent_details.version
        # )
        console.print(
            f"[dim]Agent {agent_details.name} (v{agent_details.version}) left in project "
            f"(visit Foundry portal -> Agents)[/dim]"
        )

    return 0


if __name__ == "__main__":
    test_queries = [
        "What is Azure AI Foundry? Use a tool to find the answer.",
        "Search Microsoft Learn for information about Model Context Protocol.",
        "Look up the AIProjectClient class and explain what it does.",
    ]
    sys.exit(asyncio.run(run_agent_with_mcp(test_queries)))
