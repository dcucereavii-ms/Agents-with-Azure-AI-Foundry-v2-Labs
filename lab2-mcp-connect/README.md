# Lab 2 — MCP Power Hour: Connect Anything in Minutes

**Duration:** 40 minutes  
**Skill level:** Intermediate

---

## 🎯 What You'll Build

A **custom MCP (Model Context Protocol) server** that exposes three tools, and an **Azure AI agent** that connects to that server and uses those tools to answer real queries.

```
┌──────────────────────────────────────────────────────────┐
│                    mcp_agent.py                          │
│  AIProjectClient → Azure AI Agent                        │
│       │                                                  │
│       │  (subprocess / stdio transport)                  │
│       ▼                                                  │
│  ┌────────────────────────────────────────────────────┐  │
│  │              mcp_server.py                         │  │
│  │  Tool: get_weather  (mock weather API)             │  │
│  │  Tool: search_docs  (mock knowledge base)          │  │
│  │  Tool: list_products (mock product catalog)        │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

**Flow:**
1. `mcp_agent.py` launches `mcp_server.py` as a child process
2. Agent discovers available tools via MCP `list_tools` call
3. User queries are sent to the Azure AI agent
4. Agent decides which MCP tool to call and passes arguments
5. MCP server executes the tool and returns results
6. Agent synthesizes the final response

---

## 🔧 Lab Setup

```bash
cd lab2-mcp-connect
pip install -r requirements.txt
```

Confirm your `.env` has `AIPROJECT_ENDPOINT` and `MODEL_DEPLOYMENT` set.

---

## Step 1 — Explore the MCP Server Starter

Open `starter/mcp_server.py` and review the structure:

- **`@app.list_tools()`** — declares the tool schemas available on this server
- **`@app.call_tool()`** — routes incoming tool calls to handler functions
- **`handle_list_products()`** — already fully implemented (study this as your template)
- **`handle_get_weather()`** — your first TODO
- **`handle_search_docs()`** — your second TODO
- **`DOCS`** — the mock document store list already provided

Notice how each tool is declared with a JSON Schema (`inputSchema`) and how the handler returns `list[mcp_types.TextContent]`.

---

## Step 2 — Implement Two MCP Tool Handlers

### 2a — `handle_get_weather()`

Return a mock weather response. Use the `city` and `units` arguments:

```python
async def handle_get_weather(args: dict) -> list[mcp_types.TextContent]:
    city = args["city"]
    units = args.get("units", "celsius")
    
    # Mock weather data — no real API needed
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

### 2b — `handle_search_docs()`

Search the `DOCS` list by keyword match and return up to `max_results` results:

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

> 💡 **Why return JSON strings?** MCP tool results are always plain text. Returning JSON inside a TextContent object lets the LLM parse and reason about structured data.

---

## Step 3 — Test the MCP Server Standalone

Before connecting an agent, verify the server works on its own:

```bash
cd starter
python mcp_server.py
```

The server starts and waits on stdin. You can use the `mcp` CLI to test it (if installed):

```bash
# In a second terminal:
echo '{"method":"tools/list","params":{},"id":1,"jsonrpc":"2.0"}' | python mcp_server.py
```

You should see the list of 3 tools returned. Press Ctrl+C to stop the server.

---

## Step 4 — Connect the Azure AI Agent to the MCP Server

Open `starter/mcp_agent.py`. Complete the `run_agent_with_mcp()` function:

1. **Uncomment the `list_tools` call** to discover available tools
2. **Initialize `AIProjectClient`** with your endpoint and `DefaultAzureCredential()`
3. **Create an agent** that knows about the MCP tools:
   - Convert each MCP tool schema to a `FunctionTool` definition
   - Add them to a `ToolSet`
4. **For each query**, run the agent and let it call MCP tools as needed

> 💡 **Key insight:** The Azure AI agent doesn't call MCP directly — your code intercepts tool calls from the agent run, routes them to the MCP session, and returns results. See the solution for the complete pattern.

---

## Step 5 — Run End-to-End Queries

```bash
cd starter
python mcp_agent.py
```

Expected output:
```
Available MCP tools: ['get_weather', 'search_docs', 'list_products']

Query: What's the weather like in Seattle right now?
  → Tool call: get_weather(city='Seattle', units='celsius')
  → Result: {"city": "Seattle", "temperature": 15, ...}
Response: The current weather in Seattle is partly cloudy with a temperature of 15°C...

Query: Find documentation about MCP protocol
  → Tool call: search_docs(query='MCP protocol', max_results=3)
  ...
```

---

## ✅ Success Criteria

- [ ] `python mcp_server.py` starts without errors
- [ ] `get_weather` returns a valid JSON weather object
- [ ] `search_docs` returns matching documents from the `DOCS` list
- [ ] `python mcp_agent.py` connects to the server and lists all 3 tools
- [ ] At least one test query results in a tool call and a meaningful response

---

## 🏆 Bonus: Add a Third Tool

Add a new tool called `get_stock_price` that returns mock stock data:

1. Add the tool schema to `list_tools()` in `mcp_server.py`
2. Add a handler `handle_get_stock_price()` with mock data
3. Add the routing case in `call_tool()`
4. Test with a query like "What's the current price of Microsoft stock?"

---

## 💡 Key Concepts

| Concept | What It Is |
|---|---|
| **MCP (Model Context Protocol)** | An open standard for connecting LLMs to external tools and data sources via a uniform interface |
| **stdio transport** | The simplest MCP transport — uses stdin/stdout for process-to-process communication |
| **Tool schema** | JSON Schema definition of a tool's name, description, and input parameters |
| **`ClientSession`** | The MCP client that manages the protocol handshake and tool call routing |
| **`StdioServerParameters`** | Configuration for launching an MCP server as a subprocess |
| **Tool call interception** | The pattern of intercepting agent tool calls and routing them to the appropriate backend |
