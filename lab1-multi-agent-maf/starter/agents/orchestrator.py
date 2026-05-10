"""
Orchestrator — coordinates ResearcherAgent and WriterAgent.

Your task: implement the run_pipeline() function that:
1. Creates the AIProjectClient
2. Calls the researcher to gather information
3. Passes research results to the writer
4. Returns the final formatted report
5. Cleans up all agents and threads
"""

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
    # TODO: Step 1 — Initialize the AIProjectClient
    # Hint: Use AIProjectClient(endpoint=..., credential=DefaultAzureCredential())
    # The endpoint comes from os.environ["AIPROJECT_ENDPOINT"]
    client = None  # replace this line

    researcher_id = None
    writer_id = None

    try:
        # TODO: Step 2 — Create the researcher agent
        # Call create_researcher_agent(client) and store the returned agent ID
        # researcher_id = ...

        # TODO: Step 3 — Run the researcher with the topic
        # Use run_agent_turn(client, researcher_id, f"Research this topic thoroughly: {topic}")
        # research_results = ...
        research_results = ""  # replace this line

        # TODO: Step 4 — Create the writer agent
        # Call create_writer_agent(client) and store the returned agent ID
        # writer_id = ...

        # TODO: Step 5 — Pass research results to the writer
        # Use run_agent_turn(client, writer_id, f"Write a comprehensive report based on:\n\n{research_results}")
        # final_report = ...
        final_report = "Not implemented yet"  # replace this line

        return final_report

    finally:
        # TODO: Step 6 — Clean up agents (always runs, even on error)
        # Call cleanup_agents(client, researcher_id, writer_id)
        # Hint: check for None before cleaning up
        pass
