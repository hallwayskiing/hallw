import sys
import uuid
import warnings
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from PySide6.QtWidgets import QApplication

from hallw.core import AgentEventLoop, AgentState, AgentTask
from hallw.tools import load_tools
from hallw.ui.pyside import QtAgentMainWindow, QtAgentRenderer, QtAgentThread
from hallw.utils import config, generateSystemPrompt, init_logger, logger

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

        # Set up asyncio event loop
        self.event_loop = AgentEventLoop()

        # Core components
        self.renderer = QtAgentRenderer()
        self.window = QtAgentMainWindow(self.renderer, self.start_task, self.stop_task)

        # State maintenance
        self.worker: Optional[QtAgentThread] = None
        self.tools_dict = load_tools()
        self.checkpointer = MemorySaver()
        self.thread_id = str(uuid.uuid4())
        self.is_first_task = True

        # Initialize logger
        init_logger(self.thread_id)

    def _create_initial_state(self, user_task: str) -> AgentState:
        """Construct the initial Agent state"""
        messages = []
        if self.is_first_task:
            messages.append(SystemMessage(content=generateSystemPrompt(self.tools_dict)))
            self.is_first_task = False

        messages.append(HumanMessage(content=(f"User: {user_task}")))
        logger.info(f"User: {user_task}")

        return {
            "messages": messages,
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

        # Use persistent thread_id
        task_id = self.thread_id

        llm = ChatOpenAI(
            model=config.model_name,
            base_url=config.model_endpoint,
            api_key=api_key,
            temperature=config.model_temperature,
            max_tokens=config.model_max_output_tokens,
            streaming=True,
            stream_usage=True,
        ).bind_tools(list(self.tools_dict.values()), tool_choice="auto")

        return AgentTask(
            task_id=task_id,
            llm=llm,
            tools_dict=self.tools_dict,
            renderer=self.renderer,
            initial_state=self._create_initial_state(user_task),
            checkpointer=self.checkpointer,
            event_loop=self.event_loop,
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
        self.worker.start()

    def stop_task(self):
        """Handle signal to stop the current task"""
        if self.worker and self.worker.isRunning():
            logger.info("Stopping task by user request...")
            self.worker.terminate()
            self.worker.wait()

    def cleanup(self):
        """Clean up resources before application exit"""
        self.stop_task()
        self.event_loop.stop()
        self.app.quit()

    def run(self):
        self.event_loop.start()
        self.window.show()
        sys.exit(self.app.exec())


def main():
    app = AgentApplication()
    app.run()


if __name__ == "__main__":
    main()
