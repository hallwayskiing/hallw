#!/usr/bin/env bash
set -euo pipefail

# Ensure we are in the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# ==========================================
# 1. Check and Install uv (Bootstrapping)
# ==========================================
# Check if 'uv' is available in the system PATH
if ! command -v uv >/dev/null 2>&1; then
    echo "[SETUP] 'uv' tool not found. Attempting to install..."

    # Attempt to install via pip (assuming python3 is available)
    if command -v pip3 >/dev/null 2>&1; then
        pip3 install uv
    elif command -v pip >/dev/null 2>&1; then
        pip install uv
    else
        # Fallback: If pip is missing, try the official install script
        echo "[INFO] pip not found. Trying official install script..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        # Source cargo env to make uv available immediately in this session
        [ -f "$HOME/.cargo/env" ] && source "$HOME/.cargo/env"
    fi

    # Final check
    if ! command -v uv >/dev/null 2>&1; then
        echo "[ERROR] Failed to install uv. Please install manually." >&2
        exit 1
    fi
fi

# ==========================================
# 2. Sync Environment
# ==========================================
# 'uv sync' ensures the .venv exists and matches uv.lock exactly.
# It replaces manual venv creation and 'pip install'.
echo "[SETUP] Syncing environment with uv..."
uv sync --no-group dev

# ==========================================
# 3. Handle Playwright Binaries
# ==========================================
# Use 'uv run' to execute the install command inside the project environment.
echo "[SETUP] Verifying Playwright browser binaries..."
if ! uv run playwright install chromium; then
    echo "[WARN] Browser install failed. Check your internet connection."
fi

# ==========================================
# 4. Launch Application
# ==========================================

# Check for .env configuration
if [[ ! -f ".env" ]]; then
    if [[ -f ".env.example" ]]; then
        cp .env.example .env
        echo "[WARN] .env file created from template. Please configure your API keys!"
    fi
fi

echo "[RUN] Launching HALLW with uv..."
# 'uv run' temporarily loads the .venv variables and executes the script
uv run main.py "$@"
