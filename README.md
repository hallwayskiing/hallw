# HALLW 🤖

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.14+-yellow.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Framework-blue.svg)](https://github.com/langchain-ai/langgraph)
[![Playwright](https://img.shields.io/badge/Playwright-Automation-green.svg)](https://playwright.dev/)

<div align='center'>

https://github.com/user-attachments/assets/0027e982-f924-4f14-b922-7c141804657d

<p><em>Demo for 'Collect latest 30 days NVIDIA stock price and save it to my desktop'</em></p>
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

## 🚀 Quick Start

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

**Edit `.env`** and set your providers API keys:

```env
MODEL_NAME=
OPENAI_API_KEY=
GOOGLE_API_KEY=
ANTHROPIC_API_KEY=
OPENROUTER_API_KEY=
DEEPSEEK_API_KEY=
ZAI_API_KEY=
MOONSHOT_API_KEY=
XIAOMI_MIMO_API_KEY=

```

Configure your Brave Search API key in the .env file.
```env
BRAVE_SEARCH_API_KEY=
```

### 3. Run!

- **Windows**: Double-click **`start.bat`** (or run it from PowerShell by `.\start.bat`).
- **Linux/macOS**: Make it executable once with `chmod +x start.sh`, then run `./start.sh`.

Both launchers automatically download uv, install dependencies, and start the Electron GUI window.

-----

## 💻 Manual Installation

### Installation

```bash
# Install via uv
uv sync

# Install browser binaries (Optional)
playwright install chromium
```

### Running Tasks

You can start both the backend + frontend via `main.py`:

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
| `OPENAI_API_BASE` | Base URL for the OpenAI compatible API | - |
| `ANTHROPIC_API_BASE` | Base URL for the Anthropic compatible API | - |
| `MODEL_TEMPERATURE` | Creativity (0.0 - 1.0) | `0.25` |
| `OPENAI_API_KEY` | OpenAI API Key | - |
| `GOOGLE_API_KEY` | Google API Key | - |
| `ANTHROPIC_API_KEY` | Anthropic API Key | - |
| `OPENROUTER_API_KEY` | OpenRouter API Key | - |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | - |
| `ZAI_API_KEY` | Zai API Key | - |
| `MOONSHOT_API_KEY` | Moonshot API Key | - |
| `XIAOMI_MIMO_API_KEY` | Xiaomi Mimo API Key | - |

### Exec & Search Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `ALLOW_AUTO_EXEC` | Allow auto execution | `False` |
| `ALLOW_AUTO_BLACKLIST` | Commands that still need confirmation | `[]` |
| `BRAVE_SEARCH_API_KEY` | Brave Search API key | - |
| `BRAVE_SEARCH_RESULT_COUNT` | Brave Search result count | `5` |

### 🌐 Browser Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `CHROME_USER_DATA_DIR` | Path to storage chrome user date | [.chrome_user_data/](./.chrome_user_data/) |
| `PW_HEADLESS_MODE` | Run without visible window (`True`/`False`) | `False` |
| `KEEP_PAGE_OPEN` | Keep pages open after task finishes | `True` |
| `PREFER_LOCAL_CHROME` | Use local chrome first | `True` |

-----

## 🏗️ Architecture

HALLW is built on a modular architecture designed for extensibility.

### Directory Structure

```text
hallw/
├── logs/                   # Task logs
├── frontend/               # Frontend
│   └── src/renderer/       # Main Electron Folder
│           ├── features/   # Features
│           ├── store/      # Zustand Store
│           ├── App.tsx     # Main App
│           └── main.tsx    # Main Entry Point
├── src/                    # Backend
│   └── hallw/              # Main Folder
│       ├── core/           # Core agent workflow
│       ├── server/         # Server codes
│       ├── tools/          # Tools codes
│       │   ├── playwright/ # Browser Tools
│       │   ├── interactive/# Interactive Tools
│       │   ├── search/     # Search Tools
│       │   └── system/     # System Command Tools
│       └── utils/          # Config & Logger & Others
├── main.py                 # Application Entry Point
├── workspace/              # Workspace
├── .env                    # Environment variables
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

## 🛠️ Extending

Adding new capabilities is easy thanks to the auto-discovery system.

1.  Create a new python file in `src/hallw/tools/`.
2.  Define a function decorated with `@tool`.
3.  It will be automatically loaded next time you run the agent.

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
