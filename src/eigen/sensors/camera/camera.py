from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np
import sys
import argparse

from eigen.core.client.comm_infrastructure.base_node import main
from eigen.core.system.component.sensor import Sensor
from eigen.core.system.driver.sensor_driver import SensorDriver
from eigen.core.tools.log import log
from eigen.types import (
    rgbd_t,
)
from eigen.types.utils import pack, unpack

try:
    from .camera_driver import CameraDriver
except ImportError as e:
    from camera_driver import CameraDriver

class Drivers(Enum):
    PYBULLET_DRIVER = "eigen.sim.pybullet.pybullet_camera_driver:BulletCameraDriver"
    DRIVER    = "eigen.robots.camera_driver.camera_driver"
    GENESIS_DRIVER  = "eigen.sim.genesis.genesis_camera_driver:GenesisCameraDriver"  # will only import if requested

class BasicCamera(Sensor):
    """Basic camera sensor component.

    Attributes:
        _runnable: Always True since this is the base sensor component.
    """

    _runnable = True

    def __init__(
        self,
        name: str,
        global_config: dict[str, Any] = None,
        driver: SensorDriver = None,
    ) -> None:
        super().__init__(
            name=name,
            global_config=global_config,
            driver=driver,
        )

        self.rgbd_channel = self.name + "/rgbd"
        if self.sim == True:
            self.rgbd_channel = self.rgbd_channel + "/sim"

        self.component_channels_init(
            {
                self.rgbd_channel: rgbd_t,
            }
        )


    
    def get_sensor_data(self) -> Any:
        """Simulate the sensor's behavior."""
        images = self._driver.get_images()
        return images
    
    def pack_data(self, images: Any) -> dict[str, Any]:
        color_image = images["color"]
        depth_image = images["depth"]

        msg = pack.rgbd(rgb_image=color_image, depth_map=depth_image, name=self.name)
        return {self.rgbd_channel: msg}

    
if __name__ == "__main__":
    # sys.argv[0] is the script name, the rest are arguments
    p = argparse.ArgumentParser()
    p.add_argument("--name", type=str, default="Camera", help="Name of the robot")
    p.add_argument(
        "--config",
        type=str,
        default="camera.yaml",
        help="Path to the robot configuration file",
    )
    args = p.parse_args()
    name = args.name
    config_path = args.config

    driver = CameraDriver(name, config_path)
    main(BasicCamera, name, config_path, driver)
