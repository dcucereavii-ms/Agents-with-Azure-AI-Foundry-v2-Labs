#!/usr/bin/env bash
# One-shot pre-workshop setup for macOS / Linux.
# Run from the repo root:
#   ./scripts/setup.sh
#
# Idempotent: re-running is safe.

set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Azure AI Foundry v2 Workshop — Pre-Setup ==="
echo

# 1. Python version check
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ python3 not found. Install Python 3.11 or 3.12 first: https://www.python.org/downloads/"
    exit 1
fi
echo "✓ $(python3 --version)"

# 2. .env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env from .env.example"
else
    echo "✓ .env already exists"
fi

# 3. Virtualenv
if [ ! -d .venv ]; then
    echo "→ Creating virtual environment .venv ..."
    python3 -m venv .venv
fi
echo "✓ .venv ready"

# 4. Activate venv for this session
# shellcheck disable=SC1091
source .venv/bin/activate
echo "✓ venv activated"

# 5. Upgrade pip
echo "→ Upgrading pip ..."
python -m pip install --upgrade pip --quiet

# 6. Install all lab requirements
for r in \
    shared/requirements.txt \
    lab1-multi-agent-maf/requirements.txt \
    lab2-mcp-connect/requirements.txt \
    lab3-deploy-observe/requirements.txt \
    lab4-eval-teams/requirements.txt; do
    echo "→ pip install -r $r"
    pip install -r "$r" --quiet
done
echo "✓ All Python dependencies installed"

# 7. Pre-cache the MCP server used by Lab 2
echo "→ Pre-caching Lab 2 MCP server (npx) ..."
if command -v npx >/dev/null 2>&1; then
    npx -y @modelcontextprotocol/server-everything --help >/dev/null 2>&1 \
        && echo "✓ Lab 2 MCP server cached" \
        || echo "⚠️  npx ran but server-everything failed — re-check before the workshop"
else
    echo "⚠️  npx not found — install Node.js 18+ before the workshop"
fi

# 8. Verify
echo
echo "=== Running verify_setup.py ==="
python shared/verify_setup.py

echo
echo "Done. You're ready for the workshop."
echo "On workshop day: activate the venv, paste endpoints into .env, run verify_setup.py once more, then start Lab 1."
