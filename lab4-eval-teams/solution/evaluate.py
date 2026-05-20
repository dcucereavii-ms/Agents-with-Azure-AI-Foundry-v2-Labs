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
import asyncio
import json
import os
import re
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

    CONCEPT_RE = re.compile(r"\b([A-Z][a-zA-Z]+(?:Tool|Client|Evaluator|Agent|Instrumentor))\b|MCP|Foundry")

    def __call__(self, *, response: str, context: str = "", **kwargs):
        ctx_terms = set(self.CONCEPT_RE.findall(context or ""))
        resp_terms = set(self.CONCEPT_RE.findall(response or ""))
        overlap = ctx_terms & resp_terms
        score = 5.0 if overlap else 1.0
        return {"citation_present": score}


# ─────────────────────────────────────────────────────────────────────────────
# Live agent target — runs the agent for each eval case via MAF FoundryAgent
# ─────────────────────────────────────────────────────────────────────────────
def make_agent_target(endpoint: str, agent_name: str, agent_version: str):
    """Return a sync callable that azure-ai-evaluation will invoke per row.

    Each call spins up a fresh `FoundryAgent` so the underlying async HTTP
    client lives entirely inside one `asyncio.run` invocation.
    """

    async def _run_one(prompt: str) -> str:
        agent = FoundryAgent(
            project_endpoint=endpoint,
            agent_name=agent_name,
            agent_version=agent_version,
            credential=DefaultAzureCredential(),
            name="eval-target",
        )
        try:
            response = await agent.run(prompt)
            return response.text or ""
        finally:
            try:
                await agent.client.close()  # type: ignore[attr-defined]
            except Exception:
                pass

    def target(query: str, context: str = "") -> dict:
        prompt = f"Context:\n{context}\n\nQuestion: {query}" if context else query
        try:
            text = asyncio.run(_run_one(prompt))
        except Exception as e:  # surface the failure to the evaluator row
            text = f"[run failed: {e}]"
        return {"response": text}

    return target


# ─────────────────────────────────────────────────────────────────────────────
# Eval runner
# ─────────────────────────────────────────────────────────────────────────────
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
        "groundedness":     GroundednessEvaluator(model_config=model_config),
        "coherence":        CoherenceEvaluator(model_config=model_config),
        "relevance":        RelevanceEvaluator(model_config=model_config),
        "citation_present": CitationPresentEvaluator(),
    }

    return evaluate(
        data=str(DATASET_PATH),
        target=make_agent_target(endpoint, agent_name, agent_version),
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
        console.rule("[bold green]v2 — strong, grounded instructions")
        agent_name, agent_version = create_strong_agent(client)
        out = "eval_results_v2.json"

    console.print(f"Agent: [cyan]{agent_name}[/cyan] (v{agent_version})")
    try:
        results = run_evaluation(endpoint, agent_name, agent_version, out)
        passed = eval_gate(results)
        return passed, (agent_name, agent_version)
    except Exception:
        try:
            client.agents.delete_version(agent_name=agent_name, agent_version=agent_version)
        except Exception:
            pass
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
            if passed and args.variant == "weak":
                console.print("[yellow]Unexpected: weak variant passed. Tighten thresholds.[/yellow]")

        if args.variant in ("strong", "both"):
            passed, agent_ref = evaluate_variant(client, endpoint, "strong")
            created_agents.append(agent_ref)
            final_passed = passed
            final_agent = agent_ref

        if final_passed:
            console.print("\n[bold green]Quality gate PASSED.[/bold green]")
            if args.promote and final_agent is not None:
                console.print("\n[bold]Promoting agent...[/bold]")
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
            console.print("\n[bold red]Quality gate FAILED. Not promoting.[/bold red]")

    finally:
        # Clean up any agent versions we created so the project doesn't accumulate them.
        for name, version in created_agents:
            try:
                client.agents.delete_version(agent_name=name, agent_version=version)
            except Exception as e:
                console.print(f"[yellow]Could not delete {name} v{version}: {e}[/yellow]")

    return 0 if final_passed else 1


if __name__ == "__main__":
    sys.exit(main())
