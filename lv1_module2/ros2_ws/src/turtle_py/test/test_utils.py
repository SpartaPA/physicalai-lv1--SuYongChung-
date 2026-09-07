import math
import pytest
from turtle_py.utils import (
    compute_distance,
    compute_heading,
    normalize_angle,
    is_waypoint_reached,
)


class TestComputeDistance:
    """목표까지의 거리 계산 테스트"""

    def test_origin(self):
        """원점에서의 거리는 0"""
        assert compute_distance(0.0, 0.0) == 0.0

    def test_known_value(self):
        """3-4-5 삼각형"""
        assert math.isclose(compute_distance(3.0, 4.0), 5.0)

    def test_negative_coords(self):
        """음수 좌표도 정상 동작"""
        assert math.isclose(compute_distance(-3.0, -4.0), 5.0)

    def test_turtle_initial(self):
        """거북이 초기 위치 (5.54, 5.54)"""
        assert math.isclose(compute_distance(5.54, 5.54), 7.835, rel_tol=1e-2)


class TestComputeHeading:
    """목표를 향한 각도 테스트"""

    def test_east(self):
        """동쪽(+x) 방향 → 0 rad"""
        assert math.isclose(compute_heading(0, 0, 1, 0), 0.0)

    def test_north(self):
        """북쪽(+y) 방향 → π/2"""
        assert math.isclose(compute_heading(0, 0, 0, 1), math.pi / 2)

    def test_west(self):
        """서쪽(-x) 방향 → π"""
        assert math.isclose(compute_heading(0, 0, -1, 0), math.pi)

    def test_south(self):
        """남쪽(-y) 방향 → -π/2"""
        assert math.isclose(compute_heading(0, 0, 0, -1), -math.pi / 2)

    def test_same_position(self):
        """같은 위치 → 0 rad"""
        assert math.isclose(compute_heading(1, 1, 1, 1), 0.0)


class TestNormalizeAngle:
    """각도 정규화 테스트 (-π ~ π)"""

    def test_within_range(self):
        """범위 내 값은 그대로"""
        assert math.isclose(normalize_angle(1.0), 1.0)

    def test_over_pi(self):
        """2π → 0"""
        assert math.isclose(normalize_angle(2 * math.pi), 0.0, abs_tol=1e-9)

    def test_under_neg_pi(self):
        """-3π → π"""
        assert math.isclose(normalize_angle(-3 * math.pi), -math.pi, abs_tol=1e-9)


class TestIsWaypointReached:
    """경유점 도달 판정 테스트"""

    def test_exact_match(self):
        """정확히 경유점 위에"""
        assert is_waypoint_reached(5.0, 5.0, 5.0, 5.0) is True

    def test_within_tolerance(self):
        """허용 오차 이내"""
        assert is_waypoint_reached(5.3, 5.0, 5.0, 5.0, tolerance=0.5) is True

    def test_on_boundary(self):
        """경계값 (거리 == tolerance)"""
        assert is_waypoint_reached(5.5, 5.0, 5.0, 5.0, tolerance=0.5) is True

    def test_outside_tolerance(self):
        """허용 오차 초과"""
        assert is_waypoint_reached(6.0, 5.0, 5.0, 5.0, tolerance=0.5) is False

    def test_zero_tolerance(self):
        """tolerance=0 → 정확히 일치해야만 True"""
        assert is_waypoint_reached(5.0, 5.0, 5.0, 5.0, tolerance=0.0) is True
        assert is_waypoint_reached(5.01, 5.0, 5.0, 5.0, tolerance=0.0) is False
