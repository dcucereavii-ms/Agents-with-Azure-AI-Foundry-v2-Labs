#!/usr/bin/env python3
"""
Lab 3 -- Run Agent with Tracing (Foundry v2 + MAF starter).

TODOs:
  1. Wrap the hosted agent in a MAF `FoundryAgent` and call
     `await foundry_agent.configure_azure_monitor(enable_sensitive_data=True)`
     BEFORE invoking it (this wires up Application Insights for you).
  2. Invoke the agent with `await foundry_agent.run(query)` inside a custom
     `tracer.start_as_current_span(...)` block so each query gets its own
     correlated trace.
"""

import asyncio
import os
import warnings

# MAF 1.5 surfaces ExperimentalWarning for MemoryStore / SkillResource the
# first time agent_framework is imported. They're informational and noisy
# in a workshop console; silence them up front.
warnings.filterwarnings("ignore", message=r".*is experimental.*")

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
]


async def run_with_tracing() -> None:
    endpoint = os.environ["AIPROJECT_ENDPOINT"]
    credential = DefaultAzureCredential()

    project_client = AIProjectClient(endpoint=endpoint, credential=credential)
    agent_name, agent_version = create_analysis_agent(project_client)
    console.print(f"[green]Agent created: {agent_name} (v{agent_version})[/green]")

    # TODO 1: wrap the agent and configure Azure Monitor.
    # analysis_agent = FoundryAgent(
    #     project_endpoint=endpoint,
    #     agent_name=agent_name,
    #     agent_version=agent_version,
    #     credential=credential,
    #     name="analysis_agent",
    # )
    # await analysis_agent.configure_azure_monitor(enable_sensitive_data=True)
    analysis_agent = ...  # replace
    tracer = get_tracer()

    try:
        for i, query in enumerate(SAMPLE_QUERIES, 1):
            console.print(f"\n[bold blue]Query {i}:[/bold blue] {query[:60]}...")

            # TODO 2: wrap the call in `with tracer.start_as_current_span(f"query-{i}") as span:`
            #         set attributes (query.text, agent.name, ...), then:
            #         result = await analysis_agent.run(query)
            #         console.print(Panel((result.text or "")[:500] + "...", title=f"Response {i}"))
            pass
    finally:
        try:
            await analysis_agent.client.close()  # type: ignore[attr-defined]
        except Exception:
            pass
        console.print(
            f"[dim]Agent {agent_name} (v{agent_version}) left in project (visit Foundry portal -> Agents)[/dim]"
        )
        console.print("\n[bold green]Done! Check the Azure AI Foundry portal -> Tracing[/bold green]")


if __name__ == "__main__":
    asyncio.run(run_with_tracing())
