#!/usr/bin/env python3
"""
Lab 3 — Run Agent with Tracing
Main entry point: configures tracing, runs the agent, generates observable spans.

Your task: wire up tracing BEFORE the agent runs.
"""

import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import RunStatus
from azure.identity import DefaultAzureCredential
from opentelemetry import trace
from rich.console import Console
from rich.panel import Panel

from tracing_config import configure_tracing, get_tracer
from agent_setup import create_analysis_agent

load_dotenv()
console = Console()

SAMPLE_QUERIES = [
    "Calculate the compound interest on $10,000 at 5% annual rate over 10 years, then plot the growth.",
    "Analyze the Fibonacci sequence: generate the first 20 numbers and identify patterns.",
    "Create a simple sales forecast: given Q1=$100K, Q2=$120K, Q3=$115K, predict Q4 with trend analysis.",
]


def run_with_tracing():
    # TODO: Step 1 — Call configure_tracing() BEFORE creating any agents
    # This ensures all Azure AI SDK calls are instrumented from the start

    tracer = get_tracer()

    client = AIProjectClient(
        endpoint=os.environ["AIPROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    agent_id = None
    try:
        agent_id = create_analysis_agent(client)
        console.print(f"[green]✅ Agent created: {agent_id}[/green]")

        for i, query in enumerate(SAMPLE_QUERIES, 1):
            console.print(f"\n[bold blue]Query {i}/{len(SAMPLE_QUERIES)}:[/bold blue] {query[:60]}...")

            # TODO: Step 2 — Wrap this agent call in a custom OpenTelemetry span
            # Use: with tracer.start_as_current_span(f"query-{i}") as span:
            #          span.set_attribute("query.text", query)
            #          span.set_attribute("query.index", i)
            #          ... (run the agent inside the span)

            thread = client.agents.create_thread()
            client.agents.create_message(thread_id=thread.id, role="user", content=query)
            run = client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent_id)

            if run.status == RunStatus.COMPLETED:
                messages = client.agents.list_messages(thread_id=thread.id)
                for msg in messages.data:
                    if msg.role == "assistant":
                        response = msg.content[0].text.value if msg.content else ""
                        console.print(Panel(response[:500] + "...", title=f"Response {i}"))
                        break
            else:
                console.print(f"[red]Run failed: {run.last_error}[/red]")

    finally:
        if agent_id:
            client.agents.delete_agent(agent_id)
            console.print("[dim]Agent cleaned up[/dim]")

    console.print("\n[bold green]✅ Done! Check the Azure AI Foundry portal → Tracing tab[/bold green]")
    console.print(f"Project: {os.environ.get('AZURE_AI_PROJECT_NAME', 'your-project')}")


if __name__ == "__main__":
    run_with_tracing()
