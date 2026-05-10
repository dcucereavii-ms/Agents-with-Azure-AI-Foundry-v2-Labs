#!/usr/bin/env python3
"""
Verify that the workshop environment is correctly set up.
Run this after completing the pre-lab setup steps in README.md.
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

REQUIRED_PACKAGES = [
    "azure.ai.projects",
    "azure.identity",
    "azure.monitor.opentelemetry",
    "opentelemetry",
    "dotenv",
    "rich",
]

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def check(label: str, ok: bool, warn: bool = False, detail: str = "") -> bool:
    if ok:
        symbol = f"{GREEN}✅{RESET}"
    elif warn:
        symbol = f"{YELLOW}⚠️ {RESET}"
    else:
        symbol = f"{RED}❌{RESET}"
    suffix = f"  {detail}" if detail else ""
    print(f"  {symbol}  {label}{suffix}")
    return ok


def main():
    print(f"\n{BOLD}=== Workshop Environment Verification ==={RESET}\n")
    results = []

    # Python version
    major, minor = sys.version_info.major, sys.version_info.minor
    ver_ok = (major == 3 and minor >= 11)
    results.append(check(
        f"Python {major}.{minor}.{sys.version_info.micro}",
        ver_ok,
        detail="(need 3.11+)" if not ver_ok else "— OK",
    ))

    # Required packages
    print()
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
            results.append(check(f"{pkg}", True, detail="— importable"))
        except ImportError:
            results.append(check(f"{pkg}", False, detail="— NOT FOUND (run: pip install -r shared/requirements.txt)"))

    # .env file
    print()
    env_path = Path(__file__).parent.parent / ".env"
    env_exists = env_path.exists()
    results.append(check(
        ".env file found",
        env_exists,
        detail=str(env_path) if env_exists else "— copy .env.example → .env",
    ))

    # AIPROJECT_ENDPOINT
    if env_exists:
        from dotenv import load_dotenv
        load_dotenv(env_path)

    endpoint = os.environ.get("AIPROJECT_ENDPOINT", "")
    endpoint_set = bool(endpoint) and "<" not in endpoint
    results.append(check(
        "AIPROJECT_ENDPOINT is set",
        endpoint_set,
        warn=not endpoint_set,
        detail="— will be provided at workshop" if not endpoint_set else f"→ {endpoint[:40]}...",
    ))

    # Azure CLI
    print()
    try:
        result = subprocess.run(
            ["az", "version", "--output", "json"],
            capture_output=True, text=True, timeout=10
        )
        az_ok = result.returncode == 0
        results.append(check("Azure CLI available", az_ok, detail="— found" if az_ok else "— not found (install from aka.ms/installazurecli)"))
    except (FileNotFoundError, subprocess.TimeoutExpired):
        results.append(check("Azure CLI available", False, detail="— not found (install from aka.ms/installazurecli)"))

    # Summary
    passes = sum(results)
    total = len(results)
    print(f"\n{BOLD}Result: {passes}/{total} checks passed{RESET}")

    if passes == total:
        print(f"\n{GREEN}{BOLD}🎉 All checks passed — you're ready for the workshop!{RESET}\n")
    elif passes >= total - 1:
        print(f"\n{YELLOW}Almost there — fix the items above before the workshop.{RESET}\n")
    else:
        print(f"\n{RED}Please fix the failing checks before the workshop.{RESET}")
        print(f"If you need help, contact the workshop team or raise your hand during setup.\n")


if __name__ == "__main__":
    main()
