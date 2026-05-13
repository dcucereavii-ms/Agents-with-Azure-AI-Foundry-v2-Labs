"""
Lab 3 — Tracing Configuration
Sets up OpenTelemetry tracing with Azure Monitor exporter.

Your task: complete the configure_tracing() function.
"""

import os
from azure.monitor.opentelemetry import configure_azure_monitor
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

    # TODO: Step 1 — Configure Azure Monitor exporter
    # Call configure_azure_monitor(connection_string=connection_string)

    # TODO: Step 2 — Enable Azure AI content recording
    # Import AIInstrumentor from azure.ai.projects.telemetry
    # Create an instance and call .instrument(enable_content_recording=enable_content_recording)

    print(f"✅ Tracing configured (content recording: {enable_content_recording})")


def get_tracer(name: str = "workshop-agent"):
    """Get a tracer for custom spans. Pre-built."""
    return trace.get_tracer(name)
