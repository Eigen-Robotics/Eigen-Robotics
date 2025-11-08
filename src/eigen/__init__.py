"""Expose the public Eigen Robotics API under the short alias ``eigen``."""
from importlib.metadata import version, PackageNotFoundError

from eigen.core import *  # noqa: F403,F401 - surface core functionality
from eigen.core.tools import *  # noqa: F403,F401 - convenience re-export
from eigen.core.client import *  # noqa: F403,F401 - client helpers
from eigen.core.config_utils import *  # noqa: F403,F401 - config helpers

from .types import *  # noqa: F403,F401 - surface all types

# GLOBAL CONSTANTS
DEFAULT_SERVICE_DECORATOR = "__DEFAULT_SERVICE"



# To expose the package version at runtime
try:
    __version__ = version("eigen-robotics")
except PackageNotFoundError:
    # When running locally without installation
    __version__ = "0.0.0-dev"