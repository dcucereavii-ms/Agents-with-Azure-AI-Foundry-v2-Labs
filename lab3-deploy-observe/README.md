# Lab 3 — Deploy & Observe: Foundry Agent Service + Tracing

**Duration:** 35 minutes  
**Skill level:** Intermediate

---

## 🎯 What You'll Build

An **instrumented agent** that emits OpenTelemetry traces to Azure Monitor, giving you full visibility into every agent run — including tool calls, prompt content, and latency — viewable in the Azure AI Foundry portal.

```
┌─────────────────────────────────────────────────────────────┐
│  run_agent.py                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  configure_tracing()   ← tracing_config.py         │   │
│  │    └─ configure_azure_monitor()                     │   │
│  │    └─ AIInstrumentor().instrument()                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  AnalysisAgent (Code Interpreter)                   │   │
│  │    Thread → Run → Tool Calls → Response             │   │
│  │         │                                           │   │
│  │         ▼ (auto-instrumented spans)                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│              Azure Monitor / App Insights                   │
│                          │                                  │
│                          ▼                                  │
│      Azure AI Foundry Portal → Tracing Tab                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Lab Setup

```bash
cd lab3-deploy-observe
pip install -r requirements.txt
```

Confirm your `.env` has these set:
- `AIPROJECT_ENDPOINT`
- `APPLICATIONINSIGHTS_CONNECTION_STRING` (instructor provides)
- `MODEL_DEPLOYMENT`

---

## Step 1 — Review the Agent Setup

Open `starter/agent_setup.py`. This file is **pre-built** — no changes needed.

Notice:
- The agent uses `CodeInterpreterTool`, which lets it write and execute Python code
- The instructions direct it to show its work with code
- This creates interesting traces because each code execution is a distinct tool call span

---

## Step 2 — Configure OpenTelemetry Tracing

Open `starter/tracing_config.py`. Complete the `configure_tracing()` function:

### TODO 1 — Configure Azure Monitor exporter

```python
configure_azure_monitor(connection_string=connection_string)
```

This single call:
- Sets up the OTLP exporter pointed at your Application Insights instance
- Registers a `TracerProvider` with Azure as the backend
- Handles sampling, batching, and retry automatically

### TODO 2 — Enable Azure AI content recording

```python
from azure.ai.projects.telemetry import AIInstrumentor

AIInstrumentor().instrument(enable_content_recording=enable_content_recording)
```

`AIInstrumentor` patches the Azure AI Projects SDK so every agent call, tool invocation, and message is automatically wrapped in an OpenTelemetry span.

> ⚠️ **Content recording:** When `enable_content_recording=True`, the actual prompt text and model responses are included in trace attributes. This is useful for debugging but should be `False` in production due to PII concerns.

---

## Step 3 — Enable Azure Monitor Exporter

Ensure your `.env` file has the `APPLICATIONINSIGHTS_CONNECTION_STRING` value. The instructor will provide this.

The format looks like:
```
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxxx-xxxx;IngestionEndpoint=https://eastus2-1.in.applicationinsights.azure.com/
```

---

## Step 4 — Run the Agent and Generate Traces

Open `starter/run_agent.py`. Complete the two TODOs:

### TODO 1 — Call `configure_tracing()` before anything else

```python
configure_tracing(enable_content_recording=True)
```

This **must** be the first call in `run_with_tracing()`. If you call it after creating the client or agent, some SDK calls will not be instrumented.

### TODO 2 — Wrap agent calls in a custom span

```python
with tracer.start_as_current_span(f"query-{i}") as span:
    span.set_attribute("query.text", query)
    span.set_attribute("query.index", i)
    # ... run the agent inside this block
```

Custom spans appear in the trace timeline and let you group related operations.

Then run the agent:

```bash
cd starter
python run_agent.py
```

---

## Step 5 — View Traces in Azure AI Foundry Portal

1. Go to [ai.azure.com](https://ai.azure.com)
2. Select your project
3. Click **Tracing** in the left navigation
4. You should see trace entries for your agent runs within 1-2 minutes
5. Click any trace to expand it

---

## Step 6 — Interpret a Trace

In the trace detail view, look for:

| Span type | What it shows |
|---|---|
| `create_and_process_run` | The full agent turn duration |
| `tool_call: code_interpreter` | Each code execution block |
| Your custom `query-N` span | The parent span you created in the TODO |
| `create_message` | Message creation latency |

**Key metrics to observe:**
- Total run latency vs. code execution latency
- Number of tool calls per run
- Model response size (if content recording enabled)

---

## ✅ Success Criteria

- [ ] `python run_agent.py` runs all 3 sample queries without errors
- [ ] Traces appear in the Azure AI Foundry portal → Tracing tab
- [ ] Each trace shows spans for the agent run and code interpreter tool calls
- [ ] Custom `query-N` spans are visible as parent spans
- [ ] You can identify which query took the longest

---

## 🏆 Bonus Challenges

### Bonus 1 — Add Custom Span Attributes
Add more context to your custom spans:
```python
span.set_attribute("agent.id", agent_id)
span.set_attribute("query.length", len(query))
```
Find these attributes in the trace detail view.

### Bonus 2 — Set Up an Alert
In Azure Monitor:
1. Go to **Alerts** → **Create alert rule**
2. Set a condition on `requests/duration > 30000ms` (30 seconds)
3. This will notify you when agent runs exceed your latency budget

### Bonus 3 — Compare With/Without Content Recording
Run once with `enable_content_recording=True`, then once with `False`.
Compare the trace payloads in the portal — notice what disappears.

---

## 💡 Key Concepts

| Concept | What It Is |
|---|---|
| **OpenTelemetry** | Open standard for distributed tracing, metrics, and logs |
| **Span** | A single timed operation (e.g., one agent run, one tool call) |
| **Trace** | A tree of spans representing one end-to-end operation |
| **`AIInstrumentor`** | Auto-instruments Azure AI SDK calls into spans |
| **`configure_azure_monitor()`** | One-call setup for OTLP export to Application Insights |
| **Content recording** | Option to include prompt/response text in span attributes |
| **`start_as_current_span()`** | Creates a custom span that becomes the parent of any child spans |
