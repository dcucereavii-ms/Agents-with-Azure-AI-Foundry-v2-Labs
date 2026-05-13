"""
Lab 3 — Agent Setup (same as starter — pre-built, no changes needed)
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import CodeInterpreterTool, ToolSet
from azure.identity import DefaultAzureCredential


def create_analysis_agent(client: AIProjectClient) -> str:
    """Create an agent with Code Interpreter for data analysis tasks."""
    toolset = ToolSet()
    toolset.add(CodeInterpreterTool())

    agent = client.agents.create_agent(
        model=os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
        name="AnalysisAgent-Lab3",
        instructions="""You are a data analysis assistant. When given data or questions about
        numbers and trends, use your code interpreter to perform calculations and generate insights.
        Always show your work with code and explain results clearly.""",
        toolset=toolset,
    )
    return agent.id
