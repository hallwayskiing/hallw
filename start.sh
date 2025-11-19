#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# ==========================================
# 1. Check for active Conda environment
# ==========================================
# Check if CONDA_PREFIX is set and not empty
if [[ -n "${CONDA_PREFIX:-}" ]]; then
    echo "[INFO] Conda environment detected: ${CONDA_DEFAULT_ENV:-unknown}"
    echo "[INFO] Path: $CONDA_PREFIX"
    echo "[INFO] Using active Conda environment - skipping .venv creation."

    # Use the python executable from the current environment
    PYTHON_EXE="python"

else
    # ==========================================
    # 2. (Fallback) Standard Virtual Environment Setup
    # ==========================================
    VENV_DIR="$PROJECT_DIR/.venv"

    # Find system Python executable
    PY_CMD="${PYTHON:-}"
    if [[ -z "$PY_CMD" ]]; then
        if command -v python3 >/dev/null 2>&1; then
            PY_CMD="python3"
        elif command -v python >/dev/null 2>&1; then
            PY_CMD="python"
        else
            echo "[ERROR] Python 3 is required but was not found on PATH." >&2
            exit 1
        fi
    fi

    # Create .venv if it doesn't exist
    if [[ ! -x "$VENV_DIR/bin/python" ]]; then
        echo "[SETUP] Virtual environment not found. Creating in .venv ..."
        "$PY_CMD" -m venv "$VENV_DIR"
    fi

    # Activate virtual environment
    # shellcheck disable=SC1090
    source "$VENV_DIR/bin/activate"
    PYTHON_EXE="python"
fi

# ==========================================
# 3. Install Dependencies
# ==========================================

echo "[SETUP] Upgrading pip ..."
"$PYTHON_EXE" -m pip install --upgrade pip >/dev/null 2>&1

echo "[SETUP] Installing project dependencies (editable mode) ..."
# Output is not suppressed here to ensure errors are visible
pip install -e .

echo "[SETUP] Verifying Playwright browser binaries ..."
if ! "$PYTHON_EXE" -m playwright install chromium >/dev/null 2>&1; then
    echo "[WARN] Automated browser install failed. You may need to run 'playwright install' manually."
fi

# ==========================================
# 4. Launch Application
# ==========================================

if [[ ! -f ".env" ]]; then
    if [[ -f ".env.example" ]]; then
        cp .env.example .env
        echo "[WARN] .env file created from template. Please configure your API keys!"
    fi
fi

echo "[RUN] Launching HALLW ..."
"$PYTHON_EXE" main.py "$@"
