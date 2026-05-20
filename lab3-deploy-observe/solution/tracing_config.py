"""
Lab 3 -- Tracing Configuration (Foundry v2 + Microsoft Agent Framework solution).

Microsoft Agent Framework enables OpenTelemetry instrumentation by default
(as of 1.5+), so we don't need to call AIProjectInstrumentor() ourselves.
We just need to:

  1. Make sure MAF instrumentation isn't disabled.
  2. Point the OTel exporter at Application Insights.

The cleanest way is to call `await foundry_agent.configure_azure_monitor()`
from run_agent.py -- it grabs the connection string from the Foundry project
itself (no env var required) and wires up Azure Monitor. The helper below is
just a thin wrapper around `opentelemetry.trace.get_tracer` for custom spans.
"""

from opentelemetry import trace


def get_tracer(name: str = "workshop-agent"):
    """Get a tracer for custom spans (e.g. one per query in run_agent.py)."""
    return trace.get_tracer(name)
