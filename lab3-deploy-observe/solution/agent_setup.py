"""
Lab 3 -- Agent Setup (Foundry v2)
Creates a Code Interpreter agent for the observability demo.
Pre-built -- the focus of Lab 3 is tracing, not agent creation.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, CodeInterpreterTool


def create_analysis_agent(client: AIProjectClient) -> tuple[str, str]:
    """Create a Foundry v2 agent with Code Interpreter. Returns (name, version)."""
    agent = client.agents.create_version(
        agent_name="AnalysisAgent-Lab3",
        description="Data analysis assistant with Code Interpreter (Lab 3).",
        definition=PromptAgentDefinition(
            model=os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
            instructions=(
                "You are a data analysis assistant. When given data or questions about "
                "numbers and trends, use your code interpreter to perform calculations and "
                "generate insights. Always show your work with code and explain results clearly."
            ),
            tools=[CodeInterpreterTool()],
        ),
    )
    return agent.name, agent.version
