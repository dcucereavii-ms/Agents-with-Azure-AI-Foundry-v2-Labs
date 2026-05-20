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
import asyncio
import json
import os
import sys
import warnings
from pathlib import Path

# MAF 1.5 surfaces ExperimentalWarning for MemoryStore / SkillResource the
# first time agent_framework is imported. Silence them up front.
warnings.filterwarnings("ignore", message=r".*is experimental.*")

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import (
    AzureOpenAIModelConfiguration,
    GroundednessEvaluator,
    CoherenceEvaluator,
    RelevanceEvaluator,
    evaluate,
)
from rich.console import Console
from rich.table import Table

from agent_framework.foundry import FoundryAgent

from agent_under_test import create_weak_agent, create_strong_agent

load_dotenv()
console = Console()

EVAL_THRESHOLDS = {
    "groundedness": 3.5,
    "coherence":    3.5,
    "relevance":    3.5,
}

DATASET_PATH = Path(__file__).parent / "datasets" / "eval_cases.jsonl"


def make_agent_target(endpoint: str, agent_name: str, agent_version: str):
    """Return a sync callable that azure-ai-evaluation will invoke per dataset row."""

    def target(query: str, context: str = "", **_) -> dict:
        # TODO 1: build a prompt that combines `context` and `query`, then
        # invoke a MAF `FoundryAgent` (project_endpoint=endpoint,
        # agent_name=agent_name, agent_version=agent_version) via
        # `asyncio.run(agent.run(prompt))` and return
        # {"response": response.text}.
        raise NotImplementedError("TODO 1: implement the live agent target")

    return target


def run_evaluation(
    endpoint: str,
    agent_name: str,
    agent_version: str,
    output_path: str,
) -> dict:
    # Judge LLM is reached via Microsoft Entra ID (AAD) -- no keys required.
    # The evaluators will use DefaultAzureCredential (same as `az login`) when
    # api_key is omitted from the model_config.
    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_deployment=os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
        api_version="2024-08-01-preview",
    )

    evaluators = {
        "groundedness": GroundednessEvaluator(model_config=model_config),
        "coherence":    CoherenceEvaluator(model_config=model_config),
        "relevance":    RelevanceEvaluator(model_config=model_config),
        # TODO 4 (bonus): add a deterministic CitationPresentEvaluator here.
    }

    # TODO 2: call evaluate(...) with data=DATASET_PATH and
    # target=make_agent_target(endpoint, agent_name, agent_version).
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


def evaluate_variant(
    client: AIProjectClient,
    endpoint: str,
    variant: str,
) -> tuple[bool, tuple[str, str]]:
    if variant == "weak":
        console.rule("[bold yellow]v1 — weak instructions")
        agent_name, agent_version = create_weak_agent(client)
        out = "eval_results_v1.json"
    else:
        console.rule("[bold green]v2 — strong instructions")
        agent_name, agent_version = create_strong_agent(client)
        out = "eval_results_v2.json"

    console.print(f"Agent: [cyan]{agent_name}[/cyan] (v{agent_version})")
    results = run_evaluation(endpoint, agent_name, agent_version, out)
    return eval_gate(results), (agent_name, agent_version)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=["weak", "strong", "both"], default="both")
    parser.add_argument("--promote", action="store_true")
    args = parser.parse_args()

    endpoint = os.environ["AIPROJECT_ENDPOINT"]
    client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    created_agents: list[tuple[str, str]] = []
    final_passed = False
    final_agent: tuple[str, str] | None = None
    try:
        if args.variant in ("weak", "both"):
            passed, agent_ref = evaluate_variant(client, endpoint, "weak")
            created_agents.append(agent_ref)

        if args.variant in ("strong", "both"):
            passed, agent_ref = evaluate_variant(client, endpoint, "strong")
            created_agents.append(agent_ref)
            final_passed = passed
            final_agent = agent_ref

        if final_passed:
            console.print("\n[bold green]Quality gate PASSED.[/bold green]")
            if args.promote and final_agent is not None:
                import subprocess
                name, version = final_agent
                subprocess.run(
                    [
                        sys.executable, "promote.py",
                        "--agent-name", name,
                        "--agent-version", version,
                    ],
                    check=True,
                )
        else:
            console.print("\n[bold red]Quality gate FAILED.[/bold red]")
    finally:
        for name, version in created_agents:
            try:
                client.agents.delete_version(agent_name=name, agent_version=version)
            except Exception as e:
                console.print(f"[yellow]Could not delete {name} v{version}: {e}[/yellow]")

    return 0 if final_passed else 1


if __name__ == "__main__":
    sys.exit(main())
