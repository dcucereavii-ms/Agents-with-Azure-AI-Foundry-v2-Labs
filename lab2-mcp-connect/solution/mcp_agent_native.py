#!/usr/bin/env python3
"""
Lab 2 — BONUS: Native MCP attach with Foundry Agent Service.

The main lab (mcp_agent.py) teaches the *manual bridging* pattern:
spawn an MCP server, intercept agent tool calls, and route them through
an MCP ClientSession. This is the right mental model for understanding
how MCP works under the hood.

In production with Azure AI Foundry v2, you typically don't do that —
you attach the MCP server **natively** using `McpTool`, and the
Foundry runtime handles tool discovery, invocation, and result routing
for you. This file shows that pattern.

Requires an HTTP/SSE-reachable MCP endpoint (Foundry currently does not
accept stdio MCP servers directly). For workshop demos point this at a
public MCP server such as the GitHub MCP server, or a locally tunnelled
endpoint (ngrok, devtunnel, etc.).

Usage:
    export MCP_SERVER_URL=https://your-mcp-server.example.com/sse
    python mcp_agent_native.py
"""

import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from rich.console import Console
from rich.panel import Panel

load_dotenv()
console = Console()


def main():
    mcp_url = os.environ.get("MCP_SERVER_URL")
    if not mcp_url:
        console.print("[red]MCP_SERVER_URL not set.[/red]")
        console.print("Set it to an HTTP/SSE MCP endpoint, e.g.:")
        console.print("  export MCP_SERVER_URL=https://api.githubcopilot.com/mcp/")
        return 1

    # Import inside main so the file loads even on SDK versions that don't
    # yet expose McpTool. The 1.0.0b series added McpTool incrementally.
    try:
        from azure.ai.projects.models import McpTool, ToolSet, RunStatus
    except ImportError:
        console.print(
            "[red]McpTool is not available in this azure-ai-projects build.[/red]\n"
            "Upgrade to a build that exposes native MCP attach, or use the\n"
            "manual bridging pattern in mcp_agent.py."
        )
        return 1

    client = AIProjectClient(
        endpoint=os.environ["AIPROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    mcp_tool = McpTool(
        server_label="workshop-mcp",
        server_url=mcp_url,
        # allowed_tools=[...]   # optionally restrict to specific tool names
    )
    toolset = ToolSet()
    toolset.add(mcp_tool)

    agent = client.agents.create_agent(
        model=os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
        name="NativeMcpAgent",
        instructions=(
            "You have access to tools served by an MCP server. "
            "Use them whenever the user asks for data those tools can supply. "
            "Cite the tool result in your answer."
        ),
        toolset=toolset,
    )
    console.print(f"[green]Created agent {agent.id} with native MCP attach.[/green]")

    try:
        thread = client.agents.create_thread()
        client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content="List the tools you have available, then call one and show the result.",
        )

        run = client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=agent.id,
        )

        if run.status == RunStatus.COMPLETED:
            messages = client.agents.list_messages(thread_id=thread.id)
            for msg in messages.data:
                if msg.role == "assistant" and msg.content:
                    console.print(Panel(msg.content[0].text.value, title="Response"))
                    break
        else:
            console.print(f"[red]Run status: {run.status}[/red]")
            if run.last_error:
                console.print(f"[red]{run.last_error}[/red]")

    finally:
        client.agents.delete_agent(agent.id)
        console.print("[dim]Agent cleaned up[/dim]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
