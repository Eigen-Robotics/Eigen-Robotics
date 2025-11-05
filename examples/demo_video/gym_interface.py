from __future__ import annotations

from typing import Any, Dict, Literal

from eigen.gym.eigen_env import EigenEnv
from eigen.types import joint_group_command_t, rgbd_t
from eigen.types.utils import pack, unpack

from utils import percentage_to_radians_list


SimulatorName = Literal["genesis", "pybullet", "none"]


class RobotEnv(EigenEnv):
    """
    A minimal EigenEnv wrapper for SO-101 that wires up action/observation channels
    for different simulators and performs lightweight (BGR->RGB) conversion for PyBullet.

    Methods expected by EigenEnv:
      - action_packing(action) -> dict
      - observation_unpacking(observation) -> dict
      - terminated_truncated_info(state, action, next_state) -> (terminated, truncated, info)
      - reward(state, action, next_state) -> float | None
    """

    # Centralized presets to avoid duplication
    _PRESETS: Dict[str, Dict[str, str]] = {
        "genesis": {
            "action": "SO101/Genesis/joint_group_command/sim",
            "obs": "Camera/Genesis/rgbd/sim",
        },
        "pybullet": {
            "action": "SO101/Pybullet/joint_group_command/sim",
            "obs": "Camera/Pybullet/rgbd/sim",
        },
        "none": {
            "action": "SO101/joint_group_command",
            "obs": "Camera/rgbd",
        },
    }

    def __init__(self, simulator: SimulatorName, config: dict | None = None):
        """
        Args:
            simulator: One of {"genesis", "pybullet", "none"}.
            config: Optional global configuration passed to EigenEnv.
        """
        if simulator not in self._PRESETS:
            raise ValueError(
                f"Unknown simulator '{simulator}'. "
                f"Choose from {list(self._PRESETS.keys())}."
            )

        self.simulator_name: SimulatorName = simulator
        presets = self._PRESETS[simulator]

        self.action_channel_name: str = presets["action"]
        self.observation_channel_name: str = presets["obs"]

        action_space = {
            self.action_channel_name: joint_group_command_t,
        }
        observation_space = {
            self.observation_channel_name: rgbd_t,
        }

        super().__init__(
            environment_name="SO-101 Environment",
            action_channels=action_space,
            observation_channels=observation_space,
            global_config=config,
            sim=True,
        )

    # ---- EigenEnv interface ----

    def action_packing(self, action: Any) -> Dict[str, Any]:
        """Pack a joint_group_command on the configured action channel."""

        action = percentage_to_radians_list(action)
        print(f"Action: {action}")
        return {
            self.action_channel_name: pack.joint_group_command(
                name="all",
                cmd=action,
            )
        }

    def observation_unpacking(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Unpack rgbd and normalize color ordering for pybullet."""
        # `unpack.rgbd` typically returns (image, depth, ...). We take the first.
        image = unpack.rgbd(observation[self.observation_channel_name])[0]

        # PyBullet often yields BGR—convert to RGB if it looks like an image tensor.
        if self.simulator_name == "pybullet" and hasattr(image, "shape") and image.ndim == 3 and image.shape[-1] == 3:
            image = image[..., ::-1].copy()

        return {"image": image}

    def terminated_truncated_info(self, state, action, next_state):
        """Stateless env: never terminates/truncates by itself."""
        return False, False, None

    def reward(self, state, action, next_state):
        """No reward shaping by default."""
        return None

    def reset_objects(self):
        """Hook for subclasses to reset scene objects."""
        pass
