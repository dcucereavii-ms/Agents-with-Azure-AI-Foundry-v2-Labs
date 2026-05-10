"""
Helper utilities — pre-built for Lab 1.
These are provided so you can focus on agent creation, not boilerplate.
"""

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import RunStatus
from rich.console import Console

console = Console()


def run_agent_turn(client: AIProjectClient, agent_id: str, user_message: str) -> str:
    """
    Send a message to an agent and wait for the response.

    Creates a thread, adds the user message, runs the agent,
    waits for completion, and returns the assistant's response text.
    """
    thread = client.agents.create_thread()

    client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=user_message,
    )

    console.print(f"  [dim]→ Running agent [cyan]{agent_id[:8]}...[/cyan][/dim]")

    run = client.agents.create_and_process_run(
        thread_id=thread.id,
        agent_id=agent_id,
    )

    if run.status == RunStatus.FAILED:
        raise RuntimeError(f"Agent run failed: {run.last_error}")

    messages = client.agents.list_messages(thread_id=thread.id)
    for msg in messages.data:
        if msg.role == "assistant":
            return msg.content[0].text.value if msg.content else ""

    return ""


def cleanup_agents(client: AIProjectClient, *agent_ids: str) -> None:
    """Delete one or more agents by ID. Skips None values."""
    for agent_id in agent_ids:
        if agent_id:
            try:
                client.agents.delete_agent(agent_id)
                console.print(f"  [dim]Cleaned up agent {agent_id[:8]}[/dim]")
            except Exception as e:
                console.print(f"  [yellow]Warning: Could not delete agent {agent_id[:8]}: {e}[/yellow]")
