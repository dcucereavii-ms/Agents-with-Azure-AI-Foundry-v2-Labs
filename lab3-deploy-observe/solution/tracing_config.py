"""
Lab 3 — Tracing Configuration: Complete Solution
"""

import os
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.ai.projects.telemetry import AIInstrumentor
from opentelemetry import trace


def configure_tracing(enable_content_recording: bool = True) -> None:
    """
    Configure OpenTelemetry with Azure Monitor exporter.

    Args:
        enable_content_recording: If True, captures prompt/response content in traces.
                                   Set False for production (PII concerns).
    """
    connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not connection_string:
        print("⚠️  APPLICATIONINSIGHTS_CONNECTION_STRING not set — traces will not be exported")
        return

    # Configure Azure Monitor as the OTLP exporter
    configure_azure_monitor(connection_string=connection_string)

    # Instrument the Azure AI Projects SDK to auto-emit spans
    AIInstrumentor().instrument(enable_content_recording=enable_content_recording)

    print(f"✅ Tracing configured (content recording: {enable_content_recording})")


def get_tracer(name: str = "workshop-agent"):
    """Get a tracer for custom spans. Pre-built."""
    return trace.get_tracer(name)
