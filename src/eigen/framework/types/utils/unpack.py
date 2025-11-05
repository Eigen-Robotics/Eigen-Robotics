from typing import Any
import zlib

import cv2
import numpy as np

from eigen.types.generated import (
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
    int64_vector_t,
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


def bullet_dynamics(msg: bullet_dynamics_t) -> dict:
    """!
    Unpack a bullet_dynamics_t message into a dictionary of values.
    """
    dynamics = {
        "bodyUniqueId": msg.bodyUniqueId,
        "linkIndex": msg.linkIndex,
        "mass": msg.mass,
        "lateralFriction": msg.lateralFriction,
        "spinningFriction": msg.spinningFriction,
        "rollingFriction": msg.rollingFriction,
        "restitution": msg.restitution,
        "linearDamping": msg.linearDamping,
        "angularDamping": msg.angularDamping,
        "contactStiffness": msg.contactStiffness,
        "contactDamping": msg.contactDamping,
        "frictionAnchor": msg.frictionAnchor,
        "localInertiaDiagonal": msg.localInertiaDiagonal,
        "ccdSweptSphereRadius": msg.ccdSweptSphereRadius,
        "activationState": msg.activationState,
        "jointDamping": msg.jointDamping,
        "anisotropicFriction": msg.anisotropicFriction,
        "maxJointVelocity": msg.maxJointVelocity,
        "collisionMargin": msg.collisionMargin,
        "jointLowerLimit": msg.jointLowerLimit,
        "jointUpperLimit": msg.jointUpperLimit,
        "jointLimitForce": msg.jointLimitForce,
        "physicsClientId": msg.physicsClientId,
    }
    return dynamics


def flag(msg: flag_t) -> int:
    """!
    Unpack a flag_t message to extract the flag value.

    @param msg  A flag_t message.
    @return The unpacked integer flag value.
    """
    return msg.flag


def int64(msg: int_64_t) -> int:
    """!
    Unpack an int_64_t message to extract the integer value.

    @param msg  An int_64_t message.
    @return The unpacked 64-bit integer value.
    """
    return msg.data


def float(msg: float_t) -> float:
    """!
    Unpack a float_t message into a float value.

    @param msg  A float_t message containing a single float value.
    @return The unpacked float value.
    """
    return msg.data


def float_vector(msg: float_vector_t) -> np.ndarray:
    """!
    Unpack a float_vector_t message into a NumPy array.

    @param msg  A float_vector_t message containing float data.
    @return A NumPy array containing the unpacked float values.
    """
    data = msg.data
    data = np.array(data)
    return data


def double_vector(msg: double_vector_t) -> np.ndarray:
    """!
    Unpack a double_vector_t message into a NumPy array.

    @param msg  A double_vector_t message containing double data.
    @return A NumPy array containing the unpacked double values.
    """
    data = msg.data
    data = np.array(data)
    return data


def int64_vector(msg: int64_vector_t) -> np.ndarray:
    """!
    Unpack a int64_vector_t message into a NumPy array.

    @param msg  A int64_vector_t message containing int64 data.
    @return A NumPy array containing the unpacked int64 values.
    """
    data = msg.data
    data = np.array(data)
    return data


def float_array(msg: float_array_t) -> np.ndarray:
    """!
    Unpack a float_array_t message into a 2D NumPy array.

    @param msg  A float_array_t message containing float data.
    @return A NumPy array containing the unpacked float values.
    """
    data = msg.data
    data = np.array(data)
    return data


def float_array(msg: float_array_t) -> np.ndarray:  # noqa: F811
    """!
    Unpack a float_array_t message into a 2D NumPy array.

    @param msg  A float_array_t message containing float data.
    @return A NumPy array containing the unpacked float values.
    """
    data = msg.data
    data = np.array(data)
    return data


def double_array(msg: double_array_t) -> np.ndarray:
    """!
    Unpack a double_array_t message into a 2D NumPy array.

    @param msg  A double_array_t message containing double data.
    @return A NumPy array containing the unpacked double values.
    """
    data = msg.data
    data = np.array(data)
    return data


def string(msg: string_t) -> str:
    """!
    Unpack a string_t message into a Python string.

    @param msg  A string_t message.
    @return The unpacked string.
    """
    return msg.data


def position(msg: position_t) -> tuple[float, float, float]:
    """!
    Unpack a position_t message into a tuple of (x, y, z).

    @param msg  A position_t message.
    @return A tuple containing x, y, z.
    """
    return msg.x, msg.y, msg.z


def quaternion(msg: quaternion_t) -> tuple[float, float, float, float]:
    """!
    Unpack a quaternion_t message into a tuple (x, y, z, w).

    @param msg  A quaternion_t message.
    @return A tuple containing x, y, z, w.
    """
    return msg.x, msg.y, msg.z, msg.w


def twist(msg: twist_t) -> tuple[np.ndarray, np.ndarray]:
    """!
    Unpack a twist_t message into linear and angular velocity numpy arrays.

    @param msg  A twist_t message.
    @return A tuple (linear_velocity, angular_velocity) as numpy arrays.
    """
    linear_velocity = np.array(msg.linear_velocity)
    angular_velocity = np.array(msg.angular_velocity)
    return linear_velocity, angular_velocity


def robot_init(
    msg: robot_init_t,
) -> tuple[str, np.ndarray, np.ndarray, np.ndarray]:
    """!
    Unpack a robot_init_t message into its components.

    @param msg  robot_init_t message.
    @return Tuple of (name, position, orientation, q_init)
        - name: string
        - position: numpy array shape (3,)
        - orientation: numpy array shape (4,)
        - q_init: numpy array shape (n,)
    """
    name = msg.name
    position = np.array(msg.position)
    orientation = np.array(msg.orientation)
    q_init = np.array(msg.q_init)

    if len(q_init) != msg.n:
        raise ValueError(
            f"q_init length {len(q_init)} does not match n {msg.n}"
        )

    return name, position, orientation, q_init


def rigid_body_state(
    msg: rigid_body_state_t,
) -> tuple[str, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """!
    Unpack a rigid_body_state_t message into its components.

    @param msg  The rigid_body_state_t message to unpack.
    @return     Tuple of (name, position, orientation, lin_velocity, ang_velocity)
    """
    name = msg.name
    position = msg.position
    orientation = msg.orientation
    lin_velocity = msg.lin_velocity
    ang_velocity = msg.ang_velocity

    return name, position, orientation, lin_velocity, ang_velocity


def service_info(msg: service_info_t) -> dict[str, Any]:
    """!
    Unpack a service_info_t message into a dictionary.

    @param msg  The service_info_t message to unpack.
    @return     Dictionary with keys:
                'comms_type', 'service_name', 'service_host', 'service_port',
                'registry_host', 'registry_port', 'request_type', 'response_type'.
    """
    return {
        "comms_type": msg.comms_type,
        "service_name": msg.service_name,
        "service_host": msg.service_host,
        "service_port": msg.service_port,
        "registry_host": msg.registry_host,
        "registry_port": msg.registry_port,
        "request_type": msg.request_type,
        "response_type": msg.response_type,
    }


def listener_info(msg: listener_info_t) -> dict[str, Any]:
    """!
    Unpack a listener_info_t message into a dictionary.

    @param msg  The listener_info_t message to unpack.
    @return     Dictionary with keys: 'comms_type', 'channel_name', 'channel_type', 'channel_status'.
    """
    return {
        "comms_type": msg.comms_type,
        "channel_name": msg.channel_name,
        "channel_type": msg.channel_type,
        "channel_status": msg.channel_status,
    }


def subscriber_info(msg: subscriber_info_t) -> dict[str, Any]:
    """!
    Unpack a subscriber_info_t message into a dictionary.

    @param msg  The subscriber_info_t message to unpack.
    @return     Dictionary with keys: 'comms_type', 'channel_name', 'channel_type', 'channel_status'.
    """
    return {
        "comms_type": msg.comms_type,
        "channel_name": msg.channel_name,
        "channel_type": msg.channel_type,
        "channel_status": msg.channel_status,
    }


def publisher_info(msg: publisher_info_t) -> dict[str, Any]:
    """!
    Unpack a publisher_info_t message into a dictionary.

    @param msg  The publisher_info_t message to unpack.
    @return     Dictionary with keys: 'comms_type', 'channel_name', 'channel_type', 'channel_status'.
    """
    return {
        "comms_type": msg.comms_type,
        "channel_name": msg.channel_name,
        "channel_type": msg.channel_type,
        "channel_status": msg.channel_status,
    }


def comms_info(
    msg: comms_info_t,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    """!
    Unpack a comms_info_t message into separate lists of dictionaries.

    @param msg  The comms_info_t message to unpack.
    @return     Tuple of four lists: (listeners, subscribers, publishers, services).
                Each is a list of dicts.
    """
    listeners = [listener_info(l) for l in msg.listeners]  # noqa: E741
    subscribers = [subscriber_info(s) for s in msg.subscribers]
    publishers = [publisher_info(p) for p in msg.publishers]
    services = [service_info(s) for s in msg.services]
    return listeners, subscribers, publishers, services


def node_info(msg: node_info_t) -> tuple[str, str, dict[str, Any]]:
    """!
    Unpack a node_info_t message to retrieve node_name, node_id, and node_infos dictionary.

    @param msg  The node_info_t message to unpack.
    @return     Tuple containing node_name (str), node_id (str), and node_infos (dict).
    """
    node_name = msg.node_name
    node_id = msg.node_id
    listeners, subscribers, publishers, services = comms_info(msg.comms)
    node_infos = {
        "listeners": listeners,
        "subscribers": subscribers,
        "publishers": publishers,
        "services": services,
    }
    return node_name, node_id, node_infos


def network_info(msg: network_info_t) -> list[dict[str, Any]]:
    """!
    Unpack a network_info_t message into a list of dictionaries.

    Each dict contains:
      - 'node_name': str
      - 'node_id': str
      - 'node_infos': dict

    @param msg network_info_t message.
    @return    List of dicts, one per node.
    """
    nodes_list = []
    for node_msg in msg.nodes:
        node_name, node_id, node_infos = node_info(node_msg)
        node_dict = {
            "node_name": node_name,
            "node_id": node_id,
            "node_infos": node_infos,
        }
        nodes_list.append(node_dict)
    return nodes_list


def stamp(msg: stamp_t) -> tuple[int, int]:
    """!
    Unpack a stamp_t message into a tuple (sec, nsec).

    @param msg stamp_t message.
    @return    Tuple of (sec, nsec).
    """
    return msg.sec, msg.nsec


def header(msg: header_t) -> tuple[int, dict[str, int], str]:
    """!
    Unpack a header_t message into its components.

    @param msg header_t message.
    @return    Tuple of (seq, (stamp.sec, stamp.nsec), frame_id).
    """
    seq = msg.seq
    sec, nsec = stamp(msg.stamp)
    stamp_dict = {"sec": sec, "nsec": nsec}
    frame_id = msg.frame_id
    return seq, stamp_dict, frame_id


def joint_state(
    msg: joint_state_t,
) -> tuple[dict, list[str], np.ndarray, np.ndarray, np.ndarray]:
    """!
    Unpack a joint_state_t message.

    @param msg A joint_state_t message.
    @return    Tuple containing:
               - header as a dict with 'seq', 'stamp' (dict), and 'frame_id'
               - name list
               - position numpy array
               - velocity numpy array
               - effort numpy array
    """
    seq, stamp_dict, frame_id = header(msg.header)
    header_dict = {"seq": seq, "stamp": stamp_dict, "frame_id": frame_id}
    name = list(msg.name)
    position_arr = np.array(msg.position)
    velocity = np.array(msg.velocity)
    effort = np.array(msg.effort)
    return header_dict, name, position_arr, velocity, effort


def force(msg: force_t) -> tuple[list[str], np.ndarray]:
    """
    @brief Unpacks a force_t message into separate name and force components.

    @param msg The force_t message to unpack.
    @return A tuple containing:
        - A list of names (list[str])
        - A NumPy array of force values (np.ndarray)
    """
    name = list(msg.name)
    force_values = np.array(msg.force)
    return name, force_values


def ee_pos(msg: ee_pos_t) -> tuple[np.ndarray, np.ndarray]:
    """!
    Unpack an ee_pos_t message.

    @param msg   An ee_pos_t message.
    @return      A tuple containing 'position' and 'quaternion', both numpy arrays.
    """
    pos = position(msg.position)
    quat = quaternion(msg.quaternion)
    return pos, quat


def image(msg: image_t) -> np.ndarray:
    """!
    Unpacks a serialized image_t message into an OpenCV-compatible NumPy array.

    Handles both compressed (JPEG/PNG) and uncompressed image data.

    @param msg The image_t message to be unpacked.
    @return A NumPy array representing the image, or None if unpacking fails.
    """
    img_data = np.frombuffer(msg.data, dtype=np.uint8)

    # Handle compression
    if msg.compression_method in (
        image_t.COMPRESSION_METHOD_JPEG,
        image_t.COMPRESSION_METHOD_PNG,
    ):
        # Decompress image
        img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
        if img is None:
            print("Failed to decompress image")
            return
    elif msg.compression_method == image_t.COMPRESSION_METHOD_NOT_COMPRESSED:
        # Determine the number of channels based on pixel_format
        try:
            # TODO(FV): FIX
            nchannels = num_channels[msg.pixel_format]  # noqa: F821
        except KeyError:
            print("Unsupported pixel format")
            return

        # Reshape the data to the original image dimensions
        try:
            img = img_data.reshape((msg.height, msg.width, nchannels))
        except ValueError as e:
            print(f"Error reshaping image data: {e}")
            return
    else:
        print("Unsupported compression method")
        return
    return img


def depth(msg: image_t) -> np.ndarray:
    """!
    Unpacks a compressed depth image from an image_t message into a NumPy array.

    The function expects the depth data to be zlib-compressed and stored as 16-bit unsigned integers
    representing millimeters. It converts the result to floating-point meters.

    @param msg The image_t message containing compressed depth data.
    @return A 2D NumPy array of depth values in meters.
    """
    depth_data = zlib.decompress(msg.data)
    depth = np.frombuffer(depth_data, dtype=np.uint16)
    depth = depth.astype(np.float32) / 1000
    depth = depth.reshape((msg.height, msg.width))
    return depth


def rgbd(msg: rgbd_t) -> tuple[np.ndarray, np.ndarray]:
    """!
    Unpacks an rgbd_t message into separate RGB image and depth map arrays.

    This function extracts and decodes the image and depth components from an RGB-D message,
    returning them as OpenCV-compatible NumPy arrays.

    @param msg The rgbd_t message containing packed image and depth data.
    @return A tuple (image, depth), where:
        - image: A NumPy array representing the RGB image.
        - depth: A 2D NumPy array representing the depth map in meters.
    """
    rgb_image = image(msg.image)
    depth_map = depth(msg.depth)
    return rgb_image, depth_map


def image_array(msg: image_array_t) -> tuple[int, np.ndarray]:
    """!
    Unpack an image_array_t message.

    @param msg   image_array_t message.
    @return      Tuple with:
                   - 'timestamp_ns': int
                   - 'images': a list of np.ndarray images
    """
    timestamp_ns = msg.timestamp_ns
    img_list = [image(img_msg) for img_msg in msg.images]
    return timestamp_ns, img_list


def laser_scan(msg: laser_scan_t) -> tuple[np.ndarray, np.ndarray]:
    """!
    Unpack a laser_scan_t message into separate NumPy arrays for angles and ranges.

    @param msg  A laser_scan_t message with packed angle and range data.
    @return A tuple of two NumPy arrays: (angles, ranges).
    """
    angles = float_vector(msg.angles)
    ranges = float_vector(msg.ranges)
    return angles, ranges


def pose(msg: pose_t) -> tuple[np.ndarray, np.ndarray]:
    """!
    Unpack a pose_t message into position and orientation numpy arrays.

    @param msg  A pose_t message.
    @return A tuple of (position, orientation) as numpy arrays.
    """
    position = np.array(msg.position)
    orientation = np.array(msg.orientation)
    return position, orientation


def pose_2d(msg: pose_2d_t) -> tuple[float, float, float]:
    """!
    Unpack a pose_2d_t message into individual pose components.

    @param msg  A pose_2d_t message containing x, y, and theta values.
    @return A tuple (x, y, theta) representing the 2D pose.
    """
    x = msg.x
    y = msg.y
    theta = msg.theta
    return x, y, theta


def velocity_2d(msg: velocity_2d_t) -> tuple[float, float, float]:
    """!
    Unpack a velocity_2d_t message into its components .
    @param msg: The velocity_2d_t message to unpack
    @return A tuple containing (v_x, v_y, w).
    """
    v_x = msg.v_x
    v_y = msg.v_y
    w = msg.w
    return v_x, v_y, w


def wheeled_velocity(msg: wheeled_velocity_t) -> tuple[float, float]:
    """!
    Unpack a wheeled_velocity message into linear and angular velocity components.

    @param msg: The wheeled_velocity message to unpack.
    @return A tuple containing (linear_velocity, angular_velocity).
    """
    linear_velocity = msg.linear
    angular_velocity = msg.angular
    return linear_velocity, angular_velocity


def joint_group_command(msg: joint_group_command_t) -> tuple[list, str]:
    """!
    Unpacks a joint group command into the values and the name.

    @param msg  A joint_ground_command_t message
    @return A tuple (cmd, name) representing the command values and the group name
    """
    cmd = msg.cmd
    name = msg.name
    return cmd, name


def joint_single_command(msg: joint_single_command_t) -> tuple[str, float]:
    """!
    Unpack a joint_single_command_t message into name and command value.

    @param msg A joint_single_command_t message.
    @return    A tuple containing (name, cmd).
    """
    name = msg.name
    cmd = msg.cmd
    return name, cmd


def grid_config(msg: grid_config_t) -> tuple[dict[str, list[float]], float]:
    """!
    Unpack a grid_config_t message into scene bounds and grid size.

    @param msg  The grid_config_t message to unpack.
    @return A tuple containing:
            - scene_bounds: A dictionary with 'x' and 'y' keys mapping to the corresponding [min, max] bounds.
            - grid_size: The size of each grid cell.
    """
    scene_bounds = {"x": msg.x_bounds, "y": msg.y_bounds}
    grid_size = msg.grid_size
    return scene_bounds, grid_size


def wheel_config(msg: wheel_config_t) -> tuple:
    """!
    Unpacks a wheel configuration message.
    @param msg The wheel configuration message of type wheel_config_t.
    @return A tuple containing:
        - radius:     Radius of the wheels.
        - thread:     Distance between the wheels
    """
    radius = msg.radius
    thread = msg.thread
    return radius, thread


def imu(msg: imu_t) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """!
    Unpack an imu_t message into orientation, gyroscope, and acceleration values
    @param msg: The imu_t message to unpack.
    @return A tuple containing:
        - orientation: A numpy array of shape (4,) representing the quaternion orientation.
        - gyro:   A numpy array of shape (3,) representing the gyroscope data.
        - accel: A numpy array of shape (3,) representing the acceleration data.
    """
    orientation = np.array(msg.orientation)
    gyro = np.array(msg.gyro)
    accel = np.array(msg.accel)
    return orientation, gyro, accel


def task_space_command(
    msg: task_space_command_t,
) -> tuple[str, np.ndarray, np.ndarray, float]:
    """!
    Unpack a task_space_command_t message into its components.

    @param msg  A task_space_command_t message.
    @return     A tuple containing:
                - name: The name of the task space command.
                - position: A numpy array representing the position.
                - quaternion: A numpy array representing the quaternion orientation.
    """
    name = msg.name
    position_arr = position(msg.position)
    quaternion_arr = quaternion(msg.quaternion)
    gripper_val = msg.gripper  # Assuming gripper is a float value
    return name, position_arr, quaternion_arr, gripper_val
