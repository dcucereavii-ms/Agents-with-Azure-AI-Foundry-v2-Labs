"""WriterAgent -- Foundry v2 solution for Lab 1."""

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
- A brief conclusion

Write in a professional tone suitable for a technical audience.
Do NOT include source citations -- focus on synthesis and clarity."""


def create_writer_agent(client: AIProjectClient) -> tuple[str, str]:
    """
    Create a Writer agent in Microsoft Foundry (v2) -- no external tools, pure LLM.

    Returns:
        Tuple of (agent_name, agent_version).
    """
    agent = client.agents.create_version(
        agent_name="WriterAgent",
        description="Technical writer that turns research into reports (Lab 1).",
        definition=PromptAgentDefinition(
            model=os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
            instructions=WRITER_INSTRUCTIONS,
        ),
    )
    return agent.name, agent.version
