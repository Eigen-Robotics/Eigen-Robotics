from eigen.core.system.driver.sensor_driver import CameraDriver
from eigen.core.tools.log import log
import genesis as gs

from typing import Any

class GenesisCameraDriver(CameraDriver):
    def __init__(
        self,
        component_name: str,
        component_config: dict[str, Any],
        attached_body_id: int = None,
        client: Any = None,
    ) -> None:
        
        super().__init__(
            component_name, component_config, True
        )  # simulation is always True

        self.client: gs.Scene = client


        self.camera_target_position = self.config["sim_config"]["fix"][
                "camera_target_position"
            ]
        self.camera_pos = self.config["sim_config"]["fix"][
                "camera_position"
            ]
        self.fov = self.config["sim_config"].get("fov", 60)
        self.width = self.config.get("width", 640)
        self.height = self.config.get("height", 480)

        self.camera = self.client.add_camera(
            res=(self.width, self.height),
            pos=self.camera_pos,
            lookat=self.camera_target_position,
            fov=self.fov,
            GUI=False,
        )

    def get_images(self) -> dict[str, Any]:
        rgb, depth, segmentation, _ = self.camera.render(depth=True, segmentation=True, normal=True)
        return {
            "color": rgb,
            "depth": depth,
            "segmentation": segmentation,
        }
    
    def shutdown_driver(self) -> None:
        pass