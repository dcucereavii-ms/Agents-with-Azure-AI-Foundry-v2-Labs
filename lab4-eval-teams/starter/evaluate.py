#!/usr/bin/env python3
"""
Lab 4 — Evaluation Runner (starter).

Your job:
  1. Wire up a live agent target so evaluators score the agent's *actual*
     output, not a pre-canned string in the dataset.
  2. Use the weak/strong agent builders from agent_under_test.py to show
     the gate failing on v1 and passing on v2.
  3. Print the raw `results["metrics"]` dict before applying thresholds so
     metric-key shape drift is visible.
  4. (Bonus) Add a deterministic citation evaluator alongside the LLM judges.

When the strong variant passes the gate, run promote.py to tag the agent.
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import RunStatus
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import (
    GroundednessEvaluator,
    CoherenceEvaluator,
    RelevanceEvaluator,
    evaluate,
)
from rich.console import Console
from rich.table import Table

from agent_under_test import create_weak_agent, create_strong_agent

load_dotenv()
console = Console()

EVAL_THRESHOLDS = {
    "groundedness": 3.5,
    "coherence":    3.5,
    "relevance":    3.5,
}

DATASET_PATH = Path(__file__).parent / "datasets" / "eval_cases.jsonl"


def make_agent_target(client: AIProjectClient, agent_id: str):
    """Return a callable that azure-ai-evaluation will invoke per dataset row."""

    def target(query: str, context: str = "", **_) -> dict:
        # TODO 1: create a thread, post a user message that includes the context
        # and the query, run the agent, and return {"response": <assistant text>}.
        raise NotImplementedError("TODO 1: implement the live agent target")

    return target


def run_evaluation(client: AIProjectClient, agent_id: str, output_path: str) -> dict:
    model_config = {
        "azure_endpoint":   os.environ["AZURE_OPENAI_ENDPOINT"],
        "api_key":          os.environ["AZURE_OPENAI_KEY"],
        "azure_deployment": os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
        "api_version":      "2024-08-01-preview",
    }

    evaluators = {
        "groundedness": GroundednessEvaluator(model_config=model_config),
        "coherence":    CoherenceEvaluator(model_config=model_config),
        "relevance":    RelevanceEvaluator(model_config=model_config),
        # TODO 4 (bonus): add a deterministic CitationPresentEvaluator here.
    }

    # TODO 2: call evaluate(...) with data=DATASET_PATH and target=make_agent_target(...).
    raise NotImplementedError("TODO 2: call evaluate() with the live target")


def eval_gate(results: dict) -> bool:
    metrics = results.get("metrics", {})

    # TODO 3: print the raw `metrics` dict here before threshold checks
    # so you can see exactly which keys the SDK emitted.

    table = Table(title="Evaluation Results")
    table.add_column("Metric")
    table.add_column("Score", justify="right")
    table.add_column("Threshold", justify="right")
    table.add_column("Status", justify="center")

    all_pass = True
    for name, threshold in EVAL_THRESHOLDS.items():
        # TODO 5: metric keys vary between SDK releases
        # ("groundedness", "groundedness.groundedness", etc.).
        # Implement a tolerant lookup helper.
        score = metrics.get(name)
        if score is None:
            table.add_row(name, "—", f"{threshold:.1f}", "[yellow]MISSING[/yellow]")
            all_pass = False
            continue
        passed = float(score) >= threshold
        all_pass = all_pass and passed
        status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
        table.add_row(name, f"{float(score):.2f}", f"{threshold:.1f}", status)

    console.print(table)
    return all_pass


def evaluate_variant(client: AIProjectClient, variant: str) -> tuple[bool, str]:
    if variant == "weak":
        console.rule("[bold yellow]v1 — weak instructions")
        agent_id = create_weak_agent(client)
        out = "eval_results_v1.json"
    else:
        console.rule("[bold green]v2 — strong instructions")
        agent_id = create_strong_agent(client)
        out = "eval_results_v2.json"

    console.print(f"Agent: [cyan]{agent_id}[/cyan]")
    results = run_evaluation(client, agent_id, out)
    return eval_gate(results), agent_id


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=["weak", "strong", "both"], default="both")
    parser.add_argument("--promote", action="store_true")
    args = parser.parse_args()

    client = AIProjectClient(
        endpoint=os.environ["AIPROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    created_agents: list[str] = []
    final_passed = False
    final_agent_id: str | None = None
    try:
        if args.variant in ("weak", "both"):
            passed, agent_id = evaluate_variant(client, "weak")
            created_agents.append(agent_id)

        if args.variant in ("strong", "both"):
            passed, agent_id = evaluate_variant(client, "strong")
            created_agents.append(agent_id)
            final_passed = passed
            final_agent_id = agent_id

        if final_passed:
            console.print("\n[bold green]Quality gate PASSED.[/bold green]")
            if args.promote and final_agent_id:
                import subprocess
                subprocess.run(
                    [sys.executable, "promote.py", "--agent-id", final_agent_id],
                    check=True,
                )
        else:
            console.print("\n[bold red]Quality gate FAILED.[/bold red]")
    finally:
        for aid in created_agents:
            try:
                client.agents.delete_agent(aid)
            except Exception as e:
                console.print(f"[yellow]Could not delete agent {aid[:8]}: {e}[/yellow]")

    return 0 if final_passed else 1


if __name__ == "__main__":
    sys.exit(main())
