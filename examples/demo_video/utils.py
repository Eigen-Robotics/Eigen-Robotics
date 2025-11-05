JOINT_LIMITS = {
    "shoulder_pan":  (-2.0,  2.0),
    "shoulder_lift": ( 0.0,  3.5),
    "elbow_flex":    (-3.14158, 0.0),
    "wrist_flex":    (-2.5,  1.2),
    "wrist_roll":    (-3.14158, 3.14158),
    "gripper":       (0.0,   2.0),  # special: 0 → 100% only
}

def percentage_to_radians_list(percentages: list[float]) -> list[float]:
    """
    Convert list of percentages → list of radians.
    Assumes order:
    [shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper]
    """
    joint_names = [
        "shoulder_pan",
        "shoulder_lift",
        "elbow_flex",
        "wrist_flex",
        "wrist_roll",
        "gripper",
    ]
    return [
        percent_to_radians(joint_name, percent)
        for joint_name, percent in zip(joint_names, percentages)
    ]

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


from IPython.display import clear_output 
import matplotlib.pyplot as plt

def notebook_plot(observation):
    clear_output(wait=True)      # ← clears previous frame
    plt.imshow(observation['image'])
    plt.axis('off')
    plt.show()