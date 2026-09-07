import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class DistanceSubscriber(Node):
    def __init__(self):
        super().__init__('distance_subscriber')

        self.declare_parameter('warn_distance', 2.5)

        self.dist_sub = self.create_subscription(
            Float32, '/turtle_distance', self.dist_callback, 10)

        self.get_logger().info('Distance subscriber started')

    def dist_callback(self, msg):
        """거리값을 받아 임계값 초과 시 경고 로그"""
        threshold = self.get_parameter('warn_distance').value

        if msg.data > threshold:
            self.get_logger().warn(
                f'Turtle too far from origin! '
                f'distance={msg.data:.2f}, threshold={threshold:.1f}')
        else:
            self.get_logger().info(f'distance={msg.data:.2f}')


def main(args=None):
    rclpy.init(args=args)
    node = DistanceSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
