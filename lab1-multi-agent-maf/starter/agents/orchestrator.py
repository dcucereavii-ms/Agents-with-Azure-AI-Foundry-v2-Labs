"""Orchestrator -- Foundry v2 + Microsoft Agent Framework (MAF) starter for Lab 1.

You will:
  1. Provision two Foundry v2 agents (already done for you in researcher.py /
     writer.py via create_version) so they appear in the Foundry portal.
  2. Wrap each one with MAF's `FoundryAgent`.
  3. Compose them with `SequentialBuilder` so the shared conversation flows
     researcher -> writer with zero glue code.
"""

import os
from typing import cast

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from agent_framework import Message
from agent_framework.foundry import FoundryAgent
from agent_framework.orchestrations import SequentialBuilder

from agents.researcher import create_researcher_agent
from agents.writer import create_writer_agent
from utils.helpers import cleanup_agents  # noqa: F401


async def run_pipeline(topic: str) -> str:
    """Run Researcher -> Writer over the given topic using MAF orchestration."""
    endpoint = os.environ["AIPROJECT_ENDPOINT"]
    credential = DefaultAzureCredential()

    project_client = AIProjectClient(endpoint=endpoint, credential=credential)
    researcher_ref = None  # (name, version)
    writer_ref = None
    researcher = None
    writer = None

    try:
        researcher_ref = create_researcher_agent(project_client)
        writer_ref = create_writer_agent(project_client)

        # TODO 1: wrap each hosted agent with MAF's FoundryAgent. Pass
        #         project_endpoint=endpoint, credential=credential, the
        #         agent_name + agent_version from the tuples above, and a
        #         friendly name= ("researcher" / "writer").
        researcher = ...  # replace with FoundryAgent(...)
        writer = ...      # replace with FoundryAgent(...)

        # TODO 2: build a sequential workflow with SequentialBuilder.
        workflow = ...    # replace with SequentialBuilder(participants=[...]).build()

        # TODO 3: iterate workflow.run(prompt, stream=True) and capture the
        #         final list[Message] from event.type == "output".
        final_conversation: list[Message] = []
        # async for event in workflow.run(...):
        #     ...

        # Pick the last assistant message (the writer's output).
        for msg in reversed(final_conversation):
            if msg.role == "assistant" and msg.text:
                return msg.text
        return "(no output produced)"

    finally:
        for agent in (researcher, writer):
            if agent is not None:
                try:
                    await agent.client.close()  # type: ignore[attr-defined]
                except Exception:
                    pass
        # Agents left in project for the workshop. Uncomment to clean up.
        # cleanup_agents(project_client, researcher_ref, writer_ref)
        pass
