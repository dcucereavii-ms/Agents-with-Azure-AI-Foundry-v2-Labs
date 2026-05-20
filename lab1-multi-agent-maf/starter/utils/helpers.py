"""
Helper utilities -- Foundry v2 + Microsoft Agent Framework (pre-built for Lab 1 starter).

Agent invocation is now handled by MAF (FoundryAgent + SequentialBuilder), so
we no longer need a hand-rolled run_agent_turn. Only the optional cleanup hook
is kept here.
"""

from azure.ai.projects import AIProjectClient
from rich.console import Console

console = Console()


def cleanup_agents(client: AIProjectClient, *agents) -> None:
    """Delete agent VERSIONS by (name, version) tuple. DISABLED during workshop."""
    for a in agents:
        if a:
            name, version = a
            console.print(
                f"  [dim]Agent {name} (v{version}) left in project (visit Foundry portal -> Agents)[/dim]"
            )
    # for a in agents:
    #     if a:
    #         name, version = a
    #         try:
    #             client.agents.delete_version(agent_name=name, agent_version=version)
    #         except Exception as e:
    #             console.print(f"  [yellow]Could not delete {name} v{version}: {e}[/yellow]")
