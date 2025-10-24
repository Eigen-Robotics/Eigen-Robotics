from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np
import sys
import argparse

from eigen.core.client.comm_infrastructure.base_node import main
from eigen.core.system.component.robot import Robot
from eigen.core.system.driver.robot_driver import RobotDriver
from eigen.core.tools.log import log
# from eigen.sim.pybullet.pybullet_robot_driver import BulletRobotDriver
from eigen.types import (
    joint_group_command_t,
    joint_state_t,
    pose_t,
    task_space_command_t,
)
from eigen.types.utils import pack, unpack

try:
    from so100_driver import SO100Driver
except ImportError:
    from .so100_driver import SO100Driver


class Drivers(Enum):
    PYBULLET_DRIVER = "eigen.sim.pybullet.pybullet_robot_driver:BulletRobotDriver"
    DRIVER    = "eigen.robots.so100_driver:SO100Driver"
    GENESIS_DRIVER  = "eigen.sim.genesis.genesis_robot_driver:GenesisRobotDriver"  # will only import if requested

class SO100(Robot):
    """SO100 robot component.

    Attributes:
        _runnable: Always True since this is the base robot component.
    """

    _runnable = True

    def __init__(
        self,
        name: str,
        global_config: dict[str, Any] = None,
        driver: RobotDriver = None,
    ) -> None:
        super().__init__(
            name=name,
            global_config=global_config,
            driver=driver,
        )

        #######################################
        ##     custom communication setup    ##
        #######################################
        self._joint_cmd_msg, self._cartesian_cmd_msg = None, None

        self.joint_group_command_ch = self.name + "/joint_group_command"
        self.cartesian_position_control_ch = self.name + "/cartesian_command"

        if self.sim:
            self.joint_group_command_ch = self.joint_group_command_ch + "/sim"
            self.cartesian_position_control_ch = (
                self.cartesian_position_control_ch + "/sim"
            )

        self.create_subscriber(
            self.joint_group_command_ch,
            joint_group_command_t,
            self._joint_group_command_callback,
        )

        if self.sim:
            self.joint_states_pub = self.name + "/joint_states/sim"
            self.component_channels_init(
                {
                    self.joint_states_pub: joint_state_t,
                }
            )
        else:
            self.joint_states_pub = self.name + "/joint_states"
            self.component_channels_init(
                {
                    self.joint_states_pub: joint_state_t,
                }
            )

        self.joint_group_command = None

    def control_robot(self):
        """
        will be called at the fequency dictated in the config
        handles the control of the robot and the
        """
        if self.joint_group_command:
            cmd_dict = {}
            group_name = self.joint_group_command["name"]
            
            for joint, goal in zip(
                list(
                    self.joint_groups[self.joint_group_command["name"]][
                        "actuated_joints"
                    ]
                ),
                self.joint_group_command["cmd"],
                strict=True,
            ):
                cmd_dict[joint] = goal
            self._joint_cmd_msg = None
            control_mode = self.joint_groups[group_name]["control_mode"]
            self.control_joint_group(control_mode, cmd_dict)

        self.joint_group_command = None
        self.cartesian_position_control_command = None

    def get_state(self) -> dict[str, Any]:
        """
        Returns the current state of the robot.
        This method is called by the base class to get the state of the robot.
        """
        joint_position = self.get_joint_positions()
        return {
            "joint_positions": joint_position,
        }

    def pack_data(self, state: dict[str, Any]) -> dict[str, Any]:
        joint_state = state["joint_positions"]

        joint_msg = joint_state_t()
        joint_msg.n = len(joint_state)
        joint_msg.name = list(joint_state.keys())
        joint_msg.position = list(joint_state.values())
        joint_msg.velocity = [0.0] * joint_msg.n
        joint_msg.effort = [0.0] * joint_msg.n

        return {self.joint_states_pub: joint_msg}

    ####################################################
    ##      Franka Subscriber Callbacks               ##
    ####################################################
    def _joint_group_command_callback(self, t, channel_name, msg):
        cmd, name = unpack.joint_group_command(msg)
        self.joint_group_command = {
            "cmd": cmd,
            "name": name,
        }

if __name__ == "__main__":
    # sys.argv[0] is the script name, the rest are arguments
    p = argparse.ArgumentParser()
    p.add_argument("--name", type=str, default="so100", help="Name of the robot")
    p.add_argument(
        "--config",
        type=str,
        default="so-100.yaml",
        help="Path to the robot configuration file",
    )
    args = p.parse_args()
    name = args.name
    config_path = args.config

    driver = SO100Driver(name, config_path)
    main(SO100, name, config_path, driver)


