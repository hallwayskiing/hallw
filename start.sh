#!/usr/bin/env bash
set -euo pipefail

# Ensure we are in the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# ==========================================
# 1. Check and Install uv
# ==========================================
if ! command -v uv >/dev/null 2>&1; then
    echo "[SETUP] 'uv' tool not found. Attempting to install..."

    if command -v pip3 >/dev/null 2>&1; then
        pip3 install uv
    elif command -v pip >/dev/null 2>&1; then
        pip install uv
    else
        echo "[INFO] pip not found. Trying official install script..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        [ -f "$HOME/.cargo/env" ] && source "$HOME/.cargo/env"
    fi

    if ! command -v uv >/dev/null 2>&1; then
        echo "[ERROR] Failed to install uv. Please install manually." >&2
        exit 1
    fi
fi

# ==========================================
# 2. Sync Environment
# ==========================================
echo "[SETUP] Syncing environment with uv..."
uv sync

# ==========================================
# 3. Install Frontend Dependencies
# ==========================================
echo "[SETUP] Installing frontend dependencies..."
pushd frontend > /dev/null
npm install
popd > /dev/null

# ==========================================
# 4. Launch Application
# ==========================================
if [[ ! -f ".env" ]]; then
    if [[ -f ".env.example" ]]; then
        cp .env.example .env
        echo "[WARN] .env file created from template. Please configure your API keys!"
    fi
fi

echo "[RUN] Launching HALLW with uv..."
uv run main.py "$@"
