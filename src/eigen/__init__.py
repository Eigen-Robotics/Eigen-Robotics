"""Public alias module so the package can be imported as `eigen`."""

from __future__ import annotations

from eigen_robotics import __all__ as _ER_ALL, get_version
from eigen_robotics import *  # noqa: F403,F401 - re-export existing API

__all__ = list(_ER_ALL)

