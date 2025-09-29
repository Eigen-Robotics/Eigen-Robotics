import array
from typing import Any
import zlib

import cv2
import numpy as np

from ark.types.generated import (
    bullet_dynamics_t,
    comms_info_t,
    double_array_t,
    double_vector_t,
    ee_pos_t,
    flag_t,
    float_array_t,
    float_t,
    float_vector_t,
    force_t,
    grid_config_t,
    header_t,
    image_array_t,
    image_t,
    imu_t,
    int_64_t,
    joint_group_command_t,
    joint_single_command_t,
    joint_state_t,
    laser_scan_t,
    listener_info_t,
    network_info_t,
    node_info_t,
    pose_2d_t,
    pose_t,
    position_t,
    publisher_info_t,
    quaternion_t,
    rgbd_t,
    rigid_body_state_t,
    robot_init_t,
    service_info_t,
    stamp_t,
    string_t,
    subscriber_info_t,
    task_space_command_t,
    twist_t,
    velocity_2d_t,
    wheel_config_t,
    wheeled_velocity_t,
)


def bullet_dynamics(data: dict) -> bullet_dynamics_t:
    """!
    Pack a dictionary of dynamics values into a bullet_dynamics_t message.

    @param data A dictionary containing bullet dynamics values.
    @return A bullet_dynamics_t message with fields populated from the dictionary.
    """
    msg = bullet_dynamics_t()
    msg.bodyUniqueId = data["bodyUniqueId"]
    msg.linkIndex = data["linkIndex"]
    msg.mass = data["mass"]
    msg.lateralFriction = data["lateralFriction"]
    msg.spinningFriction = data["spinningFriction"]
    msg.rollingFriction = data["rollingFriction"]
    msg.restitution = data["restitution"]
    msg.linearDamping = data["linearDamping"]
    msg.angularDamping = data["angularDamping"]
    msg.contactStiffness = data["contactStiffness"]
    msg.contactDamping = data["contactDamping"]
    msg.frictionAnchor = data["frictionAnchor"]
    msg.localInertiaDiagonal = data["localInertiaDiagonal"]
    msg.ccdSweptSphereRadius = data["ccdSweptSphereRadius"]
    msg.activationState = data["activationState"]
    msg.jointDamping = data["jointDamping"]
    msg.anisotropicFriction = data["anisotropicFriction"]
    msg.maxJointVelocity = data["maxJointVelocity"]
    msg.collisionMargin = data["collisionMargin"]
    msg.jointLowerLimit = data["jointLowerLimit"]
    msg.jointUpperLimit = data["jointUpperLimit"]
    msg.jointLimitForce = data["jointLimitForce"]
    msg.physicsClientId = data["physicsClientId"]


def flag(data: int) -> flag_t:
    """!
    Pack an integer value into a flag_t message.

    @param data  The integer flag value.
    @return A flag_t message with the flag field populated.
    """
    msg = flag_t()
    msg.flag = data
    return msg


def int64(data: int) -> int_64_t:
    """!
    Pack a 64-bit integer into an int_64_t message.

    @param data  The 64-bit integer value.
    @return An int_64_t message with the data field populated.
    """
    msg = int_64_t()
    msg.data = data
    return msg


def float(data: float) -> float_t:
    """!
    Pack a single float data into a float_t message.

    @param data  A float value to be packed.
    @return A float_t message with the data field populated.
    """
    msg = float_t()
    msg.data = data
    return msg


def float_vector(data: np.ndarray) -> float_vector_t:
    """!
    Pack a list or array of float values into a float_vector_t message.

    @param data  A 1D NumPy array of float values.
    @return A float_vector_t message with populated data and size fields.
    """
    msg = float_vector_t()
    msg.n = len(data)
    msg.data = data
    return msg


def double_vector(data: np.ndarray) -> double_vector_t:
    """!
    Pack a list or array of double values into a double_vector_t message.

    @param data  A 1D NumPy array of double values.
    @return A double_vector_t message with populated data and size fields.
    """
    msg = double_vector_t()
    msg.n = len(data)
    msg.data = data
    return msg


def float_array(data: np.ndarray) -> float_vector_t:
    """!
    Pack a 2D NumPy array of float values into a float_array_t message.

    @param data  A 2D NumPy array of shape (m, n) representing float values.
    @return A float_array_t message with the `m`, `n`, and `data` fields populated accordingly.
    """
    msg = float_array_t()
    msg.m = data.shape[0]
    msg.n = data.shape[1]
    msg.data = data
    return msg


def double_array(data: np.ndarray) -> double_vector_t:
    """!
    Pack a 2D NumPy array of double values into a double_array_t message.

    @param data  A 2D NumPy array of shape (m, n) representing double values.
    @return A double_array_t message with the `m`, `n`, and `data` fields populated accordingly.
    """
    msg = double_array_t()
    msg.m = data.shape[0]
    msg.n = data.shape[1]
    msg.data = data
    return msg


def string(data: str) -> string_t:
    """!
    Pack a Python string into a string_t message.

    @param data  The string to pack.
    @return A string_t message with the data field populated.
    """
    msg = string_t()
    msg.data = data
    return msg


def position(x: float, y: float, z: float) -> position_t:
    """!
    Pack x, y, z float values into a position_t message.

    @param x  The x-coordinate.
    @param y  The y-coordinate.
    @param z  The z-coordinate.
    @return A position_t message with x, y, and z populated.
    """
    msg = position_t()
    msg.x = x
    msg.y = y
    msg.z = z
    return msg


def quaternion(x: float, y: float, z: float, w: float) -> quaternion_t:
    """!
    Pack x, y, z, w float values into a quaternion_t message.

    @param x  The x component.
    @param y  The y component.
    @param z  The z component.
    @param w  The w component.
    @return A quaternion_t message with the fields populated.
    """
    msg = quaternion_t()
    msg.x = x
    msg.y = y
    msg.z = z
    msg.w = w
    return msg


def twist(linear_velocity: np.ndarray, angular_velocity: np.ndarray) -> twist_t:
    """!
    Pack linear and angular velocity numpy arrays into a twist_t message.

    @param linear_velocity   numpy array of shape (3,) for linear velocity [v_x, v_y, v_z].
    @param angular_velocity  numpy array of shape (3,) for angular velocity [omega_x, omega_y, omega_z].
    @return A twist_t message with fields populated.
    """
    if linear_velocity.shape != (3,):
        raise ValueError(
            f"linear_velocity must be numpy array of shape (3,), got {linear_velocity.shape}"
        )
    if angular_velocity.shape != (3,):
        raise ValueError(
            f"angular_velocity must be numpy array of shape (3,), got {angular_velocity.shape}"
        )

    msg = twist_t()
    msg.linear_velocity = linear_velocity
    msg.angular_velocity = angular_velocity
    return msg


def robot_init(
    name: str, position: np.ndarray, orientation: np.ndarray, q_init: np.ndarray
) -> robot_init_t:
    """!
    Pack the robot_init_t message from provided fields.

    @param name         Robot name as string.
    @param position     numpy array of shape (3,) for position.
    @param orientation  numpy array of shape (4,) for quaternion orientation.
    @param q_init       numpy array of shape (n,) with joint initial positions.
    @return             robot_init_t message.
    """
    if position.shape != (3,):
        raise ValueError(f"position must have shape (3,), got {position.shape}")
    if orientation.shape != (4,):
        raise ValueError(
            f"orientation must have shape (4,), got {orientation.shape}"
        )
    if q_init.ndim != 1:
        raise ValueError(
            f"q_init must be a 1D numpy array, got shape {q_init.shape}"
        )

    msg = robot_init_t()
    msg.name = name
    msg.position = position
    msg.orientation = orientation
    msg.n = int(q_init.shape[0])
    msg.q_init = q_init
    return msg


def rigid_body_state(
    name: str,
    position: np.ndarray,
    orientation: np.ndarray,
    lin_velocity: np.ndarray,
    ang_velocity: np.ndarray,
) -> rigid_body_state_t:
    """!
    Pack a rigid_body_state_t message from its components.

    @param name          Name of the rigid body.
    @param position      Position as a numpy array of shape (3,).
    @param orientation   Orientation quaternion as a numpy array of shape (4,).
    @param lin_velocity  Linear velocity as a numpy array of shape (3,).
    @param ang_velocity  Angular velocity as a numpy array of shape (3,).
    @return              Packed rigid_body_state_t message.
    """
    if position.shape != (3,):
        raise ValueError(f"position must have shape (3,), got {position.shape}")
    if orientation.shape != (4,):
        raise ValueError(
            f"orientation must have shape (4,), got {orientation.shape}"
        )
    if lin_velocity.shape != (3,):
        raise ValueError(
            f"lin_velocity must have shape (3,), got {lin_velocity.shape}"
        )
    if ang_velocity.shape != (3,):
        raise ValueError(
            f"ang_velocity must have shape (3,), got {ang_velocity.shape}"
        )

    msg = rigid_body_state_t()
    msg.name = name
    msg.position = position
    msg.orientation = orientation
    msg.lin_velocity = lin_velocity
    msg.ang_velocity = ang_velocity
    return msg


def service_info(data: dict[str, Any]) -> service_info_t:
    """!
    Pack a service_info_t message from a dictionary.

    @param data  Dictionary with keys:
                 'comms_type', 'service_name', 'service_host', 'service_port',
                 'registry_host', 'registry_port', 'request_type', 'response_type'.
    @return      Packed service_info_t message.
    """
    msg = service_info_t()
    msg.comms_type = data["comms_type"]
    msg.service_name = data["service_name"]
    msg.service_host = data["service_host"]
    msg.service_port = data["service_port"]
    msg.registry_host = data["registry_host"]
    msg.registry_port = data["registry_port"]
    msg.request_type = data["request_type"]
    msg.response_type = data["response_type"]
    return msg


def listener_info(data: dict[str, Any]) -> listener_info_t:
    """!
    Pack a listener_info_t message from a dictionary.

    @param data  Dictionary with keys: 'comms_type', 'channel_name', 'channel_type', 'channel_status'.
    @return      Packed listener_info_t message.
    """
    msg = listener_info_t()
    msg.comms_type = data["comms_type"]
    msg.channel_name = data["channel_name"]
    msg.channel_type = data["channel_type"]
    msg.channel_status = data["channel_status"]
    return msg


def subscriber_info(data: dict[str, Any]) -> subscriber_info_t:
    """!
    Pack a subscriber_info_t message from a dictionary.

    @param data  Dictionary with keys: 'comms_type', 'channel_name', 'channel_type', 'channel_status'.
    @return      Packed subscriber_info_t message.
    """
    msg = subscriber_info_t()
    msg.comms_type = data["comms_type"]
    msg.channel_name = data["channel_name"]
    msg.channel_type = data["channel_type"]
    msg.channel_status = data["channel_status"]
    return msg


def publisher_info(data: dict[str, Any]) -> publisher_info_t:
    """!
    Pack a publisher_info_t message from a dictionary.

    @param data  Dictionary with keys: 'comms_type', 'channel_name', 'channel_type', 'channel_status'.
    @return      Packed publisher_info_t message.
    """
    msg = publisher_info_t()
    msg.comms_type = data["comms_type"]
    msg.channel_name = data["channel_name"]
    msg.channel_type = data["channel_type"]
    msg.channel_status = data["channel_status"]
    return msg


def comms_info(
    listeners: list[dict[str, Any]],
    subscribers: list[dict[str, Any]],
    publishers: list[dict[str, Any]],
    services: list[dict[str, Any]],
) -> comms_info_t:
    """!
    Pack a comms_info_t message from separate lists of dictionaries.

    @param listeners     List of listener_info_t dictionaries.
    @param subscribers   List of subscriber_info_t dictionaries.
    @param publishers    List of publisher_info_t dictionaries.
    @param services      List of service_info_t dictionaries.
    @return             Packed comms_info_t message.
    """
    msg = comms_info_t()

    msg.n_listeners = len(listeners)
    msg.listeners = [listener_info(ld) for ld in listeners]

    msg.n_subscribers = len(subscribers)
    msg.subscribers = [subscriber_info(sd) for sd in subscribers]

    msg.n_publishers = len(publishers)
    msg.publishers = [publisher_info(pd) for pd in publishers]

    msg.n_services = len(services)
    msg.services = [service_info(sd) for sd in services]

    return msg


def node_info(
    node_name: str, node_id: str, node_infos: dict[str, Any]
) -> node_info_t:
    """!
    Pack a node_info_t message with node_name, node_id, and node_infos dictionary containing listeners, subscribers, publishers, and services.

    @param node_name    Name of the node.
    @param node_id      ID of the node.
    @param node_infos   Dictionary with keys: 'listeners', 'subscribers', 'publishers', 'services'.
    @return             Packed node_info_t message.
    """
    msg = node_info_t()
    msg.node_name = node_name
    msg.node_id = node_id
    msg.comms = comms_info(**node_infos)
    return msg


def network_info(nodes: list[dict[str, Any]]) -> network_info_t:
    """!
    Pack a network_info_t message from a list of node dictionaries.

    Each node dict should have:
      - 'node_name' (str)
      - 'node_id' (str)
      - 'node_infos' (dict with keys: listeners, subscribers, publishers, services)

    @param nodes List of node dictionaries.
    @return      Packed network_info_t message.
    """
    msg = network_info_t()
    msg.n_nodes = len(nodes)
    msg.nodes = [node_info(**node) for node in nodes]
    return msg


def stamp(sec: int, nsec: int) -> stamp_t:
    """!
    Pack stamp_t from seconds and nanoseconds.

    @param sec  Seconds part of the timestamp.
    @param nsec Nanoseconds part of the timestamp.
    @return     stamp_t message.
    """
    msg = stamp_t()
    msg.sec = sec
    msg.nsec = nsec
    return msg


def header(seq: int, stamp_dict: dict[str, int], frame_id: str) -> header_t:
    """!
    Pack a header_t message from individual fields.

    @param seq      Sequence number.
    @param stamp_dict Dict with keys 'sec' and 'nsec'.
    @param frame_id Frame identifier string.
    @return         Packed header_t message.
    """
    msg = header_t()
    msg.seq = seq
    msg.stamp = stamp(**stamp_dict)  # Use stamp to convert dict to stamp_t
    msg.frame_id = frame_id
    return msg


def joint_state(
    header_dict: dict[str, Any],
    name: list[str],
    position: np.ndarray,
    velocity: np.ndarray,
    effort: np.ndarray,
) -> joint_state_t:
    """!
    Pack a joint_state_t message.

    @param header_dict Dictionary with keys 'seq', 'stamp' (with 'sec' and 'nsec'), and 'frame_id'.
    @param name       List of joint names.
    @param position   Numpy array of joint positions.
    @param velocity   Numpy array of joint velocities.
    @param effort     Numpy array of joint efforts.
    @return           Packed joint_state_t message.
    """
    assert len(name) == len(position) == len(velocity) == len(effort), (
        "All joint arrays must be of the same length"
    )
    msg = joint_state_t()
    msg.header = header(**header_dict)
    msg.n = len(name)
    msg.name = name
    msg.position = position
    msg.velocity = velocity
    msg.effort = effort
    return msg


def force(name: list[str], force: np.ndarray) -> force_t:
    """
    @brief Packs force data into a force_t message.

    @param name A list of names (e.g., joint names or link identifiers).
    @param force A NumPy array containing force values corresponding to each name.
    @return A populated force_t message containing the name and force fields.
    """
    assert len(name) == len(force), (
        "Force arrays must match the same of the names"
    )
    msg = force_t()
    msg.n = len(name)
    msg.name = name
    msg.force = force
    return msg


def ee_pos(pos: np.ndarray, quat: np.ndarray) -> ee_pos_t:
    """!
    Pack an ee_pos_t message.

    @param pos          A numpy array of shape (3,) representing [x, y, z].
    @param quat         A numpy array of shape (4,) representing [x, y, z, w].
    @return             Packed ee_pos_t message.
    """
    msg = ee_pos_t()
    msg.position = position(pos)
    msg.quaternion = quaternion(quat)
    return msg


def image(img: np.ndarray, name: str = "") -> image_t:
    """!
    Converts an BGR image (as a NumPy array) into a serialized image_t message with compression.

    @param img   The BGR image (NumPy array) to pack.
    @param name An optional name used to generate the frame name.
    @return An image_t message containing the encoded image and metadata, or None if encoding fails.
    """
    msg = image_t()

    # Fill in timestamp and frame_name
    msg.frame_name = f"{name}_frame"

    # Get image dimensions
    height, width, _ = img.shape
    msg.height = height
    msg.width = width

    # Set pixel format and channel type
    msg.pixel_format = image_t.PIXEL_FORMAT_BGR  # OpenCV uses BGR format
    msg.channel_type = image_t.CHANNEL_TYPE_UINT8  # OpenCV images are uint8

    # Set bigendian
    msg.bigendian = False

    # Set row_stride
    msg.row_stride = img.strides[0]  # Number of bytes per row

    # Compress the image using the selected method
    success, encoded_image = cv2.imencode(".png", img)
    if success:
        data = array.array("B", encoded_image.tobytes())
        msg.data = data
        # Set size of data
        msg.size = len(msg.data)
        # Set compression method
        msg.compression_method = image_t.COMPRESSION_METHOD_PNG
    else:
        # TODO(FV): FIX
        log.warn("Failed to compress image")  # noqa: F821
        return None

    return msg


def depth(depth_map: np.ndarray, name: str = "") -> image_t:
    """!
    Converts a depth image (as a NumPy array) into a compressed image_t message using zlib compression.

    @param depth_map A 2D NumPy array containing depth values in meters.
    @param name An optional name used to generate the frame name.
    @return An image_t message containing the compressed depth image and metadata.
    """
    msg = image_t()

    # Fill in timestamp and frame_name
    msg.frame_name = f"{name}_frame"

    # Get image dimensions
    height, width = depth_map.shape
    msg.height = height
    msg.width = width

    # Set pixel format and channel type
    msg.pixel_format = image_t.PIXEL_FORMAT_DEPTH  # OpenCV uses BGR format
    msg.channel_type = image_t.CHANNEL_TYPE_UINT16  # OpenCV images are uint8

    # Set bigendian
    msg.bigendian = False

    # Set row_stride
    msg.row_stride = depth_map.strides[0]  # Number of bytes per row

    # Compress the depth using zlib
    depth_map = (depth_map * 1000).astype(np.uint16)  # Convert to mm
    depth_bytes = depth_map.tobytes()  # Convert depth map to raw bytes
    compressed_depth = zlib.compress(depth_bytes)

    # Add to message
    msg.data = compressed_depth
    # Set size of data
    msg.size = len(msg.data)
    # Set compression method
    msg.compression_method = image_t.COMPRESSION_METHOD_ZLIB
    return msg


def rgbd(
    rgb_image: np.ndarray, depth_map: np.ndarray, name: str = ""
) -> rgbd_t:
    """!
    Packs an RGB image and a depth map into a single rgbd_t message.

    This function uses `image` to encode the RGB image and `depth` to encode the depth image,
    combining them into a single RGB-D message structure.

    @param rgb_image The RGB image (typically a NumPy array) to be packed.
    @param depth_map The depth image (typically a NumPy array) to be packed.
    @param name An optional name used to generate frame names for both components.
    @return An rgbd_t message containing the packed RGB and depth data.
    """
    image_msg = image(rgb_image, name=name)
    depth_msg = depth(depth_map, name=name)

    msg = rgbd_t()
    msg.image = image_msg
    msg.depth = depth_msg
    return msg


def image_array(
    timestamp_ns: int, images: list[np.ndarray] | np.ndarray
) -> image_array_t:
    """!
    Pack an image_array_t message.

    @param timestamp_ns   Timestamp in nanoseconds.
    @param images         Either a list of numpy arrays or a single stacked numpy array (N, H, W[, C]).
    @return               Packed image_array_t message.
    """
    if isinstance(images, np.ndarray):
        # If it's a stacked array, split along axis 0
        images = list(images)

    packed_images = [image(img) for img in images]

    msg = image_array_t()
    msg.timestamp_ns = timestamp_ns
    msg.num_images = len(packed_images)
    msg.images = packed_images
    return msg


def laser_scan(angles: np.ndarray, ranges: np.ndarray) -> laser_scan_t:
    """!
    Pack angle and range data into a laser_scan_t message.

    This function uses float_vector to wrap both arrays into the appropriate message format.

    @param angles  A 1D NumPy array of LiDAR angles.
    @param ranges  A 1D NumPy array of LiDAR ranges corresponding to the angles.
    @return A laser_scan_t message containing the packed angle and range data.
    """
    angles_msg = float_vector(angles)
    ranges_msg = float_vector(ranges)

    msg = laser_scan_t()
    msg.angles = angles_msg
    msg.ranges = ranges_msg
    return msg


def pose(position: np.ndarray, orientation: np.ndarray) -> pose_t:
    """!
    Pack position and orientation numpy arrays into a pose_t message.

    @param position     numpy array of shape (3,) for (x, y, z).
    @param orientation  numpy array of shape (4,) for quaternion (x, y, z, w).
    @return A pose_t message with fields populated.
    """
    if position.shape != (3,):
        raise ValueError(
            f"Position must be a numpy array with shape (3,), got {position.shape}"
        )
    if orientation.shape != (4,):
        raise ValueError(
            f"Orientation must be a numpy array with shape (4,), got {orientation.shape}"
        )

    msg = pose_t()
    msg.position = position
    msg.orientation = orientation
    return msg


def pose_2d(x: float, y: float, theta: float) -> pose_2d_t:
    """!
    Pack 2D pose information into a pose_2d_t message.

    @param x       The x-coordinate of the pose.
    @param y       The y-coordinate of the pose.
    @param theta   The orientation angle (in radians) of the pose.
    @return A pose_2d_t message with the x, y, and theta fields populated.
    """
    msg = pose_2d_t()
    msg.x = x
    msg.y = y
    msg.theta = theta
    return msg


def velocity_2d(v_x: float, v_y: float, w: float) -> velocity_2d_t:
    """!
    Pack 2D velocity information into a velocity_2d_t message.

    @param v_x   The x-component of the linear velocity.
    @param v_y   The y-component of the linear velocity.
    @param w     The angular velocity
    @return A velocity_2d_t message
    """
    msg = velocity_2d_t()
    msg.v_x = v_x
    msg.v_y = v_y
    msg.w = w
    return msg


def wheeled_velocity(
    linear_velocity: float, angular_velocity: float
) -> wheeled_velocity_t:
    """!
    Pack 2D velocity information into a velocity_t message.

    @param linear_velocity: The linear velocity component.
    @param angular_velocity: The angular velocity component.
    @return A velocity_t message with linear and angular velocity fields populated.
    """
    msg = wheeled_velocity_t()
    msg.linear = linear_velocity
    msg.angular = angular_velocity
    return msg


def joint_group_command(cmd: list, name: str) -> joint_group_command_t:
    """!
    Pack joint group command into a joint_ground_command_t message.

    @param cmd     A list of the joint commands
    @param name    Name of the joint group.
    @return A joint_ground_command_t message
    """
    msg = joint_group_command_t()
    msg.name = name
    msg.n = len(cmd)
    msg.cmd = cmd
    return msg


def joint_single_command(name: str, cmd: float) -> joint_single_command_t:
    """!
    Pack a joint_single_command_t message from name and command value.

    @param name Joint name.
    @param cmd  Command value (e.g., position, velocity).
    @return     Packed joint_single_command_t message.
    """
    msg = joint_single_command_t()
    msg.name = name
    msg.cmd = cmd
    return msg


def grid_config(
    scene_bounds: dict[str, list[float]], grid_size: float
) -> grid_config_t:
    """!
    Pack grid_config into a grid_config_t message.

    @param scene_bounds A dictionary with 'x' and 'y' keys containing the min, max bounds for the scene.
    @param grid_size    The size of each grid cell.
    @return A grid_config_t message populated with the given bounds and grid size.
    """
    msg = grid_config_t()
    msg.x_bounds = scene_bounds["x"]
    msg.y_bounds = scene_bounds["y"]
    msg.grid_size = grid_size
    return msg


def wheel_config(radius: float, thread: float) -> wheel_config_t:
    """!
    Packs wheel configuration data into a wheel_config_t message.

    Constructs a wheel_config_t message using provided wheel metadata:
    @param radius      Radius of the wheels.
    @param thread      Distance between the wheels
    @return A wheel_config_t message containing the packed configuration data.
    """
    msg = wheel_config_t()
    msg.radius = radius
    msg.thread = thread
    return msg


def imu(orientation: np.ndarray, gyro: np.ndarray, accel: np.ndarray) -> imu_t:
    """!
    Packs IMU data into an imu_t message.

    Constructs an imu_t message using provided IMU data:
    @param orientation  A numpy array of shape (4,) representing the quaternion orientation.
    @param gyro         A numpy array of shape (3,) representing the gyroscope data.
    @param accel        A numpy array of shape (3,) representing the accelerometer data.
    @return A imu_t message containing the packed IMU data.
    """
    msg = imu_t()
    if orientation.shape != (4,):
        raise ValueError(
            f"orientation must be a numpy array with shape (4,), got {orientation.shape}"
        )
    if gyro.shape != (3,):
        raise ValueError(
            f"gyro must be a numpy array with shape (3,), got {gyro.shape}"
        )
    if accel.shape != (3,):
        raise ValueError(
            f"accel must be a numpy array with shape (3,), got {accel.shape}"
        )

    msg.orientation = orientation
    msg.gyro = gyro
    msg.accel = accel
    return msg


def task_space_command(
    name: str,
    position_values: np.ndarray,
    quaternion_values: np.ndarray,
    gripper_values: float,
) -> task_space_command_t:
    """!
    Packs task space command data into a task_space_command_t message.

    Constructs a task_space_command_t message using provided task space command data:
    @param position     A numpy array of shape (3,) representing the desired position.
    @param orientation  A numpy array of shape (4,) representing the desired orientation as a quaternion.
    @return A task_space_command_t message containing the packed task space command data.
    """
    msg = task_space_command_t()
    if position_values.shape != (3,):
        raise ValueError(
            f"position must be a numpy array with shape (3,), got {position_values.shape}"
        )
    if quaternion_values.shape != (4,):
        raise ValueError(
            f"orientation must be a numpy array with shape (4,), got {quaternion_values.shape}"
        )

    # convert to lists
    position_list = position_values.tolist()
    quaternion_list = quaternion_values.tolist()

    msg.name = name
    msg.position = position(
        x=position_list[0], y=position_list[1], z=position_list[2]
    )
    msg.quaternion = quaternion(
        x=quaternion_list[0],
        y=quaternion_list[1],
        z=quaternion_list[2],
        w=quaternion_list[3],
    )
    msg.gripper = gripper_values  # Assuming gripper is a float value
    return msg
