import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from std_msgs.msg import Float32
import math


class DistancePublisher(Node):
    def __init__(self):
        super().__init__('distance_publisher')

        self.declare_parameter('publish_rate', 10.0)
        self.last_pose = None

        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10)
        self.dist_pub = self.create_publisher(Float32, '/turtle_distance', 10)

        rate = self.get_parameter('publish_rate').value

        # 예외 처리: publish_rate가 0 이하이면 경고 후 기본값 사용
        if rate <= 0:
            self.get_logger().warn(
                f'Invalid publish_rate={rate}, using default 10.0 Hz')
            rate = 10.0

        timer_period = 1.0 / rate
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.get_logger().info(
            f'Distance publisher started at {rate} Hz')

    def pose_callback(self, msg):
        """구독 콜백: 최신 pose만 저장 (발행은 여기서 안 함!)"""
        self.last_pose = msg

    def timer_callback(self):
        """타이머 콜백: 저장된 pose로 거리 계산 후 발행"""
        if self.last_pose is None:
            return  

        distance = math.sqrt(
            self.last_pose.x ** 2 + self.last_pose.y ** 2)

        msg = Float32()
        msg.data = distance
        self.dist_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)               
    node = DistancePublisher()      
    try:
        rclpy.spin(node)              
    except KeyboardInterrupt:
        pass                        
    finally:
        node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()