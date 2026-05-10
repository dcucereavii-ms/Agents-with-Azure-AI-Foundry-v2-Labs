#!/usr/bin/env python3
"""
Lab 2 — MCP Server: Complete Solution
All tool handlers fully implemented.
"""

import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types as mcp_types

app = Server("workshop-tools-server")


@app.list_tools()
async def list_tools() -> list[mcp_types.Tool]:
    """Declare the tools this server provides."""
    return [
        mcp_types.Tool(
            name="get_weather",
            description="Get current weather conditions for a city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "units": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "default": "celsius",
                    },
                },
                "required": ["city"],
            },
        ),
        mcp_types.Tool(
            name="search_docs",
            description="Search the internal knowledge base for documentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "default": 3},
                },
                "required": ["query"],
            },
        ),
        mcp_types.Tool(
            name="list_products",
            description="List available products from the catalog",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Product category filter (optional)",
                    },
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[mcp_types.TextContent]:
    """Route tool calls to the correct handler."""
    if name == "get_weather":
        return await handle_get_weather(arguments)
    elif name == "search_docs":
        return await handle_search_docs(arguments)
    elif name == "list_products":
        return await handle_list_products(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def handle_list_products(args: dict) -> list[mcp_types.TextContent]:
    products = [
        {"id": "P001", "name": "Azure AI Foundry License", "category": "AI", "price": "$0 (included)"},
        {"id": "P002", "name": "GPT-4o API Access", "category": "AI", "price": "pay-per-token"},
        {"id": "P003", "name": "Azure Monitor", "category": "Observability", "price": "$2.30/GB"},
    ]
    category = args.get("category", "").lower()
    if category:
        products = [p for p in products if p["category"].lower() == category]
    return [mcp_types.TextContent(type="text", text=json.dumps(products, indent=2))]


async def handle_get_weather(args: dict) -> list[mcp_types.TextContent]:
    city = args["city"]
    units = args.get("units", "celsius")

    temp_c = 15
    temp_f = 59
    weather = {
        "city": city,
        "temperature": temp_c if units == "celsius" else temp_f,
        "units": units,
        "condition": "Partly Cloudy",
        "humidity": "72%",
        "wind": "12 km/h NW",
    }
    return [mcp_types.TextContent(type="text", text=json.dumps(weather, indent=2))]


DOCS = [
    {
        "id": 1,
        "title": "Azure AI Foundry Overview",
        "content": "Azure AI Foundry v2 provides a unified platform for building AI agents...",
    },
    {
        "id": 2,
        "title": "MCP Protocol Guide",
        "content": "Model Context Protocol enables standardized tool interfaces for LLMs...",
    },
    {
        "id": 3,
        "title": "Agent Deployment Guide",
        "content": "Deploy agents to production using Azure AI Agent Service...",
    },
    {
        "id": 4,
        "title": "Tracing and Observability",
        "content": "Use OpenTelemetry and Azure Monitor to trace agent execution...",
    },
    {
        "id": 5,
        "title": "Teams Bot Integration",
        "content": "Integrate your agent with Microsoft Teams using Bot Framework...",
    },
]


async def handle_search_docs(args: dict) -> list[mcp_types.TextContent]:
    query = args["query"].lower()
    max_results = int(args.get("max_results", 3))

    results = [
        doc for doc in DOCS
        if query in doc["title"].lower() or query in doc["content"].lower()
    ][:max_results]

    return [mcp_types.TextContent(type="text", text=json.dumps(results, indent=2))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
