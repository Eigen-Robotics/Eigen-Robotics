from eigen.core.system.driver.robot_driver import RobotDriver
from lerobot.robots.so101_follower import SO101FollowerConfig, SO101Follower

JOINT_LIMITS = {
    "shoulder_pan":  (-2.0,  2.0),
    "shoulder_lift": ( 0.0,  3.5),
    "elbow_flex":    (-3.14158, 0.0),
    "wrist_flex":    (-2.5,  1.2),
    "wrist_roll":    (-3.14158, 3.14158),
    "gripper":       (0.0,   2.0),  # special: 0 → 100% only
}

def radians_to_percent(joint_name: str, rad: float) -> float:
    """
    Convert radians → percentage.
    -100% to +100% for normal joints.
    0%  to 100% for gripper.
    """
    lower, upper = JOINT_LIMITS[joint_name]

    if joint_name == "gripper":
        # map 0 → lower, 100 → upper
        return (rad - lower) / (upper - lower) * 100.0
    else:
        # map lower → -100, upper → +100
        return (rad - lower) / (upper - lower) * 200.0 - 100.0

def percent_to_radians(joint_name: str, percent: float) -> float:
    """
    Convert percentage → radians.
    -100% to +100% for normal joints.
    0%  to 100% for gripper.
    """
    lower, upper = JOINT_LIMITS[joint_name]

    if joint_name == "gripper":
        # 0 → lower, 100 → upper
        return lower + (percent / 100.0) * (upper - lower)
    else:
        # -100 → lower, +100 → upper
        return lower + ((percent + 100.0) / 200.0) * (upper - lower)

class SO100Driver(RobotDriver):
    def __init__(self, name, config_path):
        self.name = name
        self.config_path = config_path
        super().__init__(component_name=name, component_config=config_path, sim=False)
        
        self.robot_config = SO101FollowerConfig(
            port="/dev/tty.usbmodem5A7A0576801",
            id="my_awesome_follower_arm",
        )
        self.robot = SO101Follower(self.robot_config)
        self.robot.connect()

    def check_torque_status(self) -> bool:
        raise NotImplementedError("Method check_torque_status() not implemented yet.")
    
    def pass_joint_positions(self, joints: list[str]) -> dict[str, float]:
        return {}
    
    def pass_joint_velocities(self, joints: list[str]) -> dict[str, float]:
        return {}
    
    def pass_joint_efforts(self, joints: list[str]) -> dict[str, float]:
        return {}

    def pass_joint_group_control_cmd(self, control_mode: str, cmd: dict[str, float], **kwargs) -> None:
        # iterate though all the keys and append .pos
        cmd = {key + ".pos": value for key, value in cmd.items()}
        # convert all the radian values to percentage values
        for joint in cmd:
            cmd[joint] = radians_to_percent(joint.replace(".pos", ""), cmd[joint])
            
        print(f"Sending command to robot: {cmd}")
        self.robot.send_action(cmd)

    def shutdown_driver(self) -> None:
        pass

    