#!/usr/bin/env python3
"""
Lab 2 — MCP Agent (starter).

Attach an Azure AI Foundry agent to an MCP server *natively* via McpTool.
The Foundry runtime handles tool discovery and invocation — your job is
just to wire up the McpTool, build the agent, and run queries against it.

Default MCP server: Microsoft Learn's public MCP endpoint.
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

DEFAULT_MCP_URL = "https://learn.microsoft.com/api/mcp"


def run_agent_with_mcp(queries: list[str]) -> int:
    mcp_url = os.environ.get("MCP_SERVER_URL", DEFAULT_MCP_URL)
    console.print(f"[dim]Attaching MCP server:[/dim] [cyan]{mcp_url}[/cyan]")

    client = AIProjectClient(
        endpoint=os.environ["AIPROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    # TODO 1: Build an McpTool pointing at mcp_url with a server_label of your choice.
    # mcp_tool = McpTool(server_label=..., server_url=...)
    raise NotImplementedError("TODO 1: build the McpTool")

    # TODO 2: Add the McpTool to a ToolSet.
    # toolset = ToolSet(); toolset.add(mcp_tool)

    # TODO 3: Create an agent with the toolset attached.
    # agent = client.agents.create_agent(
    #     model=os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
    #     name="MCPConnectedAgent",
    #     instructions="...",
    #     toolset=toolset,
    # )

    # TODO 4: For each query, create a thread, post the message, run the agent
    # to completion with create_and_process_run, and print the assistant reply.

    # TODO 5: In a finally block, delete the agent so the project stays clean.


if __name__ == "__main__":
    test_queries = [
        "What is Azure AI Foundry? Use a tool to find the answer.",
        "Search Microsoft Learn for information about Model Context Protocol.",
        "Look up the AIProjectClient class and explain what it does.",
    ]
    sys.exit(run_agent_with_mcp(test_queries))
