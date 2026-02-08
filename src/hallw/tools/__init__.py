import importlib
import inspect
import pkgutil
import sys
from typing import List

from langchain_core.tools import BaseTool, tool

from hallw.utils import logger

from .tool_response import ToolResult, build_tool_response, parse_tool_response


def _import_package_modules(package_name: str):
    """Recursively import all modules in a package so @tool decorators run."""
    package = importlib.import_module(package_name)
    if not hasattr(package, "__path__"):
        return
    for finder, name, ispkg in pkgutil.walk_packages(package.__path__, prefix=package_name + "."):
        try:
            importlib.import_module(name)
        except Exception as e:
            logger.error(f"Failed to import {name}: {e}")


def load_tools() -> dict[str, BaseTool]:
    tools_dict: dict[str, BaseTool] = {}
    tools_package_name = __name__
    # Import top-level modules and subpackages under tools
    _import_package_modules(tools_package_name)

    # Scan loaded modules for BaseTool instances
    for module_name, module in list(sys.modules.items()):
        if not module_name.startswith(tools_package_name + "."):
            continue
        try:
            for _, obj in inspect.getmembers(module):
                if isinstance(obj, BaseTool):
                    if obj.name in tools_dict:
                        logger.warning(
                            "Duplicate tool name '%s' found in module '%s' "
                            "(already registered from '%s'), overriding.",
                            obj.name,
                            module_name,
                            tools_dict[obj.name].__module__,
                        )
                    tools_dict[obj.name] = obj
        except Exception as e:
            logger.error(f"Failed to import {module_name}: {e}")
            continue
    return tools_dict


@tool
def dummy_for_missed_tool(name: str) -> str:
    """
    A dummy tool function that returns a "Tool Not Found" response.

    Args:
        name (str): The name of the missing tool.

    Returns:
        str: A standardized tool response indicating the tool was not found.
    """
    return build_tool_response(success=False, message=f"Tool {name} Not Found")


@tool
def build_stages(stage_names: List[str]) -> str:
    """
    Analyze the task and provide a list of stages with their corresponding names.

    Args:
        stage_names: A list of stage names.
    Returns:
        A formatted string listing the stages.
    """

    return build_tool_response(
        True,
        "Stages built successfully.",
        {
            "stage_names": stage_names,
        },
    )


__all__ = [
    "load_tools",
    "build_tool_response",
    "parse_tool_response",
    "dummy_for_missed_tool",
    "ToolResult",
    "build_stages",
]
