# Lab 1 — Your First Multi-Agent System on Azure AI Agent Service

**Duration:** 35 minutes  
**Skill level:** Beginner / Intermediate

> **Note on naming.** This lab uses the **Azure AI Agent Service** SDK (`azure-ai-projects`) — *not* the standalone Microsoft Agent Framework (MAF / `agent-framework`) package. The directory name `lab1-multi-agent-maf` is retained to avoid breaking links; the lab content targets the Foundry Agent Service surface end-to-end.

---

## 🎯 What You'll Build

A **multi-agent research pipeline** that takes a user-supplied topic and automatically researches it on the web, then writes a polished report — all orchestrated by agents.

```
User Query
    │
    ▼
┌──────────────────────────────────────────────┐
│               Orchestrator                   │
│  (coordinates agents, manages lifecycle)     │
└────────────┬─────────────────────┬───────────┘
             │                     │
             ▼                     ▼
   ┌──────────────────┐   ┌──────────────────┐
   │  ResearcherAgent │   │   WriterAgent    │
   │  (Bing grounding)│   │  (pure LLM)      │
   └────────┬─────────┘   └────────┬─────────┘
            │                      │
            │  research_results    │  final_report
            └──────────────────────┘
                        │
                        ▼
                 Final Report (text)
```

**Flow:**
1. User enters a research topic
2. Orchestrator creates a ResearcherAgent with Bing grounding
3. ResearcherAgent searches the web and returns structured findings
4. Orchestrator passes findings to the WriterAgent
5. WriterAgent synthesizes a professional report
6. Orchestrator returns the report and cleans up both agents

---

## 🔧 Lab Setup

```bash
cd lab1-multi-agent-maf
pip install -r requirements.txt
```

Confirm your `.env` file has these values set (instructor provides at workshop start):
- `AIPROJECT_ENDPOINT`
- `BING_CONNECTION_NAME`
- `MODEL_DEPLOYMENT` (defaults to `gpt-4o`)

---

## Step 1 — Explore the Starter Code

Open the `starter/` directory and review each file before writing any code:

| File | Purpose |
|---|---|
| `main.py` | Entry point — already complete, no changes needed |
| `agents/orchestrator.py` | Coordinates the two agents — **your main task** |
| `agents/researcher.py` | Creates the Researcher agent with Bing — **you implement this** |
| `agents/writer.py` | Creates the Writer agent — **you implement this** |
| `utils/helpers.py` | Pre-built helpers (run_agent_turn, cleanup) — no changes needed |

Read each file top to bottom. Notice:
- All TODO comments describe exactly what to implement
- `helpers.py` is fully implemented — study it to understand the run pattern
- The `RESEARCHER_INSTRUCTIONS` and `WRITER_INSTRUCTIONS` strings are already written for you

---

## Step 2 — Create the Researcher Agent

Open `starter/agents/researcher.py`.

Your task is to implement `create_researcher_agent()`. Follow the TODO comments:

1. **Get the Bing connection** from the project using `client.connections.get()`
2. **Create a `BingGroundingTool`** — pass the connection's `.id` field
3. **Create a `ToolSet`** and call `.add(bing_tool)` on it
4. **Call `client.agents.create_agent()`** with the model, name, instructions, and toolset
5. **Return `agent.id`**

> 💡 **Hint:** The connection name comes from `os.environ["BING_CONNECTION_NAME"]`. The agent ID is just a string like `"asst_abc123"`.

**Check your understanding:** Why do we return only the agent ID and not the full agent object?

---

## Step 3 — Create the Writer Agent

Open `starter/agents/writer.py`.

This is simpler than the Researcher — the Writer uses no external tools (pure LLM reasoning).

Implement `create_writer_agent()`:
1. Call `client.agents.create_agent()` with model, name, and instructions
2. **No `toolset` parameter needed**
3. Return `agent.id`

> 💡 **Compare:** Notice how much simpler a no-tool agent is. The model quality and instructions do all the work.

---

## Step 4 — Wire Up the Orchestrator

Open `starter/agents/orchestrator.py`.

This is the most important file. Implement `run_pipeline()` by filling in all 6 TODOs:

1. **Initialize `AIProjectClient`** using `AIPROJECT_ENDPOINT` and `DefaultAzureCredential()`
2. **Create the researcher agent** and save the returned ID
3. **Run the researcher** via `run_agent_turn()` with the topic as the message
4. **Create the writer agent** and save the returned ID
5. **Run the writer** via `run_agent_turn()` passing the research results
6. **Clean up** both agents in the `finally` block via `cleanup_agents()`

> ⚠️ **Important:** Always clean up in `finally` — even if an error occurs, you don't want orphaned agents in your project.

---

## Step 5 — Run the Pipeline

```bash
cd starter
python main.py
```

Enter a research topic when prompted, e.g.:
- `"Latest advances in quantum computing 2024"`
- `"Azure AI Foundry vs OpenAI Assistants comparison"`
- `"Recent breakthroughs in protein folding"`

---

## Step 6 — Observe the Output

Watch the terminal output as the pipeline runs. You should see:

```
╭─ Research Pipeline Starting ──────────────────────────────╮
│ Topic: Latest advances in quantum computing 2024           │
╰────────────────────────────────────────────────────────────╯
  → Running agent asst_abc1...
  → Running agent asst_def2...
  Cleaned up agent asst_abc1
  Cleaned up agent asst_def2
╭─ Final Report ─────────────────────────────────────────────╮
│ ## Executive Summary                                       │
│ ...                                                        │
╰────────────────────────────────────────────────────────────╯
```

Notice:
- The researcher run takes longer (it's making Bing API calls)
- The writer run is faster (pure LLM, no tool calls)
- Cleanup happens in the `finally` block regardless of success/failure

---

## ✅ Success Criteria

Your pipeline is working correctly when:

- [ ] `python main.py` runs without exceptions
- [ ] The Researcher agent returns structured findings with web citations
- [ ] The Writer agent returns a report with Executive Summary, Key Findings, and Analysis sections
- [ ] Both agents are cleaned up (no orphaned agents in your project)
- [ ] You can run it twice with different topics

---

## 🏆 Bonus Challenges

### Bonus 1 — Add a Fact-Checker Agent
Create a third agent called `FactCheckerAgent` that verifies claims from the writer's report. Insert it between the Writer and the final output in the orchestrator.

### Bonus 2 — Parallel Research
Instead of one research turn, create two Researcher agents running different angles of the topic (e.g., "technical aspects" vs "market implications") and combine their results before passing to the Writer.

### Bonus 3 — Persist Results
Modify `main.py` to save the final report to a `.md` file named after the topic + timestamp.

---

## 💡 Key Concepts

| Concept | What It Is |
|---|---|
| **`AIProjectClient`** | The main SDK entry point — connects to your Azure AI Foundry project |
| **`AgentThread`** | A single conversation context for one agent session |
| **`ToolSet`** | Container for tools (BingGrounding, CodeInterpreter, Functions) |
| **`BingGroundingTool`** | Gives the agent real-time web search via Bing |
| **`create_and_process_run()`** | Starts a run and blocks until the agent finishes (handles tool calls internally) |
| **`RunStatus.FAILED`** | Always check the run status before reading messages |
| **`delete_agent()`** | Removes the agent from your project — always clean up! |
