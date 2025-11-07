"""Public alias module so the package can be imported as `eigen`."""
"""Public alias module so the package can be imported as :mod:`eigen`."""

from eigen_robotics import __all__ as _ER_ALL
from eigen_robotics import *  # noqa: F403,F401 - re-export existing API

from eigen.core import *  # noqa: F403,F401 - re-export existing API
from eigen.core.tools import *  # noqa: F403,F401 - re-export existing API
import importlib
from types import ModuleType
from typing import Iterable

from eigen.core.client import *  # noqa: F403,F401 - re-export existing API
from eigen.core.config_utils import *  # noqa: F403,F401 - re-export existing

__all__ = list(_ER_ALL)
_ALLOWED_DUNDER_EXPORTS = {"__version__"}


def _reexport(module: ModuleType) -> Iterable[str]:
    exported: list[str] = []
    for name in dir(module):
        if name.startswith("_") and name not in _ALLOWED_DUNDER_EXPORTS:
            continue
        globals()[name] = getattr(module, name)
        exported.append(name)
    return exported


_MODULES_TO_EXPORT = (
    "eigen_robotics",
    "eigen.core",
    "eigen.core.tools",
    "eigen.core.client",
    "eigen.core.config_utils",
)

_exported: set[str] = set()
for _module_name in _MODULES_TO_EXPORT:
    _module = importlib.import_module(_module_name)
    _exported.update(_reexport(_module))

__all__ = sorted(_exported)