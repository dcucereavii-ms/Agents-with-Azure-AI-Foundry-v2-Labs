#!/usr/bin/env python3
"""
Lab 3 -- Run Agent with Tracing (Foundry v2 + Microsoft Agent Framework solution).

Creates an AnalysisAgent (Code Interpreter) in Foundry, wraps it with MAF's
FoundryAgent, and runs analytic queries through it. MAF instrumentation is on
by default, and `FoundryAgent.configure_azure_monitor()` pulls the App
Insights connection string straight from the Foundry project -- no extra env
vars needed.

Traces show up in:
  - Application Insights (Transaction Search / End-to-end transactions)
  - Microsoft Foundry portal -> Observability -> Tracing
"""

import asyncio
import os

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from rich.console import Console
from rich.panel import Panel

from agent_framework.foundry import FoundryAgent

from tracing_config import get_tracer
from agent_setup import create_analysis_agent

load_dotenv()
console = Console()

SAMPLE_QUERIES = [
    "Calculate the compound interest on $10,000 at 5% annual rate over 10 years, then plot the growth.",
    "Analyze the Fibonacci sequence: generate the first 20 numbers and identify patterns.",
    "Create a simple sales forecast: given Q1=$100K, Q2=$120K, Q3=$115K, predict Q4 with trend analysis.",
]


async def run_with_tracing() -> None:
    endpoint = os.environ["AIPROJECT_ENDPOINT"]
    credential = DefaultAzureCredential()

    # 1. Provision the hosted agent in Foundry (visible in the portal).
    project_client = AIProjectClient(endpoint=endpoint, credential=credential)
    agent_name, agent_version = create_analysis_agent(project_client)
    console.print(f"[green]OK: Agent created: {agent_name} (v{agent_version})[/green]")

    # 2. Wrap with MAF, then wire up Azure Monitor via the FoundryAgent helper.
    analysis_agent = FoundryAgent(
        project_endpoint=endpoint,
        agent_name=agent_name,
        agent_version=agent_version,
        credential=credential,
        name="analysis_agent",
    )
    await analysis_agent.configure_azure_monitor(enable_sensitive_data=True)
    tracer = get_tracer()

    try:
        for i, query in enumerate(SAMPLE_QUERIES, 1):
            console.print(f"\n[bold blue]Query {i}/{len(SAMPLE_QUERIES)}:[/bold blue] {query[:60]}...")

            # Custom span groups all MAF / Foundry sub-spans under one logical "query-N".
            with tracer.start_as_current_span(f"query-{i}") as span:
                span.set_attribute("query.text", query)
                span.set_attribute("query.index", i)
                span.set_attribute("agent.name", agent_name)
                span.set_attribute("agent.version", agent_version)

                result = await analysis_agent.run(query)
                text = result.text or "(no text output)"
                span.set_attribute("response.length", len(text))

                console.print(Panel(text[:500] + ("..." if len(text) > 500 else ""), title=f"Response {i}"))
    finally:
        try:
            await analysis_agent.client.close()  # type: ignore[attr-defined]
        except Exception:
            pass

        # Agent intentionally LEFT in the project so attendees can browse it.
        #
        # >>> AFTER LAB COMPLETION: uncomment to clean up. <<<
        # project_client.agents.delete_version(agent_name=agent_name, agent_version=agent_version)
        console.print(
            f"[dim]Agent {agent_name} (v{agent_version}) left in project (visit Foundry portal -> Agents)[/dim]"
        )

    console.print("\n[bold green]OK: Done! Check the Azure AI Foundry portal -> Tracing tab[/bold green]")


if __name__ == "__main__":
    asyncio.run(run_with_tracing())
