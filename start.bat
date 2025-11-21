@echo off
setlocal enabledelayedexpansion

set "REPO_DIR=%~dp0"
pushd "%REPO_DIR%" >nul

:: ==========================================
:: 1. Check and Install uv (Bootstrapping)
:: ==========================================
:: Check if 'uv' is available in the PATH
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [SETUP] 'uv' tool not found. Attempting to install...

    :: Attempt to install uv using system pip
    :: Note: This assumes Python is installed. For a zero-dependency setup,
    :: you could swap this with the PowerShell download script.
    python -m pip install uv
    if errorlevel 1 (
        echo [ERROR] Failed to install uv. Please install it manually: pip install uv
        goto :fail
    )
)

:: ==========================================
:: 2. Sync Environment (The Magic Step)
:: ==========================================
:: 'uv sync' handles everything:
:: 1. Creates the virtual environment (.venv) if it doesn't exist.
:: 2. Reads pyproject.toml and uv.lock.
:: 3. Installs/Updates dependencies to match the lock file exactly.
echo [SETUP] Syncing environment and dependencies with uv...
uv sync --no-group dev
if errorlevel 1 goto :fail

:: ==========================================
:: 3. Handle Playwright Binaries
:: ==========================================
:: Use 'uv run' to execute commands inside the virtual environment without explicit activation.
echo [SETUP] Verifying Playwright browser binaries...
uv run playwright install chromium
if errorlevel 1 (
    echo [WARN] Browser install failed. You may need to check your internet connection.
)

:: ==========================================
:: 4. Launch Application
:: ==========================================
:: Check for .env configuration
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [WARN] .env file created from template. Please configure your API keys!
    )
)

echo [RUN] Launching HALLW with uv...
:: 'uv run' automatically injects the .venv environment variables.
uv run main.py %*
set "EXIT_CODE=%errorlevel%"
goto :cleanup

:fail
set "EXIT_CODE=%errorlevel%"
echo [ERROR] Startup failed.

:cleanup
popd >nul 2>&1
if %EXIT_CODE% neq 0 pause
exit /b %EXIT_CODE%
