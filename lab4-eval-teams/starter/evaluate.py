#!/usr/bin/env python3
"""
Lab 4 — Evaluation Runner
Runs Azure AI Evaluation on agent responses and implements a quality gate.

Your tasks:
1. Implement run_evaluation() using azure-ai-evaluation SDK
2. Implement eval_gate() that passes/fails based on thresholds
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()

EVAL_THRESHOLDS = {
    "groundedness": 3.5,  # out of 5
    "coherence": 3.5,     # out of 5
    "relevance": 3.5,     # out of 5
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
    """
    TODO: Run Azure AI Evaluation on the test cases.

    Steps:
    1. Import RelevanceEvaluator, CoherenceEvaluator, GroundednessEvaluator
       from azure.ai.evaluation
    2. Import evaluate from azure.ai.evaluation
    3. Get the OpenAI configuration:
       model_config = {
           "azure_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"],
           "api_key": os.environ["AZURE_OPENAI_KEY"],
           "azure_deployment": os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
           "api_version": "2024-08-01-preview",
       }
    4. Initialize evaluators:
       evaluators = {
           "groundedness": GroundednessEvaluator(model_config=model_config),
           "coherence": CoherenceEvaluator(model_config=model_config),
           "relevance": RelevanceEvaluator(model_config=model_config),
       }
    5. Call evaluate(
           data=str(DATASET_PATH),
           evaluators=evaluators,
           output_path="eval_results.json",
       )
    6. Return results

    Hint: The evaluate() function returns a dict with 'metrics' and 'rows' keys
    """
    raise NotImplementedError("TODO: implement run_evaluation()")


def eval_gate(results: dict) -> bool:
    """
    TODO: Implement the evaluation quality gate.

    Check if all metrics in results['metrics'] meet the thresholds in EVAL_THRESHOLDS.

    Steps:
    1. Extract the metrics dict from results
    2. For each evaluator name + threshold in EVAL_THRESHOLDS:
       - Look for the metric key (format: "{evaluator_name}.{evaluator_name}" or similar)
       - Compare average score to threshold
    3. Return True if ALL metrics pass, False otherwise
    4. Print a table showing each metric, its score, threshold, and PASS/FAIL status

    Hint: metric keys look like "groundedness.groundedness" (the evaluator name repeated)
    """
    raise NotImplementedError("TODO: implement eval_gate()")


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
