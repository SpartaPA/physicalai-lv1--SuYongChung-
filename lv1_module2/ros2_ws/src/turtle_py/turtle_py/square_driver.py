import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math


class SquareDriver(Node):
    def __init__(self):
        super().__init__('square_driver')

        self.cmd_pub = self.create_publisher(
            Twist, '/turtle1/cmd_vel', 10)

        self.state = 'forward'
        self.side_count = 0
        self.elapsed = 0.0

        self.linear_speed = 1.0
        self.side_length = 2.0
        self.angular_speed = math.pi / 2

        self.forward_duration = self.side_length / self.linear_speed
        self.turn_duration = (math.pi / 2) / self.angular_speed

        self.dt = 0.1
        self.timer = self.create_timer(self.dt, self.timer_callback)

        self.get_logger().info('Square driver started')

    def timer_callback(self):
        if self.side_count >= 4:
            self.cmd_pub.publish(Twist())
            self.get_logger().info('Square complete!')
            self.timer.cancel()
            raise SystemExit

        msg = Twist()
        self.elapsed += self.dt  

        if self.state == 'forward':
            if self.elapsed >= self.forward_duration:
                self.state = 'turn'
                self.elapsed = 0.0
            else:
                msg.linear.x = self.linear_speed
        elif self.state == 'turn':
            if self.elapsed >= self.turn_duration:
                self.state = 'forward'
                self.elapsed = 0.0
                self.side_count += 1
            else:
                msg.angular.z = self.angular_speed

        self.cmd_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SquareDriver()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()