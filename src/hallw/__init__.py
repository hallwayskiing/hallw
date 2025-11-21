"""
HALLW - Hyper-Automation-Large-Language-Wizard

An autonomous AI agent framework for browser automation and file operations.
"""

__version__ = "0.2.0"
__author__ = "Ethan Nie"
__email__ = "ethannie88@gmail.com"

from hallw.agent_graph import build_graph
from hallw.agent_state import AgentState
from hallw.utils.config_mgr import config

__all__ = [
    "__version__",
    "build_graph",
    "AgentState",
    "config",
]
