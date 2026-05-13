"""ResearcherAgent — complete solution for Lab 1."""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import BingGroundingTool, ToolSet


RESEARCHER_INSTRUCTIONS = """You are a research specialist with web search capabilities.
When given a topic, use your Bing search tool to find the latest, most relevant information.
Return a well-structured summary with:
- Key facts and statistics
- Recent developments (last 12 months preferred)
- Relevant context and background
- Source citations where possible
Be thorough but concise. Format your response in clear sections."""


def create_researcher_agent(client: AIProjectClient) -> str:
    """
    Create a Researcher agent with Bing grounding.

    Args:
        client: An initialized AIProjectClient

    Returns:
        The agent ID string
    """
    bing_connection = client.connections.get(os.environ["BING_CONNECTION_NAME"])
    bing_tool = BingGroundingTool(connection_id=bing_connection.id)

    toolset = ToolSet()
    toolset.add(bing_tool)

    agent = client.agents.create_agent(
        model=os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
        name="ResearcherAgent",
        instructions=RESEARCHER_INSTRUCTIONS,
        toolset=toolset,
    )
    return agent.id
