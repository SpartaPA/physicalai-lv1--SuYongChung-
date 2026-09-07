import math


def compute_distance(x, y):
    """원점(0,0)에서 (x, y)까지의 거리"""
    return math.sqrt(x ** 2 + y ** 2)


def compute_heading(x_current, y_current, x_target, y_target):
    """현재 위치에서 목표까지의 방향각 (rad, -π ~ π)"""
    dx = x_target - x_current
    dy = y_target - y_current
    angle = math.atan2(dy, dx)
    return angle


def normalize_angle(angle):
    """임의의 각도를 -π ~ π 범위로 정규화"""
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


def is_waypoint_reached(x, y, wx, wy, tolerance=0.5):
    """현재 위치 (x,y)가 경유점 (wx,wy)에 도달했는지 판정"""
    dist = math.sqrt((x - wx) ** 2 + (y - wy) ** 2)
    return dist <= tolerance
