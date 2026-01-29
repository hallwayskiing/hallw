# HALLW 🤖

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.12+-yellow.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Framework-blue.svg)](https://github.com/langchain-ai/langgraph)
[![Playwright](https://img.shields.io/badge/Playwright-Automation-green.svg)](https://playwright.dev/)

<div align='center'>

https://github.com/user-attachments/assets/e1dcae67-f06e-4412-8a2c-3e4ac02e691e

<p><em>Demo for 'Summarize today's tech headlines and save as tech_news.md'</em></p>
</div>

**HALLW** (Heuristic Autonomous Logic Loop Worker) is an autonomous desktop AI agent framework. It leverages **LangGraph** and **Playwright** to intelligently browse the web, manage local files, and self-correct through reflection loops.

> **Simply tell it what to do, and watch it work.**

## ✨ Key Features

### 🧠 Advanced Reasoning Engine

  - **Stage Building**: Automatically deconstructs complex task into multiple stages.
  - **Self Correcting**: Uses a **Reflection Loop**. If fails occur and accumulate to the threshold, the agent analyzes the error and tries a different strategy automatically.
  - **State Machine**: Built on **LangGraph**, ensuring deterministic state transitions and memory management.
  - **Model Agnostic**: Works with any OpenAI-compatible API

### 🌐 Autonomous Browser Control

  - **Full Interaction**: Clicks, types, and navigates websites like a human via Chrome DevTools Protocol (CDP).
  - **Smart Search**: Performs Google searches and intelligently parses results.
  - **Resilient**: Handles timeouts, CAPTCHA (manual intervention), and dynamic content loading.
  - **Profile Persistence**: Can use your local Chrome profile to skip logins and retain cookies.


### 📁 Local System Operations

  - **File Management**: Reads, writes, and analyzes local files (PDF, Markdown, Code, JSON).
  - **Data Extraction**: Scrapes web content and save it directly to local reports.

### 💻 System-level Command Execution
 - **System Commnd**: Provides system commands that directly control pc.
 - **Smart Adaption**: Smartly adapts to user's environment. (Powershell on Windows and bash on Linux)
 - **Safety Strategy**: Controlled by user's manual confirmation.

-----

## 🚀 Quick Start (For Users)

No coding knowledge required. Follow these steps to get started:

### 1\. Download & Prepare

Clone this repository or download the ZIP file.

```bash
git clone https://github.com/hallwayskiing/hallw.git
cd hallw
```

### 2\. Configure Environment

Copy the example configuration file and edit it with your API keys.

```bash
# Windows
copy .env.example .env
# Linux
cp .env.example .env
```

**Edit `.env`** and set your LLM credentials:

```env
MODEL_API_KEY=your-api-key-here
MODEL_NAME=gemini-2.5-flash
```

Copy the example PROFILE file, and fill out the fields to give the Agent your personal information, in order to better accomplish tasks.

```bash
# Windows
copy PROFILE.example PROFILE
# Linux
cp PROFILE.example PROFILE
```


### 3. Run!

- **Windows**: Double-click **`start.bat`** (or run it from PowerShell by `.\start.bat`).
- **Linux/macOS**: Make it executable once with `chmod +x start.sh`, then run `./start.sh`.

Both launchers automatically download uv, install dependencies, and start the Electron GUI window.

-----

## 💻 Usage (For Developers)

### Installation

```bash
# Install via uv (including dev dependencies)
uv sync

# Install browser binaries (Optional)
playwright install chromium
```

### Running Tasks

You can start the GUI window directly via `main.py`:

```bash
python main.py
```

-----

## ⚙️ Configuration Guide

All settings are managed via `.env`.

### 🧠 Model Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `MODEL_NAME` | The LLM model ID to use | `gemini-2.5-flash-lite` |
| `MODEL_ENDPOINT` | Base URL for the API | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| `MODEL_API_KEY` | **Required** API Key | - |
| `MODEL_TEMPERATURE` | Creativity (0.0 - 1.0) | `0.25` |

### 🌐 Browser Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `CHROME_USER_DATA_DIR` | Path to storage chrome user date | [.chrome_user_data/](./.chrome_user_data/) |
| `PW_HEADLESS_MODE` | Run without visible window (`True`/`False`) | `False` |
| `KEEP_PAGE_OPEN` | Keep pages open after task finishes | `True` |
| `SEARCH_RESULT_COUNT` | Google search depth | `10` |
| `PREFER_LOCAL_CHROME` | Use local chrome first | `True` |

### 📁 File System Settings
| Variable | Description | Default |
|----------|-------------|---------|
| `FILE_SAVE_DIR` |	Directory where the agent saves files |	workspace/ |
| `FILE_READ_DIR` |	Base directory allowed for reading files	| . |
| `FILE_MAX_READ_CHARS` |	Max characters to read from one file | 5000 |

-----

## 🏗️ Architecture

HALLW is built on a modular architecture designed for extensibility.

### Directory Structure

```text
hallw/
├── logs/                   # Task logs
├── src/                    # Source codes
│   └── hallw/              # Main Folder
│       ├── agent.py        # LangGraph State Machine
│       ├── tools/          # Auto-discovered Tool Modules
│       │   ├── playwright/ # Browser Tools
│       │   ├── file/       # File System Tools
│       │   └── system/     # System Command Tools
│       ├── ui/             # User Interface
│       └── utils/          # Config & Logger & Others
├── main.py                 # Application Entry Point
├── start.bat               # One-click Launcher
├── uv.lock                 # Frozen Dependencies
└── pyproject.toml          # Package Metadata
```

### Agent Workflow (The Graph)
```
                 +-----------------------+
                 |     🚀 User Task      |
                 +-----------+-----------+
                             |
                             v
          .-------------------------------------.
          |         🧠 AGENT CORE (LLM)         |
          |-------------------------------------|
          |                                     |
          |        +-------------------+        |
          |        |  🧮 Analyse Task  |        |
          |        +---------+---------+        |
          |                  |                  |
          |                  v                  |
          |        +-------------------+        |
          |        |  📝 Build Stages  |        |
          |        +---------+---------+        |
          |                  |                  |
          |                  v                  |
          |        +-------------------+        |
      +---|------> | ⚡Start New Stage |        |
      |   |        +---------+---------+        |
      |   |                  |                  |
      |   '------------------|------------------'
      |                      |
      |            +---------+---------+
      |            |                   |
      |        [Action]            [Finish]
      |            |                   |
      |            v                   v
      |   .-----------------.  +---------------------+
      |   |   🛠️ Execute    | |   ✨ Task Complete  |
      |   |-----------------|  +---------------------+
      |   | +-------------+ |
      |   | | 💻 Run Tool | |
      |   | +------+------+ |
      |   |        |        |
      |   |        v        |
      |   | < ✅ Success? > |
      |   '--------+--------'
      |            |
      |      +-----+-----+
      |      |           |
      |    [Yes]        [No]
      |      |           |
      |      |           v
      |      |   .-------------------------.
      |      |   |     🛡️ REFLECTION      |
      |      |   |------------------------ |
      |      |   |  <⚠️Retry Threshold? > |
      |      |   |    /            \       |
      |      |   |  (No)          (Yes)    |
      |      |   |   |              |      |
      |      |   |   v              v      |
      |      |   | [Retry]      [Reflect]  |
      |      |   |               & Plan    |
      |      |   '---+---------------+-----'
      |      |       |               |
      +------+-------+---------------+
```
1.  **Analyse**: The agent reads the state and conversation history.
2.  **Build**: The agent deconstructs the task into multiple stages.
3.  **Act**: The agent uses appropriate tools to finish current stage goal.
4.  **Reflect**: If an error occurs, the failure counter increments. If it hits the threshold, the agent enters **Reflection Mode** to analyze why it failed and plan a fix.

-----

## 🛠️ Extending HALLW

Adding new capabilities is easy thanks to the auto-discovery system.

1.  Create a new python file in `src/hallw/tools/`.
2.  Define a function decorated with `@tool`.
3.  It will be automatically loaded next time you run the agent.

<!-- end list -->

```python
# src/hallw/tools/my_custom_tool.py
from langchain_core.tools import tool

@tool
def get_system_time() -> str:
    """Returns the current system time."""
    import datetime
    return str(datetime.datetime.now())
```

-----

## ⚠️ Disclaimer & Security

  - **Local Access**: This agent runs locally on your machine. It has access to your file system and browser.
  - **API Costs**: Using LLMs (OpenAI, Gemini, etc.) may incur costs based on token usage.
  - **Sandboxing**: It is recommended to run this in a virtual machine or a controlled environment if you are executing untrusted prompts.

## 📄 License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](https://www.apache.org/licenses/LICENSE-2.0) file for details.

## 📮 Contact

**Author:** Ethan Nie
**GitHub:** [hallwayskiing](https://github.com/hallwayskiing)
**Issues:** Please report bugs via [GitHub Issues](https://github.com/hallwayskiing/hallw/issues).
