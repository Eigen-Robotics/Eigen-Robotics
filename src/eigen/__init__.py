"""Public alias module so the package can be imported as `eigen`."""

from eigen_robotics import __all__ as _ER_ALL
from eigen_robotics import *  # noqa: F403,F401 - re-export existing API

from eigen.core import *  # noqa: F403,F401 - re-export existing API
from eigen.core.tools import *  # noqa: F403,F401 - re-export existing API

from eigen.core.client import *  # noqa: F403,F401 - re-export existing API
from eigen.core.config_utils import *  # noqa: F403,F401 - re-export existing

__all__ = list(_ER_ALL)
