#!/usr/bin/env python3
"""
Lab 2 — MCP Agent
Connects an Azure AI agent to the MCP server via subprocess transport.

Your task:
1. Start the MCP server as a subprocess
2. Connect to it and list available tools
3. Create an Azure AI agent that uses those tools
4. Run test queries
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, ToolSet
from azure.identity import DefaultAzureCredential
from rich.console import Console

load_dotenv()
console = Console()


async def connect_to_mcp_server():
    """
    TODO: Connect to the MCP server and return the tools list.

    Steps:
    1. Create StdioServerParameters pointing to mcp_server.py
       server_params = StdioServerParameters(
           command=sys.executable,
           args=["mcp_server.py"],
       )
    2. Use stdio_client(server_params) as a context manager
    3. Create ClientSession(read, write) and call session.initialize()
    4. Call session.list_tools() to get available tools
    5. Return the tool list

    Note: For this lab, we'll return the tools list and handle session externally
    """
    raise NotImplementedError("TODO: implement connect_to_mcp_server")


def build_tool_executor(session):
    """
    Returns a function that executes MCP tool calls.
    Pre-built — no changes needed.
    """
    async def execute_tool(tool_name: str, **kwargs):
        result = await session.call_tool(tool_name, arguments=kwargs)
        return result.content[0].text if result.content else ""
    return execute_tool


async def run_agent_with_mcp(queries: list[str]):
    """Main function — runs the agent pipeline with MCP tools."""

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # TODO: List tools from the MCP server
            # tools_response = await session.list_tools()
            # console.print(f"Available MCP tools: {[t.name for t in tools_response.tools]}")

            # TODO: Initialize AIProjectClient
            # client = AIProjectClient(
            #     endpoint=os.environ["AIPROJECT_ENDPOINT"],
            #     credential=DefaultAzureCredential(),
            # )

            # TODO: Create an agent and run each query
            # For demonstration, print the queries and note what you would do:
            for query in queries:
                console.print(f"\n[bold]Query:[/bold] {query}")
                console.print("[yellow]TODO: Connect agent to MCP and run this query[/yellow]")


if __name__ == "__main__":
    test_queries = [
        "What's the weather like in Seattle right now?",
        "Find documentation about MCP protocol",
        "List all AI-category products",
    ]
    asyncio.run(run_agent_with_mcp(test_queries))
