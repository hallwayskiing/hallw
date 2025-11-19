@echo off
setlocal enabledelayedexpansion

set "REPO_DIR=%~dp0"
pushd "%REPO_DIR%" >nul

:: ==========================================
:: 1. Check for active Conda environment
:: ==========================================
if defined CONDA_PREFIX (
    echo [INFO] Conda environment detected: %CONDA_DEFAULT_ENV%
    echo [INFO] Path: %CONDA_PREFIX%
    echo [INFO] Using active Conda environment - skipping .venv creation.

    REM Use the python executable from the current environment
    set "PYTHON_EXE=python"

    REM Skip venv setup and go directly to dependency installation
    goto :install_deps
)

:: ==========================================
:: 2. (Fallback) Standard Virtual Environment Setup
:: ==========================================
set "VENV_DIR=%REPO_DIR%\.venv"
set "PYTHON_EXE="

:: Find system Python executable
for %%P in (python.exe py.exe) do (
    where %%P >nul 2>&1
    if not errorlevel 1 if not defined PYTHON_EXE set "PYTHON_EXE=%%P"
)

if not defined PYTHON_EXE (
    echo [ERROR] Python 3 is required but was not found on PATH.
    echo [HINT] Please install Python from python.org and check "Add to PATH".
    goto :cleanup
)

:: Create .venv if it doesn't exist
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [SETUP] Virtual environment not found. Creating in .venv...
    "%PYTHON_EXE%" -m venv "%VENV_DIR%"
    if errorlevel 1 goto :fail
)

:: Activate .venv
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 goto :fail


:: ==========================================
:: 3. Install Dependencies
:: ==========================================
:install_deps

echo [SETUP] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

echo [SETUP] Installing project dependencies (editable mode)...
pip install -e .
if errorlevel 1 goto :fail

echo [SETUP] Verifying Playwright browser binaries...
python -m playwright install chromium >nul 2>&1
if errorlevel 1 (
    echo [WARN] Automated browser install failed. You may need to run 'playwright install' manually.
)

:: ==========================================
:: 4. Launch Application
:: ==========================================
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [WARN] .env file created from template. Please configure your API keys!
    )
)

echo [RUN] Launching HALLW...
python main.py %*
set "EXIT_CODE=%errorlevel%"
goto :cleanup

:fail
set "EXIT_CODE=%errorlevel%"
echo [ERROR] Startup failed with exit code %EXIT_CODE%.

:cleanup
popd >nul 2>&1
echo [INFO] Process finished. Press any key to exit.
pause >nul
exit /b %EXIT_CODE%
