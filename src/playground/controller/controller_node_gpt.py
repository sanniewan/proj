import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class ControllerNode(Node):
    def __init__(self):
        # Initialize the ROS 2 node with the name "controller_node"
        super().__init__('controller_node')

        # Declare a ROS parameter named 'target_value' with default value 5.0.
        # This is the desired setpoint that the controller tries to reach.
        self.declare_parameter('target_value', 5.0)

        # Retrieve the actual value of the 'target_value' parameter.
        self.target = self.get_parameter('target_value').value

        # Define the proportional gain (Kp) for the controller.
        # This determines how aggressively the controller reacts to the error.
        self.kp = 1.0

        # Create a publisher to send control signals (Float32) on the 'control_signal' topic.
        # The actuator node should subscribe to this topic.
        self.control_pub = self.create_publisher(Float32, 'control_signal', 10)

        # Create a subscriber to the 'sensor_data' topic, listening for Float32 messages.
        # Every time new data arrives, the callback function `sensor_callback` is triggered.
        self.sensor_sub = self.create_subscription(Float32, 'sensor_data', self.sensor_callback, 10)

        # Log an informational message showing the set target value
        self.get_logger().info(f'Controller initialized with target: {self.target}')

    def sensor_callback(self, msg: Float32):
        """
        Callback function triggered whenever new sensor data is received.

        Args:
            msg (Float32): The incoming sensor data message.
        """

        # Calculate the error between the desired target and the current sensor reading
        error = self.target - msg.data

        # Apply proportional control: control effort = Kp * error
        control_effort = self.kp * error

        # Log what’s happening: the received sensor value, the computed error, and the resulting control signal
        self.get_logger().info(
            f'Received: {msg.data:.2f}, Error: {error:.2f}, Control: {control_effort:.2f}'
        )

        # Publish the control effort to the 'control_signal' topic
        self.control_pub.publish(Float32(data=control_effort))


def main():
    # Initialize the ROS 2 Python client library
    rclpy.init()

    # Create an instance of the controller node
    node = ControllerNode()

    # Keep the node running, waiting for callbacks
    rclpy.spin(node)

    # Once the node is shut down (e.g., via Ctrl+C), clean up
    node.destroy_node()
    rclpy.shutdown()
