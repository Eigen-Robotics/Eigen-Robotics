"""Public alias module so the package can be imported as `eigen`."""

# from __future__ import annotation
import sys

from eigen_robotics import __all__ as _ER_ALL, get_version
from eigen_robotics import *  # noqa: F403,F401 - re-export existing API

from eigen_robotics import __version__

from eigen.core import *  # noqa: F403,F401 - re-export existing API
from eigen.core.tools import *  # noqa: F403,F401 - re-export existing API

__all__ = list(_ER_ALL) + [__version__] + ["tools", "log"]

