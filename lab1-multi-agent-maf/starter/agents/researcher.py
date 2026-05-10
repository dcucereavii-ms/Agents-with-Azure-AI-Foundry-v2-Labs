"""
ResearcherAgent — uses Bing grounding to search the web and summarize findings.

Your task: implement create_researcher_agent() that:
1. Retrieves the Bing connection from the project
2. Configures a BingGroundingTool
3. Creates an agent with appropriate instructions
4. Returns the agent ID
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import BingGroundingTool, ToolSet


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
    # TODO: Step 1 — Get the Bing connection from the project
    # Use client.connections.get(os.environ["BING_CONNECTION_NAME"])
    # bing_connection = ...

    # TODO: Step 2 — Create a BingGroundingTool with the connection ID
    # bing_tool = BingGroundingTool(connection_id=bing_connection.id)

    # TODO: Step 3 — Create a ToolSet and add the Bing tool
    # toolset = ToolSet()
    # toolset.add(bing_tool)

    # TODO: Step 4 — Create the agent
    # Use client.agents.create_agent(
    #     model=os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
    #     name="ResearcherAgent",
    #     instructions=RESEARCHER_INSTRUCTIONS,
    #     toolset=toolset,
    # )
    # agent = ...

    # TODO: Step 5 — Return agent.id
    raise NotImplementedError("Implement create_researcher_agent()")
