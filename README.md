# From Prototype to Production: Building Real Agents with Azure AI Foundry v2

*Azure AI Foundry v2 + Microsoft Agent Framework — Advanced Workshop*

---

## 🗓️ Workshop Agenda

| Time | Session | Format |
|---|---|---|
| 9:00 – 9:20 AM | **Module 1** — The Agent Production Gap: Where Most Devs Get Stuck | Presentation |
| 9:20 – 9:35 AM | **Module 2** — The Model Catalog: Right Model, Right Task, Right Cost | Presentation + Live Demo |
| 9:35 – 10:05 AM | **Module 3** — Microsoft Agent Framework: Build Agents the Right Way | Presentation + Code Walkthrough |
| 10:05 – 10:40 AM | **Module 4** — Agent Service: The Managed Runtime for Your Agents | Presentation + Live Demo |
| 10:40 – 11:10 AM | **Module 5** — MCP + A2A: The Open Standards That Change Everything | Presentation + Live Demo |
| 11:10 – 11:35 AM | **Module 6** — Ship It: Voice, Teams, Evals, Production | Presentation + Demo |
| 11:35 AM – 12:30 PM | *Lunch Break* | — |
| 12:30 – 1:05 PM | **Lab 1** — Your First Multi-Agent System with MAF | Hands-On Lab |
| 1:05 – 1:45 PM | **Lab 2** — MCP Power Hour: Connect Anything in Minutes | Hands-On Lab |
| 1:45 – 2:20 PM | **Lab 3** — Deploy & Observe: Foundry Agent Service + Tracing | Hands-On Lab |
| 2:20 – 2:55 PM | **Lab 4** — Ship It: Eval Gate + Iterate to Production | Hands-On Lab |
| 2:55 – 3:05 PM | **Wrap-Up** — Live Agents in the Room | Discussion & Demo |

> **Morning** = presentations + demos. **Afternoon** = 4 hands-on labs back-to-back.
> Pre-workshop setup (below) is required so the afternoon starts at minute one.

---

## 📋 Pre-Workshop Student Guide

Welcome! This guide will get you fully prepared **before** you arrive at the workshop. Please complete **all** setup steps ahead of time — the labs are 100% hands-on and we hit the ground running from minute one.

---

> **⚠️ IMPORTANT: Bring Your Own Device**
>
> Students **must bring their own laptop** to the workshop. All labs are hands-on and require a working development environment on your machine. Loaner devices are **not** available. If you have any concerns about hardware, please contact the organizers at least 48 hours in advance.

---

## 🔐 Microsoft Authenticator — Required

You **must** have the **Microsoft Authenticator** app installed and configured on your mobile device **before** arriving at the workshop. This is the required second factor for authenticating with the sandbox Azure subscription.

### Install the app

| Platform | Where to get it |
|---|---|
| **iOS** | Open the App Store and search **"Microsoft Authenticator"** (by Microsoft Corporation) |
| **Android** | Open Google Play and search **"Microsoft Authenticator"** (by Microsoft Corporation) |

### Setup steps

1. Install the app on your phone
2. Open Authenticator and sign in with your **Microsoft account or work/school account**
3. Complete the initial setup (add your account, scan the QR code if prompted)
4. Verify the app shows your account tile before the workshop day

### Sandbox subscription access

- Sandbox credentials will be **emailed to you 24 hours before the workshop**
- After receiving the email, use Authenticator to complete the MFA sign-in and **confirm it works**
- If you cannot log in, contact the workshop team **before** arriving — we cannot pause labs for account issues

---

## 💻 Hardware Requirements

| Requirement | Minimum | Recommended |
|---|---|---|
| **OS** | Windows 10, macOS 12 (Monterey), Ubuntu 20.04 | Windows 11, macOS 14+, Ubuntu 22.04+ |
| **RAM** | 8 GB | 16 GB |
| **Free disk space** | 10 GB | 15 GB+ |
| **Internet** | Required | Stable connection (workshop Wi-Fi provided) |
| **Ports** | 443 (HTTPS) must be open | — |

> **Corporate laptops:** If you are on a managed corporate device, confirm you can install Python packages and run `az login` without restrictions. VPN/proxy settings can block Azure CLI authentication — test this ahead of time.

---

## 🛠️ Software Prerequisites

Please install all of the following **before** the workshop. Each item includes a link and quick verification command.

### 1. Python 3.11+

Python 3.11 or 3.12 is required. Python 3.10 and below **will not work** with some SDK features.

- **Download:** https://www.python.org/downloads/
- During Windows installation, check **"Add Python to PATH"**

**Verify:**
```bash
python --version
# Expected: Python 3.11.x or 3.12.x
```

---

### 2. Git

- **Download:** https://git-scm.com/downloads
- Accept defaults during installation on Windows

**Verify:**
```bash
git --version
# Expected: git version 2.x.x
```

---

### 3. Visual Studio Code (Recommended)

VS Code is the recommended editor for this workshop.

- **Download:** https://code.visualstudio.com/
- After installation, install the **Python extension**:
  - Open VS Code → Extensions (Ctrl+Shift+X) → search "Python" → install the one by Microsoft

**Verify:** Open VS Code and confirm the Python extension is visible in the status bar.

---

### 4. Azure CLI

The Azure CLI is required to authenticate with your sandbox Azure subscription.

- **Installation guide:** https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
  - **Windows:** Download the MSI installer from the link above
  - **macOS:** `brew install azure-cli`
  - **Ubuntu:** `curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash`

**Verify:**
```bash
az version
# Expected: JSON output with "azure-cli": "2.x.x"
```

---

### 5. Node.js 18+ (Required for Lab 2)

Lab 2 uses MCP tooling that requires Node.js.

- **Download:** https://nodejs.org/ (choose the LTS version)

**Verify:**
```bash
node --version
# Expected: v18.x.x or v20.x.x

npm --version
# Expected: 9.x.x or 10.x.x
```

---

## 🔑 Azure Access Setup

Sandbox subscription credentials will arrive via email 24 hours before the workshop. Once you have them, complete these steps:

### Step 1 — Log in with Azure CLI

```bash
az login
```

This opens a browser (or shows a device code). Complete the MFA prompt with Microsoft Authenticator.

### Step 2 — Select the sandbox subscription

```bash
az account set --subscription <subscription-id>
```

Replace `<subscription-id>` with the ID from your credentials email.

### Step 3 — Verify you're on the right subscription

```bash
az account show
```

Confirm the `"name"` and `"id"` fields match the sandbox subscription from your email.

> **Tip:** If you see your personal or corporate subscription instead of the sandbox, run `az account list --output table` to see all available subscriptions, then use `az account set` again with the correct ID.

---

## ⚡ Pre-Lab Environment Setup — Do This **Before** You Arrive

> **We only have half a day. Every minute spent on `pip install` is a minute we don't get back.**
> Complete *all* steps below before the workshop. If you arrive with a fully primed environment, we go straight into Lab 1.

You will install **every** dependency for **every** lab ahead of time. Total install: ~5 minutes on a fast connection, ~15 on hotel Wi-Fi. Do not leave this for the workshop room.

### TL;DR — one command

After cloning the repo (Step 1 below), you can run a single script that does Steps 2–7 for you:

```powershell
# Windows (PowerShell)
.\scripts\setup.ps1
```

```bash
# macOS / Linux
chmod +x scripts/setup.sh
./scripts/setup.sh
```

If that finishes with **all green** in `verify_setup.py`, skip to the [verification checklist](#-pre-workshop-verification-checklist). Otherwise, follow the manual steps below.

---

### Step 1 — Clone the repo

```bash
git clone https://github.com/dcucereavii-ms/Agents-with-Azure-AI-Foundry-v2-Labs.git
cd Agents-with-Azure-AI-Foundry-v2-Labs
```

You should see four lab directories: `lab1-multi-agent-maf`, `lab2-mcp-connect`, `lab3-deploy-observe`, `lab4-eval-teams`.

### Step 2 — Create your `.env` file

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

> The actual values (`AIPROJECT_ENDPOINT`, `AZURE_OPENAI_*`, etc.) will be handed out at the workshop. You just need the file to exist.

### Step 3 — Create and activate a virtual environment

```bash
python -m venv .venv
```

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd.exe)
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

You should see `(.venv)` at the start of your terminal prompt. **All subsequent steps must run inside this venv.**

### Step 4 — Upgrade pip and install ALL lab dependencies

This is the critical step. Do not skip — install every lab's requirements now so they're cached and resolved on your machine before the workshop:

```bash
python -m pip install --upgrade pip

pip install -r shared/requirements.txt
pip install -r lab1-multi-agent-maf/requirements.txt
pip install -r lab2-mcp-connect/requirements.txt
pip install -r lab3-deploy-observe/requirements.txt
pip install -r lab4-eval-teams/requirements.txt
```

> All lab `requirements.txt` files extend `shared/requirements.txt`, so this is fast after the first one — but **run all five commands anyway** so any lab-specific package (`mcp`, `azure-ai-evaluation`) lands in the pip cache.

**One-liner alternative (PowerShell):**

```powershell
'shared','lab1-multi-agent-maf','lab2-mcp-connect','lab3-deploy-observe','lab4-eval-teams' | ForEach-Object { pip install -r "$_/requirements.txt" }
```

**One-liner alternative (bash):**

```bash
for d in shared lab1-multi-agent-maf lab2-mcp-connect lab3-deploy-observe lab4-eval-teams; do
  pip install -r "$d/requirements.txt"
done
```

### Step 5 — Install Node.js dependencies for Lab 2

Lab 2 uses an MCP server that runs on Node. Pre-fetch the npm package now so you don't wait at the workshop:

```bash
npx -y @modelcontextprotocol/server-everything --help
```

This downloads and caches the reference MCP server. You should see a help message and exit. If it hangs or errors, fix it before the workshop.

### Step 6 — Verify your setup

```bash
python shared/verify_setup.py
```

A successful pre-workshop run looks like:

```
✅ Python 3.11.9 — OK
✅ pip 24.x — OK
✅ Virtualenv active — OK
✅ azure-ai-projects (AIProjectClient) — Lab 1, 2, 3, 4
✅ azure-ai-projects.models (BingGroundingTool) — Lab 1
✅ azure-ai-projects.models (CodeInterpreterTool) — Lab 1
✅ azure-ai-projects.models (McpTool) — Lab 2
✅ azure-ai-projects.telemetry (AIInstrumentor) — Lab 3
✅ azure-identity (DefaultAzureCredential) — Lab 1, 2, 3, 4
✅ azure-monitor-opentelemetry (configure_azure_monitor) — Lab 3
✅ azure-ai-evaluation (GroundednessEvaluator) — Lab 4
✅ mcp (Client) — Lab 2
✅ httpx — Lab 2
✅ python-dotenv (load_dotenv) — Lab 1, 2, 3, 4
✅ rich (Console) — Lab 1, 2, 3, 4
✅ .env file found
⚠️  AIPROJECT_ENDPOINT not set (will be provided at workshop)
⚠️  AZURE_OPENAI_ENDPOINT not set (will be provided at workshop)
✅ Azure CLI available
✅ Node.js 20.x — OK (Lab 2)
```

The two `⚠️` warnings about endpoints are **expected** before the workshop. Everything else should be green.

If you see **any** ❌ on a package import, fix it on your machine **before** the workshop — proctors will not have time to debug environment issues during labs.

### Step 7 — Cache the Azure CLI bits we'll use

```bash
az extension add --name ml --yes 2>$null   # PowerShell
# or
az extension add --name ml --yes           # bash
```

This ensures the ML extension is locally available; the labs don't strictly require it but it speeds up some `az ai` flows.

---

## 🔍 Pre-Workshop Verification Checklist

Tick every box **before** arriving. If any item is unchecked, you risk losing lab time.

**Software**
- [ ] Python 3.11 or 3.12 installed (`python --version`)
- [ ] Git installed (`git --version`)
- [ ] VS Code installed with the Python extension
- [ ] Azure CLI installed (`az version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Microsoft Authenticator installed and your sandbox account configured

**Repo + environment**
- [ ] Repository cloned and you can `cd Agents-with-Azure-AI-Foundry-v2-Labs`
- [ ] `.env` file exists (copied from `.env.example`)
- [ ] `.venv` created and activated (prompt shows `(.venv)`)
- [ ] `pip install` ran successfully for **all 5** requirements files (shared + 4 labs)
- [ ] `npx @modelcontextprotocol/server-everything --help` runs without error
- [ ] `python shared/verify_setup.py` shows **all green** (the two endpoint warnings are OK)

**Azure access**
- [ ] You received your sandbox credentials email
- [ ] `az login` succeeds
- [ ] `az account show` returns the sandbox subscription (not your corporate sub)

**On workshop day — first 5 minutes**

When you sit down:

1. Activate the venv: `.venv\Scripts\Activate.ps1` (or `source .venv/bin/activate`)
2. Paste the values the instructor gives you into `.env`
3. Run `python shared/verify_setup.py` one more time — confirm endpoint warnings are now ✅
4. Open Lab 1 and start

That's it. No installs. No "wait, my pip is stuck." Straight to the lab.

---

## 📚 Workshop Labs Overview

### Lab 1 — Your First Multi-Agent System on Azure AI Agent Service
**⏱ 35 minutes**

Build a multi-agent research pipeline using the Azure AI Foundry v2 agents SDK. You'll create a `ResearcherAgent` (with Bing grounding for web search), a `WriterAgent` (for synthesizing reports), and an `Orchestrator` that coordinates them end-to-end.

**You'll learn:** Agent creation, BingGroundingTool, ToolSet, AgentThread lifecycle, agent-to-agent orchestration patterns.

> The directory name `lab1-multi-agent-maf` is retained for backward-compat with earlier workshop links. The lab uses the Foundry Agent Service SDK directly — no separate MAF runtime is required.

---

### Lab 2 — MCP Power Hour: Connect Anything in Minutes
**⏱ 40 minutes**

Build a custom MCP (Model Context Protocol) server that exposes tools, then connect an Azure AI agent to consume those tools. Understand how MCP enables pluggable, reusable tool infrastructure that any LLM can call.

**You'll learn:** MCP server implementation, stdio transport, tool schema definition, connecting Azure AI agents to external tool servers.

---

### Lab 3 — Deploy & Observe: Foundry Agent Service + Tracing
**⏱ 35 minutes**

Instrument an agent with OpenTelemetry tracing, deploy it to Azure AI Agent Service, and observe execution traces in the Azure portal. Learn to interpret spans, tool calls, and latency from real agent runs.

**You'll learn:** OpenTelemetry setup, `AIInstrumentor`, Azure Monitor exporter, trace visualization in the Foundry portal, custom span attributes.

---

### Lab 4 — Ship It: Evaluate, Iterate, Promote
**⏱ 35 minutes**

Add a quality gate using Azure AI Evaluation. Run Groundedness, Coherence, Relevance, and a deterministic citation evaluator against the agent's **live** responses. Watch a weak instruction set fail the gate, fix it, watch the strong version pass, then promote the agent by stamping metadata and surfacing the Foundry Playground URL.

**You'll learn:** `azure-ai-evaluation` SDK with live agent targets, weak→strong iteration loops, deterministic + LLM-judge evaluator blends, tolerant metric-key lookup, metadata-driven agent promotion.

> The directory name `lab4-eval-teams` is retained for backward-compat. The Teams deployment step has been removed — in Foundry v2 the realistic promotion artifact is metadata + a Playground URL, not a Teams app package.

---

## ❓ Troubleshooting

### `az login` fails or loops

- Make sure Microsoft Authenticator is set up and you have a valid account
- Try: `az login --use-device-code` and follow the browser prompt
- Check if a corporate firewall or VPN is blocking `login.microsoftonline.com`

### Wrong Python version

- Confirm with `python --version` — needs 3.11+
- On some systems, `python3` is the correct command; use `python3 -m venv .venv` accordingly
- If you have multiple versions, use `py -3.11 -m venv .venv` on Windows

### Package install failures

- Make sure your virtual environment is **activated** (you should see `(.venv)` in your prompt)
- Try: `pip install --upgrade pip` then retry
- Corporate proxies: `pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r shared/requirements.txt`

### Network / proxy issues

- Check if your corporate proxy blocks `*.azureml.ms` or `*.api.azureml.ms`
- Workshop Wi-Fi is unrestricted — connecting to it resolves most proxy issues
- Ask a proctor if you suspect environment-level restrictions

### "Module not found" errors

- Confirm the virtual environment is activated before running any scripts
- Re-run `pip install -r shared/requirements.txt`
- For lab-specific issues, each lab has its own `requirements.txt` — install that too

### General issues during labs

- **Raise your hand** — proctors are walking the room throughout the workshop
- Ask your neighbour — pairing is encouraged!
- Check the `solution/` folder in each lab if you're stuck and want to compare

---

*See you at the workshop! 🚀*
