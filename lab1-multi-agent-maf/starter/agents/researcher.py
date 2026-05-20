"""ResearcherAgent -- Foundry v2 starter for Lab 1.

TODO: implement `create_researcher_agent` so it returns (agent_name, agent_version).
Hint: use `client.agents.create_version(...)` with `PromptAgentDefinition` and
a `CodeInterpreterTool()` in the `tools` list.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, CodeInterpreterTool


RESEARCHER_INSTRUCTIONS = """You are a research specialist.
When given a topic, draw on your training knowledge to produce a well-structured
summary with:
- Key facts and statistics
- Recent developments and trends
- Relevant context and background
- Caveats where information may be outdated

Use your code interpreter if you need to compute, transform, or structure data
(e.g. building a comparison table). Be thorough but concise."""


def create_researcher_agent(client: AIProjectClient) -> tuple[str, str]:
    """Create a Foundry v2 Researcher agent. Returns (agent_name, agent_version)."""
    # TODO: call client.agents.create_version(...) with a PromptAgentDefinition
    #       that includes CodeInterpreterTool().
    raise NotImplementedError("Implement create_researcher_agent for Lab 1")
