# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New: HALLW can execute system commands (powershell on Windows or bash on Linux) directly now.

## [0.6.0] - 2025-11-28

### Added
- Brand new graph logic: Auto-create multi-stages chain of actions at the start of every coversation, bringing far more effective workflow
- New Tools: `build_stages` and `end_current_stage` for models to explictly manage stages.

### Changed
- Adjusted and fixed UI logic for better user experiments

## [0.5.0] - 2025-11-25

### Added
- Added a EventBus to manage cross-module communications
- Added a Back button to reset the app
- New dependency: markdown for solving PySide compatiability
- Added HistoryLineEdit to reuse history inputs conveniently
- More tests

### Changed
- Rewrite Main Window for much better performance

## [0.4.0] - 2025-11-25

### Added
- Support multi-task calls in a window now
- Manual controlled event loop in `agent_event_loop.py`
- You can now edit and save settings in main window now

### Changed
- Merged `playwright_state.py` into `playwright_mgr.py`
- `playwright_mgr.py` maintains a `PlaywrightManager` class now
- Agent Graph is re-designed to support multi-task calls

### Removed
- Removed `ask_info.py`
- Removed `finish_task.py`
- Removed `playwright_state.py`

## [0.3.0] - 2025-11-23

### Added
- Brand new GUI with PySide6
- Multi-pages control of Agent

### Changed
- Core functions refactored and extracted into hallw/core
- Better error handling

## [0.2.0] - 2025-11-19

### Added
- Support stream output of LLM.
- Use Rich to build a friendly terminal user interface (TUI).
- Complete log system.

### Changed
- Improved file operations logic (path resolution and format handling).
- Switched to **uv** for package and environment management (replaced Conda/pip workflow).

### Removed
- Removed `requirements.txt` in favor of `uv.lock`.

## [0.1.0] - 2025-11-19

### Added
- Initial release of HALLW.
- Core agent functionality with LangGraph.
- Playwright browser automation tools:
  - `browser_goto`: Navigate to URLs.
  - `browser_click`: Click elements by ARIA role.
  - `browser_fill`: Fill form inputs.
  - `browser_search`: Google search with CAPTCHA detection.
  - `browser_get_content`: Extract page content.
  - `browser_get_structure`: Get page structure.
- File operation tools:
  - `file_read`: Read multiple file formats (txt, md, json, yaml, csv, html, pdf).
  - `file_save`: Save content to text files.
  - `file_append`: Append content to files.
  - `get_local_file_list`: List files with glob patterns.
- Utility tools:
  - `ask_for_more_info`: Interactive user queries.
  - `finish_task`: Task completion signal.
- Self-correcting mechanism with reflection.
- Comprehensive configuration via environment variables.
- Statistics tracking (tool calls, failures, token usage).

[Unreleased]: https://github.com/hallwayskiing/hallw/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/hallwayskiing/hallw/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/hallwayskiing/hallw/releases/tag/v0.1.0
