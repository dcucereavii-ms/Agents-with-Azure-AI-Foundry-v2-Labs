#!/usr/bin/env python3
"""
Lab 4 — Evaluation Runner: Complete Solution
All TODOs filled in — full evaluation pipeline with quality gate.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import (
    GroundednessEvaluator,
    CoherenceEvaluator,
    RelevanceEvaluator,
    evaluate,
)
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()

EVAL_THRESHOLDS = {
    "groundedness": 3.5,
    "coherence": 3.5,
    "relevance": 3.5,
}

DATASET_PATH = Path(__file__).parent / "datasets" / "eval_cases.jsonl"


def load_eval_cases() -> list[dict]:
    """Load evaluation cases from JSONL file. Pre-built."""
    cases = []
    with open(DATASET_PATH) as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))
    return cases


def run_evaluation(project_client: AIProjectClient) -> dict:
    """Run Azure AI Evaluation on the test cases."""
    model_config = {
        "azure_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"],
        "api_key": os.environ["AZURE_OPENAI_KEY"],
        "azure_deployment": os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
        "api_version": "2024-08-01-preview",
    }

    evaluators = {
        "groundedness": GroundednessEvaluator(model_config=model_config),
        "coherence": CoherenceEvaluator(model_config=model_config),
        "relevance": RelevanceEvaluator(model_config=model_config),
    }

    results = evaluate(
        data=str(DATASET_PATH),
        evaluators=evaluators,
        output_path="eval_results.json",
    )
    return results


def eval_gate(results: dict) -> bool:
    """Implement the evaluation quality gate."""
    metrics = results.get("metrics", {})

    table = Table(title="Evaluation Results")
    table.add_column("Metric", style="bold")
    table.add_column("Score", justify="right")
    table.add_column("Threshold", justify="right")
    table.add_column("Status", justify="center")

    all_pass = True
    for name, threshold in EVAL_THRESHOLDS.items():
        # Metric keys use the format "evaluator_name.metric_name"
        key = f"{name}.{name}"
        score = float(metrics.get(key, 0.0))
        passed = score >= threshold
        all_pass = all_pass and passed

        status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
        table.add_row(name, f"{score:.2f}", f"{threshold:.1f}", status)

    console.print(table)
    return all_pass


def main():
    console.print("[bold blue]🔍 Running Evaluation Suite[/bold blue]")

    client = AIProjectClient(
        endpoint=os.environ["AIPROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    cases = load_eval_cases()
    console.print(f"Loaded {len(cases)} evaluation cases from {DATASET_PATH.name}")

    console.print("\nRunning evaluators... (this takes 1-2 minutes)")
    results = run_evaluation(client)

    passed = eval_gate(results)

    if passed:
        console.print("\n[bold green]✅ QUALITY GATE PASSED — Agent is ready for deployment![/bold green]")
    else:
        console.print("\n[bold red]❌ QUALITY GATE FAILED — Review results before deploying[/bold red]")

    return 0 if passed else 1


if __name__ == "__main__":
    exit(main())
