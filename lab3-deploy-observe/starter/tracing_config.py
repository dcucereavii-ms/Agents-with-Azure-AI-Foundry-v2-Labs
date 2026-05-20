"""
Lab 3 -- Tracing Configuration (Foundry v2 + MAF starter).

Microsoft Agent Framework enables OpenTelemetry instrumentation by default
(1.5+). To send those spans to Application Insights, call
`await foundry_agent.configure_azure_monitor()` from run_agent.py -- it grabs
the App Insights connection string from the Foundry project itself.

This helper just gives you a tracer for custom spans (e.g. one per query).
"""

from opentelemetry import trace


def get_tracer(name: str = "workshop-agent"):
    """Get a tracer for custom spans. Pre-built."""
    return trace.get_tracer(name)
