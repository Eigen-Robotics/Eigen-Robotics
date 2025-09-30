"""System component definitions used by EIGEN.

This package bundles the core component abstractions that are shared
between the robotics backends.  Every component is implemented as a
node that can send and receive data through the EIGEN communication
infrastructure.
"""

from .robot import Robot
from .sensor import Sensor
