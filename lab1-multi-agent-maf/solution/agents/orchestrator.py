"""Orchestrator — complete solution for Lab 1."""

import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from agents.researcher import create_researcher_agent
from agents.writer import create_writer_agent
from utils.helpers import run_agent_turn, cleanup_agents


def run_pipeline(topic: str) -> str:
    """
    Run the full research pipeline for the given topic.

    Args:
        topic: The research topic to investigate

    Returns:
        The final formatted research report
    """
    client = AIProjectClient(
        endpoint=os.environ["AIPROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    researcher_id = None
    writer_id = None

    try:
        researcher_id = create_researcher_agent(client)

        research_results = run_agent_turn(
            client,
            researcher_id,
            f"Research this topic thoroughly: {topic}",
        )

        writer_id = create_writer_agent(client)

        final_report = run_agent_turn(
            client,
            writer_id,
            f"Write a comprehensive report based on:\n\n{research_results}",
        )

        return final_report

    finally:
        cleanup_agents(client, researcher_id, writer_id)
