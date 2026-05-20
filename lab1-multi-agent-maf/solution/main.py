#!/usr/bin/env python3
"""
Lab 1 -- Multi-Agent Research Pipeline (Foundry v2 + Microsoft Agent Framework).
Entry point: orchestrates Researcher -> Writer via MAF's SequentialBuilder.
"""

import asyncio
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

load_dotenv()
console = Console()


async def _async_main() -> None:
    topic = input("Enter a research topic: ").strip()
    if not topic:
        topic = "Latest advances in quantum computing 2024"

    console.print(Panel(f"[bold blue]Research Pipeline Starting[/bold blue]\nTopic: {topic}"))

    from agents.orchestrator import run_pipeline
    result = await run_pipeline(topic)

    console.print(Panel(result, title="[bold green]Final Report[/bold green]", expand=True))


def main() -> None:
    asyncio.run(_async_main())


if __name__ == "__main__":
    main()
