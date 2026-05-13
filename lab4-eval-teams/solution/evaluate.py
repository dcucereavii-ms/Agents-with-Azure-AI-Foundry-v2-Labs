#!/usr/bin/env python3
"""
Lab 4 — Evaluation Runner (complete solution).

What's different from a static-data eval:

  - eval_cases.jsonl has ONLY query / ground_truth / context.
  - The `response` is generated **live** by the agent under test at eval time.
  - A deterministic `citation_present` evaluator runs alongside the LLM judges,
    so the gate has some signal even when the judge LLM is rate-limited.
  - We print the raw `results["metrics"]` dict before gating so version-skew
    in metric key naming is immediately visible (no silent zero-defaults).
  - The gate tolerates either "groundedness.groundedness" or bare
    "groundedness" style keys (the SDK has shipped both across releases).
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import RunStatus
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
    "groundedness":     3.5,   # LLM judge, 1-5
    "coherence":        3.5,   # LLM judge, 1-5
    "relevance":        3.5,   # LLM judge, 1-5
    "citation_present": 3.0,   # deterministic, 1 or 5 → average must clear 3.0
}

DATASET_PATH = Path(__file__).parent / "datasets" / "eval_cases.jsonl"


# ─────────────────────────────────────────────────────────────────────────────
# Deterministic evaluator
# ─────────────────────────────────────────────────────────────────────────────
class CitationPresentEvaluator:
    """Returns 5.0 if the response references a concept/class from the context,
    1.0 otherwise. Cheap, fast, no LLM call — gives the gate baseline signal
    when judge LLMs are flaky."""

    CONCEPT_RE = re.compile(r"\b([A-Z][a-zA-Z]+(?:Tool|Client|Evaluator|Agent|Instrumentor))\b|MCP|Foundry|Bing")

    def __call__(self, *, response: str, context: str = "", **kwargs):
        ctx_terms = set(self.CONCEPT_RE.findall(context or ""))
        resp_terms = set(self.CONCEPT_RE.findall(response or ""))
        overlap = ctx_terms & resp_terms
        score = 5.0 if overlap else 1.0
        return {"citation_present": score}


# ─────────────────────────────────────────────────────────────────────────────
# Live agent target — runs the agent for each eval case
# ─────────────────────────────────────────────────────────────────────────────
def make_agent_target(client: AIProjectClient, agent_id: str):
    """Return a callable that azure-ai-evaluation will invoke per row."""

    def target(query: str, context: str = "", **_) -> dict:
        thread = client.agents.create_thread()
        # Feed context to the agent in the user turn so it has something to ground on.
        prompt = f"Context:\n{context}\n\nQuestion: {query}" if context else query
        client.agents.create_message(thread_id=thread.id, role="user", content=prompt)

        run = client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent_id)
        if run.status != RunStatus.COMPLETED:
            return {"response": f"[run failed: {run.last_error}]"}

        messages = client.agents.list_messages(thread_id=thread.id)
        for msg in messages.data:
            if msg.role == "assistant" and msg.content:
                return {"response": msg.content[0].text.value}
        return {"response": ""}

    return target


# ─────────────────────────────────────────────────────────────────────────────
# Eval runner
# ─────────────────────────────────────────────────────────────────────────────
def run_evaluation(client: AIProjectClient, agent_id: str, output_path: str) -> dict:
    model_config = {
        "azure_endpoint":   os.environ["AZURE_OPENAI_ENDPOINT"],
        "api_key":          os.environ["AZURE_OPENAI_KEY"],
        "azure_deployment": os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
        "api_version":      "2024-08-01-preview",
    }

    evaluators = {
        "groundedness":     GroundednessEvaluator(model_config=model_config),
        "coherence":        CoherenceEvaluator(model_config=model_config),
        "relevance":        RelevanceEvaluator(model_config=model_config),
        "citation_present": CitationPresentEvaluator(),
    }

    return evaluate(
        data=str(DATASET_PATH),
        target=make_agent_target(client, agent_id),
        evaluators=evaluators,
        output_path=output_path,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Gate — tolerant of metric-key shape drift across SDK versions
# ─────────────────────────────────────────────────────────────────────────────
def _lookup_metric(metrics: dict, name: str) -> float | None:
    """Find a metric average regardless of which key shape the SDK emitted.

    Known shapes across releases:
      - "groundedness.groundedness"
      - "groundedness.gpt_groundedness"
      - "groundedness"
    """
    if name in metrics:
        return float(metrics[name])
    prefix = f"{name}."
    candidates = [v for k, v in metrics.items() if k.startswith(prefix)]
    if candidates:
        # Prefer keys whose suffix equals the name (e.g. groundedness.groundedness).
        exact = metrics.get(f"{name}.{name}")
        return float(exact) if exact is not None else float(candidates[0])
    return None


def eval_gate(results: dict) -> bool:
    metrics = results.get("metrics", {})

    console.print("\n[dim]Raw metric keys returned by evaluate():[/dim]")
    console.print_json(data=metrics)

    table = Table(title="Evaluation Results")
    table.add_column("Metric", style="bold")
    table.add_column("Score", justify="right")
    table.add_column("Threshold", justify="right")
    table.add_column("Status", justify="center")

    all_pass = True
    for name, threshold in EVAL_THRESHOLDS.items():
        score = _lookup_metric(metrics, name)
        if score is None:
            table.add_row(name, "—", f"{threshold:.1f}", "[yellow]MISSING[/yellow]")
            all_pass = False
            continue
        passed = score >= threshold
        all_pass = all_pass and passed
        status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
        table.add_row(name, f"{score:.2f}", f"{threshold:.1f}", status)

    console.print(table)
    return all_pass


# ─────────────────────────────────────────────────────────────────────────────
# Main: run weak agent → gate fails → strong agent → gate passes → promote
# ─────────────────────────────────────────────────────────────────────────────
def evaluate_variant(client: AIProjectClient, variant: str) -> tuple[bool, str]:
    if variant == "weak":
        console.rule("[bold yellow]v1 — weak instructions")
        agent_id = create_weak_agent(client)
        out = "eval_results_v1.json"
    else:
        console.rule("[bold green]v2 — strong, grounded instructions")
        agent_id = create_strong_agent(client)
        out = "eval_results_v2.json"

    console.print(f"Agent: [cyan]{agent_id}[/cyan]")
    try:
        results = run_evaluation(client, agent_id, out)
        passed = eval_gate(results)
        return passed, agent_id
    except Exception:
        client.agents.delete_agent(agent_id)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--variant",
        choices=["weak", "strong", "both"],
        default="both",
        help="Which agent variant to evaluate.",
    )
    parser.add_argument("--promote", action="store_true",
                        help="If the strong variant passes, run promote.py against it.")
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
            if passed and args.variant == "weak":
                console.print("[yellow]Unexpected: weak variant passed. Tighten thresholds.[/yellow]")

        if args.variant in ("strong", "both"):
            passed, agent_id = evaluate_variant(client, "strong")
            created_agents.append(agent_id)
            final_passed = passed
            final_agent_id = agent_id

        if final_passed:
            console.print("\n[bold green]Quality gate PASSED.[/bold green]")
            if args.promote and final_agent_id:
                console.print("\n[bold]Promoting agent...[/bold]")
                import subprocess
                subprocess.run(
                    [sys.executable, "promote.py", "--agent-id", final_agent_id],
                    check=True,
                )
        else:
            console.print("\n[bold red]Quality gate FAILED. Not promoting.[/bold red]")

    finally:
        # Clean up any agents we created so the project doesn't accumulate them.
        for aid in created_agents:
            try:
                client.agents.delete_agent(aid)
            except Exception as e:
                console.print(f"[yellow]Could not delete agent {aid[:8]}: {e}[/yellow]")

    return 0 if final_passed else 1


if __name__ == "__main__":
    sys.exit(main())
