import time
from typing import Any

from ark.core.system.component_registry import (
    ComponentSpec,
    ComponentType,
    _register_default_component,
)
from ark.core.system.driver.robot_driver import RobotDriver
from ark.core.tools.log import log

# Optional import for franky - only register component if dependencies are available
try:
    from franky import (
        Affine,
        CartesianMotion,
        CartesianVelocityMotion,
        Duration,
        Gripper,
        JointMotion,
        JointVelocityMotion,
        Robot,
        Twist,
    )

    _FRANKY_AVAILABLE = True
except ImportError:
    _FRANKY_AVAILABLE = False
    log.warn(
        "FrankaResearch3Driver dependencies not available. "
        "Component registered but not runnable. Install 'franky' to enable."
    )


@_register_default_component(
    ComponentSpec(
        component_type=ComponentType.ROBOT,
        id="franka-research3d-base",
        is_driver=True,
    )
)
class FrankaResearch3Driver(RobotDriver):
    """Franka Research 3 driver using franky library.

    Attributes:
        _runnable: Whether this driver can actually be used (dependencies available).
    """

    _runnable = _FRANKY_AVAILABLE

    def __init__(
        self,
        component_name: str,
        component_config: dict[str, Any] = None,
        sim: bool = False,
    ) -> None:
        super().__init__(component_name, component_config, sim)

        if not _FRANKY_AVAILABLE:
            raise ImportError(
                "FrankaResearch3Driver requires 'franky' library. "
                "Install it with: pip install franky"
            )

        self.robot = Robot(self.config["real_config"]["robot_ip"])
        self.gripper = Gripper(self.config["real_config"]["gripper_ip"])
        self.robot.relative_dynamics_factor = self.config["real_config"][
            "relative_dynamics_factor"
        ]
        self.gripper_speed = self.config["real_config"]["gripper_speed"]

    # ======================
    # Driver Functions
    # ======================
    def check_torque_status(self) -> bool:
        log.info("Torque status check not implemented in Franka driver.")
        pass

    def pass_joint_positions(self, joints: list[str]) -> dict[str, float]:
        joint_state = self.robot.current_joint_state.position
        width = self.gripper.width
        joint_state = joint_state.tolist()
        joint_state.append(width)
        joint_state.append(width)

        joints_state_dict = {}
        for i, joint_name in enumerate(joints):
            joints_state_dict[joint_name] = joint_state[i]

        # print(joints_state_dict)
        return joints_state_dict

    def pass_joint_velocities(self, joints: list[str]) -> dict[str, float]:
        raise NotImplementedError

    def pass_joint_efforts(self, joints: list[str]) -> dict[str, float]:
        raise NotImplementedError

    # ======================
    # Control Functions
    # ======================

    def pass_joint_group_control_cmd(
        self,
        control_mode: str,
        joints: list[str],
        cmd: dict[str, float],
        **kwargs,
    ) -> None:
        values = list(cmd.values())
        group = kwargs["group_name"]

        if group == "all":
            if control_mode == "position":
                motion = JointMotion(values[:7])
                self.robot.move(motion, asynchronous=True)
                # success_future
                _ = self.gripper.move_async(values[7], self.gripper_speed)
                time.sleep(0.01)
        elif group == "arm":
            if control_mode == "position":
                motion = JointMotion(values)
            elif control_mode == "velocity":
                # Accelerate to the given joint velocity and hold it. After 500ms stop the robot again.
                motion = JointVelocityMotion(values[:7], duration=Duration(500))
            else:
                log.error(
                    "Invalid Control Mode: recived " + str(control_mode) + ""
                )
            self.robot.move(motion, asynchronous=True)
            time.sleep(0.01)
        elif group == "gripper":
            # success_future
            _ = self.gripper.move_async(values[0], self.gripper_speed)
            time.sleep(0.01)
            log.error("gripper not implimented yet")
        else:
            log.error("Invalid Group: recived " + str(group) + "")

    def pass_cartesian_control_cmd(
        self, control_mode, position, quaternion
    ) -> None:
        if control_mode == "position":
            motion = CartesianMotion(Affine(position, quaternion))
        elif control_mode == "velocity":
            # A cartesian velocity motion with linear (first argument) and angular (second argument) components
            log.error(
                "Cartesian Velocity Control is not tested in Franka Driver yet"
            )
            motion = CartesianVelocityMotion(
                Twist(position, quaternion), duration=Duration(500)
            )
        else:
            log.error("Invalid Control Mode: recived " + str(control_mode) + "")

        self.robot.move(motion, asynchronous=True)
        time.sleep(0.01)

    # ======================
    # Core Functions
    # ======================

    def shutdown_driver(self):
        pass
