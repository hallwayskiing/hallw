import importlib
import inspect
import pkgutil
import sys

from langchain_core.tools import BaseTool

from hallw.utils import logger

from .tool_response import build_tool_response

tools_package_name = __name__
tools_dict = {}


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


# Import top-level modules and subpackages under tools
_import_package_modules(tools_package_name)

# Scan loaded modules for BaseTool instances
for module_name, module in list(sys.modules.items()):
    if not module_name.startswith(tools_package_name + "."):
        continue
    try:
        for _, obj in inspect.getmembers(module):
            if isinstance(obj, BaseTool):
                tools_dict[obj.name] = obj
    except Exception:
        continue

__all__ = ["tools_dict", "build_tool_response"]
