#!/usr/bin/env python3
"""
Lab 1 — Multi-Agent Research Pipeline
Entry point: orchestrates the full research → write pipeline
"""

import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

load_dotenv()
console = Console()


def main():
    topic = input("Enter a research topic: ").strip()
    if not topic:
        topic = "Latest advances in quantum computing 2024"

    console.print(Panel(f"[bold blue]Research Pipeline Starting[/bold blue]\nTopic: {topic}"))

    from agents.orchestrator import run_pipeline
    result = run_pipeline(topic)

    console.print(Panel(result, title="[bold green]Final Report[/bold green]", expand=True))


if __name__ == "__main__":
    main()
