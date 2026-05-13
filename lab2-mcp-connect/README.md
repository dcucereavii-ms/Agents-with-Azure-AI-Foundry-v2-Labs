# Lab 2 — MCP Power Hour: Connect Anything in Minutes

**Duration:** 40 minutes
**Skill level:** Intermediate

---

## 🎯 What You'll Build

Two complementary pieces of MCP:

1. **A custom MCP server** (`mcp_server.py`) — three tools exposed over stdio, so you understand what an MCP server *is*.
2. **A Foundry agent attached to a remote MCP server** (`mcp_agent.py`) — uses the native `McpTool` integration. By default it points at the public **Microsoft Learn MCP server**; change `MCP_SERVER_URL` to attach any other MCP endpoint (your own, GitHub MCP, etc.).

```
┌──────────────────────────────────────────────────────────────────┐
│              Part A — your MCP server (local, stdio)             │
│   mcp_server.py: get_weather · search_docs · list_products       │
│   You test it standalone — no agent needed.                      │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│           Part B — Foundry agent + remote MCP server             │
│                                                                  │
│   AIProjectClient → Agent (McpTool attached natively)            │
│                              │                                   │
│                              ▼                                   │
│            https://learn.microsoft.com/api/mcp                   │
│   Foundry runtime handles discovery + invocation. No bridge.     │
└──────────────────────────────────────────────────────────────────┘
```

> **Why two parts?** Part A teaches what MCP *is* — a tiny protocol any server can speak. Part B teaches the production pattern on Foundry v2: attach an MCP endpoint and let the runtime do the work. Earlier versions of this lab tried to hand-roll a bridge between the two; the Foundry-native attach is shorter, more correct, and what you'll actually ship.

---

## 🔧 Lab Setup

```bash
cd lab2-mcp-connect
pip install -r requirements.txt
```

Confirm your `.env` has:
- `AIPROJECT_ENDPOINT`
- `MODEL_DEPLOYMENT`
- (Optional) `MCP_SERVER_URL` — defaults to `https://learn.microsoft.com/api/mcp` if not set.

---

## Part A — Build a local MCP server

### Step 1 — Explore the starter

Open `starter/mcp_server.py` and review the structure:

- **`@app.list_tools()`** — declares the tool schemas available on this server
- **`@app.call_tool()`** — routes incoming tool calls to handler functions
- **`handle_list_products()`** — already fully implemented (study this as your template)
- **`handle_get_weather()`** — your first TODO
- **`handle_search_docs()`** — your second TODO
- **`DOCS`** — the mock document store list already provided

### Step 2 — Implement the two tool handlers

**`handle_get_weather()`** — mock weather response:

```python
async def handle_get_weather(args: dict) -> list[mcp_types.TextContent]:
    city = args["city"]
    units = args.get("units", "celsius")
    weather = {
        "city": city,
        "temperature": 15 if units == "celsius" else 59,
        "units": units,
        "condition": "Partly Cloudy",
        "humidity": "72%",
        "wind": "12 km/h NW",
    }
    return [mcp_types.TextContent(type="text", text=json.dumps(weather, indent=2))]
```

**`handle_search_docs()`** — keyword search over `DOCS`:

```python
async def handle_search_docs(args: dict) -> list[mcp_types.TextContent]:
    query = args["query"].lower()
    max_results = args.get("max_results", 3)
    results = [
        doc for doc in DOCS
        if query in doc["title"].lower() or query in doc["content"].lower()
    ][:max_results]
    return [mcp_types.TextContent(type="text", text=json.dumps(results, indent=2))]
```

### Step 3 — Test the server standalone

```bash
cd starter
python mcp_server.py
```

The server starts and waits on stdin. In a second terminal, send a list-tools request:

```bash
echo '{"method":"tools/list","params":{},"id":1,"jsonrpc":"2.0"}' | python mcp_server.py
```

You should see all 3 tools returned. Press Ctrl+C to stop.

> 💡 **What just happened?** You built a self-contained MCP server. Any MCP-compatible client (Claude Desktop, VS Code, Foundry, an IDE plugin, etc.) can now plug into it without any custom integration code. That's the whole point of MCP.

---

## Part B — Attach a remote MCP server to a Foundry agent

### Step 4 — Wire up the McpTool

Open `starter/mcp_agent.py`. Complete the five TODOs in `run_agent_with_mcp()`:

1. Build `McpTool(server_label=..., server_url=mcp_url)`.
2. Add it to a `ToolSet`.
3. Create the agent with the toolset attached.
4. For each query: create a thread, post the message, run with `create_and_process_run`, print the response.
5. Delete the agent in a `finally` block.

The key line is just:

```python
mcp_tool = McpTool(server_label="workshop_mcp", server_url=mcp_url)
toolset = ToolSet(); toolset.add(mcp_tool)
```

Foundry handles the rest — tool discovery, schema, invocation, result routing.

### Step 5 — Run end-to-end

```bash
cd starter
python mcp_agent.py
```

Expected output:

```
Attaching MCP server: https://learn.microsoft.com/api/mcp
Created agent: asst_...

Query: What is Azure AI Foundry? Use a tool to find the answer.
╭─ Response ────────────────────────────────────────────╮
│ Azure AI Foundry is Microsoft's unified platform...   │
│ (citing the Microsoft Learn MCP search tool)          │
╰───────────────────────────────────────────────────────╯
```

You should see at least one of the responses reference a tool call — the agent is reaching into Microsoft Learn through MCP and grounding its answer in live documentation.

---

## ✅ Success Criteria

- [ ] `python mcp_server.py` starts without errors
- [ ] `get_weather` returns a valid JSON weather object
- [ ] `search_docs` returns matching documents from `DOCS`
- [ ] `python mcp_agent.py` connects to the remote MCP server and responds to all 3 queries
- [ ] At least one response cites the MCP tool that produced the data

---

## 🏆 Bonus tracks

**A. Add a third tool to your local MCP server.** Add `get_stock_price` to `list_tools()`, write `handle_get_stock_price()` with mock data, and route it in `call_tool()`.

**B. Point the agent at your own MCP server.** Expose your local `mcp_server.py` over HTTP (e.g. with a tiny FastAPI wrapper or `mcp dev`), tunnel it with `devtunnel` or `ngrok`, set `MCP_SERVER_URL` to the public URL, and rerun `mcp_agent.py`. The agent now talks to *your* server through the same `McpTool` attach.

**C. Attach two MCP servers at once.** Call `toolset.add(mcp_tool_a); toolset.add(mcp_tool_b)`. Watch the agent route the right query to the right server.

---

## 💡 Key Concepts

| Concept | What It Is |
|---|---|
| **MCP (Model Context Protocol)** | Open standard for connecting LLMs to external tools and data sources via a uniform interface |
| **stdio transport** | The simplest MCP transport — uses stdin/stdout for process-to-process communication (Part A) |
| **HTTP/SSE transport** | What Foundry attaches to natively via `McpTool` (Part B) |
| **`McpTool`** | The Foundry-native way to attach an MCP server to an agent — no bridge code required |
| **Tool schema** | JSON Schema definition of a tool's name, description, and input parameters |
| **`ClientSession`** | The Python MCP client used in Part A when you test the server standalone |
