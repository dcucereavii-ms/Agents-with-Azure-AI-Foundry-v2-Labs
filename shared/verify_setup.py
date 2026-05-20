#!/usr/bin/env python3
"""
Verify the workshop environment is correctly set up.

Run this from the repo root *after* installing each lab's requirements:

    python shared/verify_setup.py

Checks:
  - Python 3.10+
  - All SDK classes used by Labs 1-4 are importable (catches version drift)
  - .env file exists
  - AIPROJECT_ENDPOINT looks plausible (warning only)
  - Azure CLI is installed
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

# (module_path, class_or_attr_name, used_by_lab) — class-level imports catch
# breakage that simple `import` checks miss.
SDK_IMPORTS = [
    # core (every lab) -- Foundry v2 SDK
    ("azure.ai.projects",                 "AIProjectClient",           "all"),
    ("azure.ai.projects.models",          "PromptAgentDefinition",     "all"),
    ("azure.identity",                    "DefaultAzureCredential",    "all"),
    ("dotenv",                            "load_dotenv",               "all"),
    ("rich.console",                      "Console",                   "all"),
    # Microsoft Agent Framework (labs 1-3 orchestration layer)
    ("agent_framework",                   "Message",                   "1,2,3"),
    ("agent_framework.foundry",           "FoundryAgent",              "1,2,3"),
    ("agent_framework.orchestrations",    "SequentialBuilder",         "1"),
    # Lab 1
    ("azure.ai.projects.models",          "CodeInterpreterTool",       "1,3"),
    # Lab 2 -- MCPTool is provided by azure-ai-projects (Foundry v2)
    ("azure.ai.projects.models",          "MCPTool",                   "2"),
    # mcp client SDK is used by the local mcp_server.py demo
    ("mcp",                               "types",                     "2"),
    ("mcp.server",                        "Server",                    "2"),
    # Lab 3 -- tracing
    ("azure.monitor.opentelemetry",       "configure_azure_monitor",   "3"),
    ("opentelemetry",                     "trace",                     "3"),
    # Lab 4 -- still uses classic azure-ai-agents for run polling + evaluators
    ("azure.ai.agents.models",            "RunStatus",                 "4"),
    ("azure.ai.evaluation",               "GroundednessEvaluator",     "4"),
    ("azure.ai.evaluation",               "CoherenceEvaluator",        "4"),
    ("azure.ai.evaluation",               "RelevanceEvaluator",        "4"),
    ("azure.ai.evaluation",               "evaluate",                  "4"),
]

GREEN, RED, YELLOW, RESET, BOLD = "\033[92m", "\033[91m", "\033[93m", "\033[0m", "\033[1m"


def check(label, ok, warn=False, detail=""):
    symbol = f"{GREEN}OK{RESET}" if ok else (f"{YELLOW}WARN{RESET}" if warn else f"{RED}FAIL{RESET}")
    suffix = f"  {detail}" if detail else ""
    print(f"  [{symbol}] {label}{suffix}")
    return ok or warn


def main():
    print(f"\n{BOLD}=== Workshop Environment Verification ==={RESET}\n")
    results = []

    # Python version (MAF requires 3.10+)
    major, minor = sys.version_info.major, sys.version_info.minor
    ver_ok = (major == 3 and minor >= 10)
    results.append(check(
        f"Python {major}.{minor}.{sys.version_info.micro}",
        ver_ok,
        detail="(need 3.10+)" if not ver_ok else "",
    ))

    # SDK class-level imports
    print()
    failed_labs = set()
    for module_path, attr_name, used_by in SDK_IMPORTS:
        label = f"{module_path}.{attr_name}  [lab {used_by}]"
        try:
            module = importlib.import_module(module_path)
            if not hasattr(module, attr_name):
                results.append(check(label, False, detail=f"attribute missing — SDK version drift"))
                failed_labs.add(used_by)
            else:
                results.append(check(label, True))
        except ImportError as e:
            results.append(check(label, False, detail=f"{type(e).__name__}: {e}"))
            failed_labs.add(used_by)

    # .env file
    print()
    repo_root = Path(__file__).resolve().parent.parent
    env_path = repo_root / ".env"
    env_exists = env_path.exists()
    results.append(check(
        ".env file present",
        env_exists,
        detail=str(env_path) if env_exists else "copy .env.example to .env",
    ))

    if env_exists:
        from dotenv import load_dotenv
        load_dotenv(env_path)

    endpoint = os.environ.get("AIPROJECT_ENDPOINT", "")
    endpoint_set = bool(endpoint) and "<" not in endpoint
    results.append(check(
        "AIPROJECT_ENDPOINT set",
        endpoint_set,
        warn=not endpoint_set,
        detail="will be provided at workshop" if not endpoint_set else "",
    ))

    # Azure CLI
    print()
    try:
        result = subprocess.run(
            ["az", "version", "--output", "json"],
            capture_output=True, text=True, timeout=10,
        )
        az_ok = result.returncode == 0
        results.append(check("Azure CLI available", az_ok,
                             detail="" if az_ok else "install from aka.ms/installazurecli"))
    except (FileNotFoundError, subprocess.TimeoutExpired):
        results.append(check("Azure CLI available", False,
                             detail="install from aka.ms/installazurecli"))

    # Summary
    passes = sum(results)
    total = len(results)
    print(f"\n{BOLD}Result: {passes}/{total} checks passed{RESET}")

    if passes == total:
        print(f"\n{GREEN}{BOLD}All checks passed — you're ready for the workshop.{RESET}\n")
        return 0

    if failed_labs:
        print(f"\n{YELLOW}SDK import failures affect lab(s): {', '.join(sorted(failed_labs))}{RESET}")
        print(f"Run:  pip install -r lab<N>/requirements.txt")

    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
