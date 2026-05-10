"""WriterAgent — complete solution for Lab 1."""

import os
from azure.ai.projects import AIProjectClient


WRITER_INSTRUCTIONS = """You are an expert technical writer. You receive research summaries
and transform them into clear, well-structured, professional reports.

Your output should include:
- An executive summary (2-3 sentences)
- Key findings (bullet points)
- Detailed analysis (3-4 paragraphs)
- Implications and recommendations
- A brief conclusion

Write in a professional tone suitable for a technical audience.
Do NOT include source citations — focus on synthesis and clarity."""


def create_writer_agent(client: AIProjectClient) -> str:
    """
    Create a Writer agent (no external tools, pure LLM).

    Args:
        client: An initialized AIProjectClient

    Returns:
        The agent ID string
    """
    agent = client.agents.create_agent(
        model=os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
        name="WriterAgent",
        instructions=WRITER_INSTRUCTIONS,
    )
    return agent.id
