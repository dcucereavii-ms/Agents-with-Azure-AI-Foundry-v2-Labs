"""
Helper utilities -- Foundry v2 + Microsoft Agent Framework edition.

Invocation is now handled by MAF (FoundryAgent + SequentialBuilder), so we no
longer need a hand-rolled run_agent_turn(). The only helper kept here is the
optional cleanup hook for the hosted agent versions provisioned in Foundry.
"""

from azure.ai.projects import AIProjectClient
from rich.console import Console

console = Console()


def cleanup_agents(client: AIProjectClient, *agents) -> None:
    """Delete one or more agent VERSIONS by (name, version) tuple.

    NOTE: Cleanup is intentionally DISABLED during the workshop so attendees
    can browse the agents they created in the Foundry portal (Agents tab).

    >>> AFTER LAB COMPLETION: uncomment the block below to clean up. <<<
    """
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
    #             console.print(f"  [dim]Cleaned up {name} v{version}[/dim]")
    #         except Exception as e:
    #             console.print(f"  [yellow]Could not delete {name} v{version}: {e}[/yellow]")
