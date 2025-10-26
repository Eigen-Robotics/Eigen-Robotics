
from eigen.framework.core.system.driver.sensor_driver import SensorDriver
from typing import Any
import numpy as np
import cv2
import eigen.core.tools.log as log

class CameraDriver(SensorDriver):
    def __init__(self, sensor_name: str, sensor_config: dict[str, Any] = None) -> None:
        super().__init__(sensor_name, sensor_config, False)
        self.cap = cv2.VideoCapture(1)  # 0 = default camera

        if not self.cap.isOpened():
            log.error("Error: Could not open camera.")
            return
        

    def get_images(self) -> Any:
        """Acquire images from the camera or its simulation."""
        # Placeholder implementation

        ret, frame = self.cap.read()
        if not ret:
            log.error("Failed to grab frame.")
            return

        # Process the frame (e.g., convert to RGB, resize, etc.)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (640, 480))

        return {"color": frame, "depth": np.zeros((480, 640), dtype=np.uint8)}

    def shutdown_driver(self) -> None:
        """Shut down the camera driver."""
        self.cap.release()