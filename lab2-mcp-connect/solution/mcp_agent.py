#!/usr/bin/env python3
"""
Lab 2 — MCP Agent (complete solution).

Attaches an Azure AI Foundry agent to an MCP server *natively* via McpTool.
The Foundry runtime handles tool discovery, invocation, and result routing —
no manual bridge code required.

Default MCP server: Microsoft Learn's public MCP endpoint (no auth needed).
Override with the MCP_SERVER_URL env var to point at your own server.
"""

import os
import sys
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import McpTool, ToolSet, RunStatus
from azure.identity import DefaultAzureCredential
from rich.console import Console
from rich.panel import Panel

load_dotenv()
console = Console()

# Microsoft Learn exposes a public MCP server — perfect for workshop demos.
DEFAULT_MCP_URL = "https://learn.microsoft.com/api/mcp"


def run_agent_with_mcp(queries: list[str]) -> int:
    mcp_url = os.environ.get("MCP_SERVER_URL", DEFAULT_MCP_URL)
    console.print(f"[dim]Attaching MCP server:[/dim] [cyan]{mcp_url}[/cyan]")

    client = AIProjectClient(
        endpoint=os.environ["AIPROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    # 1. Define the MCP attach — server_label is free-form, server_url is the SSE/HTTP endpoint.
    mcp_tool = McpTool(server_label="workshop_mcp", server_url=mcp_url)
    toolset = ToolSet()
    toolset.add(mcp_tool)

    # 2. Create an agent with the MCP server attached natively.
    agent = client.agents.create_agent(
        model=os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
        name="MCPConnectedAgent",
        instructions=(
            "You are a helpful assistant with access to tools provided by an MCP server. "
            "Use the available tools to answer questions accurately. "
            "Always cite which tool you used and the data it returned."
        ),
        toolset=toolset,
    )
    console.print(f"Created agent: [green]{agent.id}[/green]")

    try:
        for query in queries:
            console.print(f"\n[bold blue]Query:[/bold blue] {query}")

            thread = client.agents.create_thread()
            client.agents.create_message(thread_id=thread.id, role="user", content=query)

            run = client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)

            if run.status == RunStatus.COMPLETED:
                messages = client.agents.list_messages(thread_id=thread.id)
                for msg in messages.data:
                    if msg.role == "assistant" and msg.content:
                        console.print(Panel(msg.content[0].text.value, title="Response"))
                        break
            else:
                console.print(f"[red]Run failed: {run.status} — {run.last_error}[/red]")

    finally:
        client.agents.delete_agent(agent.id)
        console.print("[dim]Agent cleaned up.[/dim]")

    return 0


if __name__ == "__main__":
    test_queries = [
        "What is Azure AI Foundry? Use a tool to find the answer.",
        "Search Microsoft Learn for information about Model Context Protocol.",
        "Look up the AIProjectClient class and explain what it does.",
    ]
    sys.exit(run_agent_with_mcp(test_queries))
