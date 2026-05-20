"""WriterAgent -- Foundry v2 starter for Lab 1.

TODO: implement `create_writer_agent` so it returns (agent_name, agent_version).
No external tools needed -- pure LLM.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition


WRITER_INSTRUCTIONS = """You are an expert technical writer. You receive research summaries
and transform them into clear, well-structured, professional reports.

Your output should include:
- An executive summary (2-3 sentences)
- Key findings (bullet points)
- Detailed analysis (3-4 paragraphs)
- Implications and recommendations
- A brief conclusion"""


def create_writer_agent(client: AIProjectClient) -> tuple[str, str]:
    """Create a Foundry v2 Writer agent (no tools). Returns (name, version)."""
    # TODO: call client.agents.create_version(...) with a PromptAgentDefinition.
    raise NotImplementedError("Implement create_writer_agent for Lab 1")
