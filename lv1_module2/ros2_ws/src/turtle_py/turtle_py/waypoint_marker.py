import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point


class WaypointMarker(Node):
    def __init__(self):
        super().__init__('waypoint_marker')

        self.marker_pub = self.create_publisher(
            Marker, '/waypoints', 10)

        self.waypoints = [
            (5.54, 5.54),
            (7.54, 5.54),
            (7.54, 7.54),
            (5.54, 7.54),
        ]

        self.timer = self.create_timer(1.0, self.timer_callback)
        self.get_logger().info('Waypoint marker publisher started')

    def timer_callback(self):
        # 예외 처리: 경유점 목록이 비어있으면 경고 후 스킵
        if not self.waypoints:
            self.get_logger().warn('Waypoint list is empty, skipping publish')
            return
        
        marker = Marker()
        marker.header.frame_id = 'world'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'waypoints'
        marker.id = 0
        marker.type = Marker.SPHERE_LIST
        marker.action = Marker.ADD

        marker.scale.x = 0.3
        marker.scale.y = 0.3
        marker.scale.z = 0.3

        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        marker.color.a = 1.0

        for wx, wy in self.waypoints:
            p = Point()
            p.x = wx
            p.y = wy
            p.z = 0.0
            marker.points.append(p)

        self.marker_pub.publish(marker)


def main(args=None):
    rclpy.init(args=args)
    node = WaypointMarker()
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
