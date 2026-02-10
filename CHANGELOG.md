# Changelog

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v0.10.0 (2026-02-10)

### Feat

- **core**: add MODEL_REASONING_EFFORT configuration
- **ui**: add recently used models to choose in the settings
- **skills**: add stage-builder skill
- **tools**: add `browser_get_content` tool
- **core**: add support for model reasoning
- **ui**: add better light effects for dark mode
- **ui**: support light & dark mode switch
- **tools**: support Bocha Search Engine for Chinese users
- add frontend `npm install` step
- support DeepSeek and Xiaomi Mimo
- **tools**: create read & write tools for better file management
- **core**: support multi-provider api keys management

### Fix

- **ui**: avoid rendering empty bubbles
- **ui**: improve reasoning content rendering
- **server**: fix connection after refresh
- **ui**: fix fatal error renderring
- **core**: improve stability of tool calls
- **core**: refine data statistics and history message logics
- **ui**: refine ui logic on fatal error and cancellation

### Refactor

- **core**: decouple core components and improve agent stability
- **tools**: refactor browser management
- **core**: remove unused dependencies

## v0.9.0 (2026-02-08)

### Feat
- **ui**: use Zustand to manage component states and socket
- **ui**: refine Sidebar UI with auto-scaling
- **ui**: redesign welcome page with articles, animations and interactions
- **ui**: redesign settings page with better layout and controls
- **tools**: enable auto-allow exec with configurable blacklist

### Refactor
- **core**: migrate from langchain_openai to langchain_litellm for Gemini 3 Series support

## v0.8.0 (2026-02-07)

### Feat
- add user profile support
- add Claude Skills support
- add runtime user inputs

### Refactor
- search now uses Brave Search API instead of browser retrieval

### Breaking Changes
- remove `file` tools. `exec` replaced them all.

## v0.7.0 (2026-01-27)

### Feat
- HALLW can execute system commands (powershell on Windows or bash on Linux) directly now

### Refactor
- switch to `Electron` from `PySide6` for the GUI

## v0.6.0 (2025-11-28)

### Feat
- **core**: brand new graph logic: Auto-create multi-stages chain of actions
- **tools**: add `build_stages` and `end_current_stage` tools

### Fix
- **ui**: adjusted and fixed UI logic for better user experience

## v0.5.0 (2025-11-25)

### Feat
- add EventBus to manage cross-module communications
- add a Back button to reset the app
- add HistoryLineEdit to reuse history inputs conveniently
- add more tests

### Refactor
- **ui**: rewrite Main Window for much better performance

### Chore
- **deps**: add markdown for solving PySide compatibility

## v0.4.0 (2025-11-25)

### Feat
- support multi-task calls in a window
- add manual controlled event loop in `agent_event_loop.py`
- support edit and save settings in main window

### Refactor
- merge `playwright_state.py` into `playwright_mgr.py`
- **core**: re-design Agent Graph to support multi-task calls

### Breaking Changes
- remove `ask_info.py`, `finish_task.py`, and `playwright_state.py`

## v0.3.0 (2025-11-23)

### Feat
- brand new GUI with PySide6
- add multi-pages control of Agent

### Refactor
- **core**: extract core functions into `hallw/core`

### Fix
- improve error handling

## v0.2.0 (2025-11-19)

### Feat
- support stream output of LLM
- use Rich to build a friendly terminal user interface (TUI)
- add complete log system

### Refactor
- **core**: improve file operations logic
- **chore**: switch to **uv** for package management (replaced Conda/pip)

### Breaking Changes
- remove `requirements.txt` in favor of `uv.lock`

## v0.1.0 (2025-11-19)

### Feat
- initial release of HALLW
- **core**: core agent functionality with LangGraph
- **tools**: browser automation tools (goto, click, fill, search, etc.)
- **tools**: file operation tools (read, save, append, list)
- **core**: self-correcting mechanism with reflection
- **core**: statistics tracking (tool calls, failures, token usage)
