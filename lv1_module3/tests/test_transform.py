"""문제 5 — 동차변환 inv_T 검증 (pytest). [학생 작성용 템플릿]

지시문이 요구하는 것은 `inv_T` 검증이지만,
점/방향 구분과 벡터화, 최소자승까지 함께 검증해 두면 이후 문제에서 안전하다.

실행: 프로젝트 루트에서  pytest -v
"""

import numpy as np
import pytest

from src.rotation import rot_x, rot_y, rot_z
from src.transform import (
    inv_T,
    least_squares_normal_equation,
    make_T,
    transform_direction,
    transform_point,
    transform_points,
)


@pytest.fixture
def T():
    """테스트에 쓸 대표 동차변환 하나."""
    R = rot_z(0.6) @ rot_y(-0.25) @ rot_x(1.1)
    return make_T(R, [0.3, -0.2, 0.45])


def test_inv_T_gives_identity(T):
    # TODO: inv_T(T) @ T 와 T @ inv_T(T) 가 모두 4x4 단위행렬인지 검사
    raise NotImplementedError("test_inv_T_gives_identity 를 작성하세요")


def test_inv_T_matches_generic_inverse(T):
    # TODO: inv_T(T) 가 np.linalg.inv(T) 와 일치하는지 검사 (np.linalg 는 검산용)
    raise NotImplementedError("test_inv_T_matches_generic_inverse 를 작성하세요")


def test_point_and_direction_differ(T):
    # TODO: 같은 벡터를 점(w=1)/방향(w=0)으로 변환하면 결과가 다르고,
    #       그 차이가 정확히 병진 벡터 T[:3, 3] 이며,
    #       방향 변환은 길이를 보존하는지 검사
    raise NotImplementedError("test_point_and_direction_differ 를 작성하세요")


def test_transform_points_is_vectorized(T):
    # TODO: (N,3) 점군을 한 번에 변환한 결과가
    #       transform_point 를 반복문으로 돌린 결과와 같은지 검사
    raise NotImplementedError("test_transform_points_is_vectorized 를 작성하세요")


def test_roundtrip_through_inverse(T):
    # TODO: T 로 보냈다가 inv_T(T) 로 되돌리면 원래 점군이 나오는지 검사
    raise NotImplementedError("test_roundtrip_through_inverse 를 작성하세요")


def test_least_squares_matches_lstsq():
    # TODO: 노이즈를 섞은 과결정 문제를 만들어
    #       least_squares_normal_equation 의 해가 np.linalg.lstsq 와 일치하고
    #       잔차가 A 의 열공간에 수직(A^T r = 0)인지 검사
    raise NotImplementedError("test_least_squares_matches_lstsq 를 작성하세요")
