"""
Agent-under-test for Lab 4.

Two variants of the same agent so students can watch the eval gate fail,
fix the instructions, and watch it pass:

    create_weak_agent()    — terse, no grounding requirement, no citations
    create_strong_agent()  — grounded in provided context, must cite

You run the *same* eval suite against both and compare scores.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

WEAK_INSTRUCTIONS = """You are a helpful assistant. Answer questions briefly."""

STRONG_INSTRUCTIONS = """You are an expert assistant for Azure AI developers.

Rules:
- Answer ONLY using facts present in the user-provided context.
- If the context does not contain the answer, say "I don't have enough information to answer that."
- Always reference the specific concept or class name from the context (e.g., AIProjectClient, McpTool).
- Keep responses 2-4 sentences. No filler, no hedging.
"""


def create_agent(client: AIProjectClient, name: str, instructions: str) -> tuple[str, str]:
    """Create an agent VERSION in Foundry v2 and return (name, version)."""
    agent = client.agents.create_version(
        agent_name=name,
        description=f"Lab 4 eval target: {name}",
        definition=PromptAgentDefinition(
            model=os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
            instructions=instructions,
        ),
    )
    return agent.name, agent.version


def create_weak_agent(client: AIProjectClient) -> tuple[str, str]:
    """v1: deliberately under-specified -- should fail the groundedness bar."""
    return create_agent(client, "EvalAgent-v1-weak", WEAK_INSTRUCTIONS)


def create_strong_agent(client: AIProjectClient) -> tuple[str, str]:
    """v2: grounded + citation-required -- should pass the eval gate."""
    return create_agent(client, "EvalAgent-v2-strong", STRONG_INSTRUCTIONS)
