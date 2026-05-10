#!/usr/bin/env python3
"""
Lab 4 — Teams Deployment Configuration
Configures and deploys the agent to Microsoft Teams via Azure AI Agent Service.

This script is a guided walkthrough — most steps require portal configuration
alongside code. Follow the README instructions for the full flow.
"""

import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from rich.console import Console
from rich.panel import Panel

load_dotenv()
console = Console()


def configure_teams_channel(client: AIProjectClient, agent_id: str) -> dict:
    """
    TODO: Configure Teams channel for an agent using Azure AI Agent Service.

    In the Azure AI Foundry v2 SDK, Teams channel configuration is done via:
    client.agents.connections or via the REST API / portal.

    For this lab, we'll use the portal-first approach and verify programmatically.

    Steps (mostly portal, verify via SDK):
    1. Go to: Azure AI Foundry portal → your project → Agents
    2. Select your agent → Channels → Add Teams channel
    3. Download the Teams app manifest
    4. Upload to Teams Admin Center or use "Upload custom app" in Teams

    This function verifies the agent is accessible (as a deployment check).
    """
    try:
        agent = client.agents.get_agent(agent_id)
        return {
            "agent_id": agent.id,
            "name": agent.name,
            "model": agent.model,
            "status": "ready",
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}


def create_teams_ready_agent(client: AIProjectClient) -> str:
    """Create a production-ready agent configured for Teams interaction."""
    from azure.ai.projects.models import CodeInterpreterTool, ToolSet

    toolset = ToolSet()
    toolset.add(CodeInterpreterTool())

    agent = client.agents.create_agent(
        model=os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
        name="TeamsAssistant-Production",
        instructions="""You are a helpful assistant deployed in Microsoft Teams.
        You help team members with:
        - Data analysis and calculations
        - Answering questions about Azure AI Foundry
        - Drafting emails and documents
        - General productivity tasks

        Keep responses concise and Teams-friendly (use bullet points, avoid walls of text).
        When doing calculations, show your work briefly.""",
        toolset=toolset,
    )

    console.print(f"[green]✅ Teams-ready agent created: {agent.id}[/green]")
    console.print(Panel(
        f"""[bold]Agent Details[/bold]
ID:    {agent.id}
Name:  {agent.name}
Model: {agent.model}

[yellow]Next steps:[/yellow]
1. Go to Azure AI Foundry portal
2. Navigate to: Agents → {agent.name}
3. Click [bold]Channels[/bold] → [bold]Microsoft Teams[/bold]
4. Follow the Teams app setup wizard
5. Upload the generated manifest to Teams""",
        title="Teams Deployment Guide",
    ))

    return agent.id


def main():
    console.print("[bold blue]🚀 Teams Deployment Configuration[/bold blue]\n")

    client = AIProjectClient(
        endpoint=os.environ["AIPROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    agent_id = create_teams_ready_agent(client)
    status = configure_teams_channel(client, agent_id)

    console.print(f"\n[dim]Deployment status: {status}[/dim]")
    console.print("\n[bold green]✅ Agent ready for Teams configuration![/bold green]")
    console.print("Follow the portal steps shown above to complete Teams setup.")


if __name__ == "__main__":
    main()
