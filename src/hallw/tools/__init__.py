import importlib
import inspect
import pkgutil

from langchain_core.tools import BaseTool

from .excludes.build_stages import build_stages
from .excludes.dummy_tool import dummy_for_missed_tool
from .stages.edit_stages import edit_stages
from .stages.end_stage import end_current_stage
from .utils.tool_response import ToolResult, build_tool_response, parse_tool_response

EXCLUDE_DIRS = ["excludes"]


def _import_package_modules(package_name: str, tools_dict: dict[str, BaseTool]):
    """Recursively import all modules in a package so @tool decorators run."""
    package = importlib.import_module(package_name)
    if not hasattr(package, "__path__"):
        return

    for info in pkgutil.walk_packages(package.__path__, prefix=package_name + "."):
        parts = info.name.split(".")
        if any(ex in parts for ex in EXCLUDE_DIRS):
            continue

        try:
            module = importlib.import_module(info.name)
            for _, obj in inspect.getmembers(module):
                if isinstance(obj, BaseTool):
                    if obj.name and obj.name not in tools_dict:
                        tools_dict[obj.name] = obj
        except Exception:
            continue


def load_tools() -> dict[str, BaseTool]:
    tools_dict: dict[str, BaseTool] = {}
    _import_package_modules(__name__, tools_dict)
    return tools_dict


__all__ = [
    "load_tools",
    "build_tool_response",
    "parse_tool_response",
    "dummy_for_missed_tool",
    "ToolResult",
    "build_stages",
    "edit_stages",
    "end_current_stage",
]
