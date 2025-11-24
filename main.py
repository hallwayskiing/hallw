import sys
import uuid
import warnings
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from PySide6.QtWidgets import QApplication

from hallw.core import AgentState, AgentTask
from hallw.tools import load_tools
from hallw.ui.pyside import QtAgentMainWindow, QtAgentRenderer, QtAgentThread
from hallw.utils import config, generatePrompt, init_logger, logger

# Ignore specific warnings from LangSmith about UUID v7
warnings.filterwarnings("ignore", message=".*LangSmith now uses UUID v7.*")


def _patch_windows_asyncio():
    """Fix RuntimeError when closing asyncio event loop on Windows"""
    if sys.platform.startswith("win"):
        from asyncio.proactor_events import _ProactorBasePipeTransport

        def silence_event_loop_closed(self):
            pass

        _ProactorBasePipeTransport.__del__ = silence_event_loop_closed  # type: ignore


class AgentApplication:
    """Agent application controller responsible for managing GUI and thread lifecycle"""

    def __init__(self):
        _patch_windows_asyncio()

        # Initialize Qt application
        self.app = QApplication(sys.argv)

        # Core components
        self.renderer = QtAgentRenderer()
        self.window = QtAgentMainWindow(self.renderer, self.start_task)

        # State maintenance
        self.worker: Optional[QtAgentThread] = None
        self.tools_dict = load_tools()

    def _create_initial_state(self, user_task: str) -> AgentState:
        """Construct the initial Agent state"""
        return {
            "messages": [
                SystemMessage(content=generatePrompt(user_task, self.tools_dict)),
                HumanMessage(
                    content=(
                        f"Think step-by-step, plan your actions, and use proper tools to "
                        f"complete the task: {user_task}"
                    )
                ),
            ],
            "task_completed": False,
            "stats": {
                "tool_call_counts": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "failures": 0,
                "failures_since_last_reflection": 0,
            },
        }

    def _build_agent_task(self, user_task: str) -> Optional[AgentTask]:
        """Construct AgentTask instance"""
        api_key = config.model_api_key.get_secret_value() if config.model_api_key else None

        task_id = str(uuid.uuid4())
        init_logger(task_id)
        logger.info(f"Starting task: {user_task}, ID: {task_id}")

        llm = ChatOpenAI(
            model=config.model_name,
            base_url=config.model_endpoint,
            api_key=api_key,
            temperature=config.model_temperature,
            max_tokens=config.model_max_output_tokens,
            streaming=True,
            stream_usage=True,
        ).bind_tools(list(self.tools_dict.values()), tool_choice="auto")

        checkpointer = MemorySaver()

        return AgentTask(
            task_id=task_id,
            llm=llm,
            tools_dict=self.tools_dict,
            renderer=self.renderer,
            initial_state=self._create_initial_state(user_task),
            checkpointer=checkpointer,
        )

    def start_task(self, user_task: str):
        """Handle signal to start a task"""
        # If an old task is running, stop it first
        if self.worker and self.worker.isRunning():
            logger.warning("Stopping previous task...")
            self.worker.terminate()
            self.worker.wait()

        agent_task = self._build_agent_task(user_task)
        if not agent_task:
            return

        # Start worker thread
        self.worker = QtAgentThread(agent_task)
        self.worker.finished.connect(self.renderer.task_finished.emit)
        # Explicitly handle cleanup after thread finishes to prevent zombie objects
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def run(self):
        self.window.show()
        sys.exit(self.app.exec())


def main():
    app = AgentApplication()
    app.run()


if __name__ == "__main__":
    main()
