"""ResearcherAgent -- Foundry v2 solution for Lab 1."""

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
(e.g. building a comparison table). Be thorough but concise. Format your
response in clear sections."""


def create_researcher_agent(client: AIProjectClient) -> tuple[str, str]:
    """
    Create a Researcher agent in Microsoft Foundry (v2) with a Code Interpreter tool.

    Uses the new `create_version` + `PromptAgentDefinition` API, so the agent
    shows up in the NEW Foundry portal's "Agents" page (not "Classic agents")
    and emits rich traces under Observability -> Tracing.

    Returns:
        Tuple of (agent_name, agent_version) -- needed for invocation and cleanup.
    """
    agent = client.agents.create_version(
        agent_name="ResearcherAgent",
        description="Research specialist with Code Interpreter (Lab 1).",
        definition=PromptAgentDefinition(
            model=os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
            instructions=RESEARCHER_INSTRUCTIONS,
            tools=[CodeInterpreterTool()],
        ),
    )
    return agent.name, agent.version
