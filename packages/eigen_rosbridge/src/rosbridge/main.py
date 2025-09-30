from functools import partial

try:
    import rospy  # pyright: ignore[reportMissingImports]
except ImportError:
    print("ROS1 is not installed or `rospy` can't be imported.")
    exit(1)

from eigen.core.client.comm_infrastructure.base_node import BaseNode
from eigen.core.tools.log import log

__doc__ = """EIGEN to ROS translator"""


class EigenRosBridge(BaseNode):
    def __init__(
        self, mapping_table, node_name="EIGEN_ROS_Bridge", global_config=None
    ):
        super().__init__(node_name, global_config=global_config)
        self.ros_to_eigen_mapping = []

        ros_to_eigen_table = mapping_table["ros_to_eigen"]
        eigen_to_ros_table = mapping_table["eigen_to_ros"]

        for mapping in ros_to_eigen_table:
            ros_channel = mapping["ros_channel"]
            ros_type = mapping["ros_type"]
            eigen_channel = mapping["eigen_channel"]
            eigen_type = mapping["eigen_type"]
            translator_callback = mapping["translator_callback"]

            publisher = self.create_publisher(eigen_channel, eigen_type)

            modified_callback = partial(
                self._generic_ros_to_eigen_translator_callback,
                translator_callback=translator_callback,
                ros_channel=ros_channel,
                ros_type=ros_type,
                eigen_channel=eigen_channel,
                eigen_type=eigen_type,
                publisher=publisher,
            )

            rospy.Subscriber(ros_channel, ros_type, modified_callback)

            ros_to_eigen_map = {
                "ros_channel": ros_channel,
                "ros_type": ros_type,
                "eigen_channel": eigen_channel,
                "eigen_type": eigen_type,
                "translator_callback": translator_callback,
                "publisher": publisher,
            }
            self.ros_to_eigen_mapping.append(ros_to_eigen_map)

        self.eigen_to_ros_mapping = []

        for mapping in eigen_to_ros_table:
            eigen_channel = mapping["eigen_channel"]
            eigen_type = mapping["eigen_type"]
            ros_channel = mapping["ros_channel"]
            ros_type = mapping["ros_type"]
            translator_callback = mapping["translator_callback"]

            # Create a listener
            publisher = rospy.Publisher(ros_channel, ros_type, queue_size=10)

            modified_callback = partial(
                self._generic_eigen_to_ros_translator_callback,
                translator_callback=translator_callback,
                eigen_channel=eigen_channel,
                eigen_type=eigen_type,
                ros_channel=ros_channel,
                ros_type=ros_type,
                publisher=publisher,
            )

            # Create a ROS publisher
            self.create_subscriber(eigen_channel, eigen_type, modified_callback)

            ros_to_eigen_map = {
                "ros_channel": ros_channel,
                "ros_type": ros_type,
                "eigen_channel": eigen_channel,
                "eigen_type": eigen_type,
                "translator_callback": translator_callback,
                "publisher": publisher,
            }
            self.eigen_to_ros_mapping.append(ros_to_eigen_map)

        # Create a minimal ROS node
        rospy.init_node(node_name, anonymous=True)

    def _generic_ros_to_eigen_translator_callback(
        self,
        ros_msg,
        translator_callback,
        ros_channel,
        ros_type,
        eigen_channel,
        eigen_type,
        publisher,
    ):
        """
        This is the modified callback that includes the ROS channel and eigen publisher.
        """
        eigen_msg = translator_callback(
            ros_msg, ros_channel, ros_type, eigen_channel, eigen_type
        )
        publisher.publish(eigen_msg)

    def _generic_eigen_to_ros_translator_callback(
        self,
        t,
        _,
        eigen_msg,
        translator_callback,
        eigen_channel,
        eigen_type,
        ros_channel,
        ros_type,
        publisher,
    ):
        """
        This is the modified callback that includes the eigen channel and ROS publisher.
        """
        ros_msg = translator_callback(t, eigen_channel, eigen_msg)
        publisher.publish(ros_msg)

    def spin(self) -> None:
        """!
        Runs the node’s main loop, handling eigen messages continuously until the node is finished.

        The loop calls `self._eigen.handle()` to process incoming messages. If an OSError is encountered,
        the loop will stop and the node will shut down.
        """
        while not self._done and not rospy.is_shutdown():
            try:
                self._lcm.handle_timeout(0)
                # rospy.spin()
            except OSError as e:
                log.warning(f"Eigen or ROS threw OSError {e}")
                self._done = True

    @staticmethod
    def get_cli_doc():
        return __doc__

    def shutdown(self) -> None:
        """!
        Shuts down the node by stopping all communication handlers and steppers.

        Iterates through all registered communication handlers and steppers, shutting them down.
        """
        for ch in self._comm_handlers:
            ch.shutdown()
        for s in self._steppers:
            s.shutdown()
