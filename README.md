# From Prototype to Production: Building Real Agents with Azure AI Foundry v2

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

## 📦 Clone the Repository

```bash
git clone https://github.com/dcucereavii-ms/Agents-with-Azure-AI-Foundry-v2-Labs.git
cd Agents-with-Azure-AI-Foundry-v2-Labs
```

You should see four lab directories: `lab1-multi-agent-maf`, `lab2-mcp-connect`, `lab3-deploy-observe`, `lab4-eval-teams`.

---

## ⚡ Pre-Lab Environment Setup

Complete these steps after cloning the repo:

### Step 1 — Create your `.env` file

```bash
cp .env.example .env
```

> The `.env` values will be provided by the instructor at the start of the workshop. You do not need to fill them in ahead of time — just confirm the file exists.

### Step 2 — Create a virtual environment

```bash
python -m venv .venv
```

**Activate it:**

```bash
# Windows (Command Prompt / PowerShell)
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

You should see `(.venv)` at the start of your terminal prompt.

### Step 3 — Install base dependencies

```bash
pip install -r shared/requirements.txt
```

### Step 4 — Verify your setup

```bash
python shared/verify_setup.py
```

A successful run looks like:
```
✅ Python 3.11.9 — OK
✅ azure-ai-projects — importable
✅ azure-identity — importable
✅ .env file found
⚠️  AIPROJECT_ENDPOINT not set (will be provided at workshop)
✅ Azure CLI available
```

The `AIPROJECT_ENDPOINT` warning is expected at this stage — you'll fill it in at the workshop.

---

## 🔍 Quick Verification Checklist

Before arriving, confirm all of the following:

- [ ] Python 3.11+ is installed (`python --version`)
- [ ] Git is installed (`git --version`)
- [ ] VS Code is installed with the Python extension
- [ ] Azure CLI is installed (`az version`)
- [ ] `az login` works and you can reach your sandbox subscription
- [ ] Node.js 18+ is installed (`node --version`)
- [ ] Repository is cloned and you can `cd` into it
- [ ] Virtual environment created and `pip install -r shared/requirements.txt` succeeds
- [ ] `python shared/verify_setup.py` runs without errors
- [ ] Microsoft Authenticator is installed and your account is configured

---

## 📚 Workshop Labs Overview

### Lab 1 — Your First Multi-Agent System with Microsoft Agent Framework
**⏱ 35 minutes**

Build a multi-agent research pipeline using the Azure AI Foundry v2 agents SDK. You'll create a `ResearcherAgent` (with Bing grounding for web search), a `WriterAgent` (for synthesizing reports), and an `Orchestrator` that coordinates them end-to-end.

**You'll learn:** Agent creation, BingGroundingTool, ToolSet, AgentThread lifecycle, agent-to-agent orchestration patterns.

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

### Lab 4 — Ship It: Eval Gate + Live Deployment to Teams
**⏱ 35 minutes**

Add a quality gate using Azure AI Evaluation before deploying. Run Groundedness, Coherence, and Relevance evaluators on agent responses, implement a pass/fail threshold gate, and configure the agent for Microsoft Teams deployment.

**You'll learn:** `azure-ai-evaluation` SDK, evaluation datasets, scoring thresholds, Teams channel configuration via Azure AI Foundry portal.

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
