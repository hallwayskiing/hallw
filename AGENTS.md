# AGENTS.md

This document provides a comprehensive overview of the HALLW (Heuristic Autonomous Logic Loop Worker) project structure and architecture, designed to help Agents quickly understand the codebase.

## 1. Project Identity

*   **Name:** HALLW
*   **Purpose:** Autonomous desktop AI agent framework.
*   **Core Technologies:**
    *   **Backend:** Python 3.12+, LangGraph (State Machine), Playwright (Browser Automation), FastAPI/Uvicorn (Server).
    *   **Frontend:** Electron, React 19, Vite, TailwindCSS, Zustand.
    *   **Communication:** Socket.io (Real-time bidirectional events).
    *   **Package Manager:** `uv` (Python), `npm` (Node.js).

## 2. Directory Structure

### Root Directory
*   `main.py`: **Entry Point**. Starts the backend server and Electron app.
*   `pyproject.toml` & `uv.lock`: Python dependency management.
*   `start.bat` / `start.sh`: One-click startup scripts.
*   `.env`: Configuration (API keys, settings).
*   `workspace/`: **Agent Working Directory**. Files created/modified by the agent should go here.

### Backend (`src/hallw/`)
The core logic resides here.
*   **`core/`**: The brain of the agent.
    *   `agent_graph.py`: Defines the LangGraph state machine (nodes, edges).
    *   `agent_task.py`: Manages task breakdown and execution.
    *   `agent_event_dispatcher.py`: Handles event emission to the frontend.
*   **`server/`**: The API layer.
    *   `server.py`: Sets up the Socket.io server and endpoints.
    *   `socket_renderer.py`: Bridges backend events to frontend UI updates.
*   **`tools/`**: Tool implementations.
*   **`utils/`**: Helper functions (logging, config parsing).

### Frontend (`frontend/`)
A modern React + Electron application with feature-based architecture.
*   **`package.json`**: Frontend dependencies.
*   **`src/renderer/`**: React application code.
    *   `src/renderer/features`: Main features.
    *   `src/renderer/store`: Global Zustand state stores.
*   **`src/main/`**: Electron main process code.

### Workspace (`workspace/`)
All the works done by the agent should be saved here.

## 3. Architecture & Data Flow

1.  **User Input**: User types a prompt in the Electron frontend.
2.  **Socket Event**: Frontend sends an event (e.g., `user_input`) to the Python backend via Socket.io.
3.  **Agent Core**:
    *   `server.py` receives the input.
    *   A task is created by `agent_task.py`.
    *   Core workflow runs in `agent_graph.py`.
4.  **Tool Execution**:
    *   If a tool is called (e.g., `browser_init`), it executes in `src/hallw/tools`.
    *   Results are fed back into the graph state.
5.  **UI Update**:
    *   `agent_event_dispatcher.py` emits events (e.g., `tool_start`, `tool_end`).
    *   Frontend listens for these events and updates the Zustand store, which triggers a React re-render.

## 4. Key Development Commands

| Action | Command | Context |
| :--- | :--- | :--- |
| **Install Python Deps** | `uv sync` | Root |
| **Add Python Deps** | `uv add <package>` | Root |
| **Run Full App** | `python main.py` | Root |
| **Install JS Deps** | `npm install` | `frontend/` |
| **Run Frontend Dev** | `npm run dev` | `frontend/` |
| **Build Frontend** | `npm run build` | `frontend/` |

## 5. Agent Guidelines

*   **Core Agent**: Core workflow is defined in `src/hallw/core/agent_graph.py`
*   **Adding Tools**: Create a new file in `src/hallw/tools/`, define a `@tool` decorated function, and it will be auto-discovered.
*   **Frontend-Backend Sync**: Ensure Socket.io event names match in both `src/hallw/server/server.py` and `frontend/src/renderer/store/slices/socketSlice.ts`.
