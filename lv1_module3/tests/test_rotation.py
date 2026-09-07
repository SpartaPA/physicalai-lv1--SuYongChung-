"""문제 3 — 회전 행렬의 수학적 성질 검증 (pytest). [학생 작성용 템플릿]

지시문이 요구하는 4가지를 각각 테스트 함수로 작성한다.

  1. 회전행렬의 열이 서로 직교하는 단위벡터인가   -> test_columns_are_orthonormal
  2. 행렬식이 1인가                               -> test_determinant_is_one
  3. 역행렬이 전치와 같은가                       -> test_inverse_equals_transpose
  4. 재직교화 결과가 직교행렬인가                 -> test_gram_schmidt_restores_orthogonality

작성 요령
--------
- `@pytest.mark.parametrize` 로 여러 축 x 여러 각도를 한 함수에서 검사하면
  테스트 하나가 여러 케이스를 담당한다 (아래 ANGLES / MAKERS 참고).
- 비교는 반드시 `np.isclose` / `np.allclose` 로 한다 (부동소수점).
- `np.linalg` 는 검산용으로만 쓰고, 쓸 때는 주석으로 검산임을 밝힌다.
- assert 에 실패 메시지를 붙이면 어디가 깨졌는지 바로 보인다.
- 4개는 **최소 개수**다. 반사 행렬 반례, 로드리게스 일치, 축·각 왕복 같은
  테스트를 더 붙이면 좋다.

실행: 프로젝트 루트에서  pytest -v
"""

import numpy as np
import pytest

from src.rotation import (
    axis_angle_from_matrix,
    gram_schmidt,
    is_rotation,
    orthogonality_error,
    rodrigues,
    rot_x,
    rot_y,
    rot_z,
)
from src.vectors import det # def test_determinant_is_one에 det 함수 추가

ANGLES = [0.0, np.deg2rad(22.5), np.pi / 6, np.pi / 4, np.pi / 2, 2.0, np.pi, -1.234]
MAKERS = [rot_x, rot_y, rot_z]


@pytest.fixture
def rng():
    """난수는 반드시 시드를 고정한다."""
    return np.random.default_rng(42)


# --- 1. 열이 서로 직교하는 단위벡터인가 -------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_columns_are_orthonormal(maker, theta):
    # TODO: 각 열의 길이가 1 인지, 서로 다른 두 열의 내적이 0 인지 검사
    R = maker(theta) # maker는 rot_x, rot_y, rot_z중 하나다. theta를 넣으면 회전행렬이 나온다.
    for j in range(3):
        col_len = np.sqrt(np.sum(R[:, j] * R[:, j])) # j번째 열의 길이
        assert np.isclose(col_len, 1.0), f"열 {j}의 길이가 1이 아님: {col_len}"
    for i in range(3):
        for j in range(i + 1, 3):
            dot_val = np.dot(R[:, i], R[:, j])
            assert np.isclose(dot_val, 0.0), f"열 {i}과 열 {j}이 수직이 아님: {dot_val}"



# --- 2. 행렬식이 1인가 --------------------------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_determinant_is_one(maker, theta):
    # TODO: det(R) == 1 인지 검사
    R = maker(theta)
    assert np.isclose(det(R), 1.0), "행렬식이 1이 아님"


# --- 3. 역행렬 == 전치 --------------------------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_inverse_equals_transpose(maker, theta):
    # TODO: inv(R) == R.T 이고 R.T @ R == I 인지 검사
    R = maker(theta)
    assert np.allclose(R.T @ R, np.eye(3)), "역행렬이 전치와 다름" # np.allclose는 배열 안의 모든 원소를 비교하는 함수


# --- 4. 재직교화 결과가 직교행렬인가 -----------------------------------------

def test_gram_schmidt_restores_orthogonality(rng):
    # TODO: 회전행렬에 작은 노이즈를 섞어 직교성을 깨뜨린 뒤,
    #       gram_schmidt 로 복구하면 직교성 오차가 기계정밀도 수준으로 줄고
    #       det 가 1 이며 is_rotation 이 True 인지 검사
    R = rot_x(0.3) @ rot_y(0.7)
    noisy = R + 1e-3 * rng.standard_normal((3, 3)) # rng.standard_normal((3, 3))은 3 x 3 랜덤 행렬, 1e-3을 곱해서 아주 작은 노이즈를 만드는 것
    fixed = gram_schmidt(noisy)

    assert orthogonality_error(fixed) < 1e-14, "직교성 복수 실패"
    assert np.isclose(det(fixed), 1.0), "행렬식이 1이 아님"
    assert is_rotation(fixed), "회전행렬이 아님"


# --- 여기부터는 추가 테스트 (권장) -------------------------------------------
#
def test_reflection_is_not_a_rotation():
    """det = -1 인 반사 행렬은 직교여도 회전이 아니다."""
    reflect = np.diag([-1.0, 1.0, 1.0]) # np.diag([-1, 1, 1])는 대각선에 -1, 1, 1을 넣은 행렬
    assert not is_rotation(reflect), "반사 행렬을 회전으로 팔정함" # assert not 은 False여야 통과

@pytest.mark.parametrize("theta", ANGLES)
def test_rodrigues_matches_rot_z(theta):
    """rodrigues(z축, theta) 가 rot_z(theta) 와 일치해야 한다."""
    R_rod = rodrigues([0, 0, 1], theta)
    R_z = rot_z(theta)
    assert np.allclose(R_rod, R_z), "rodrigues 결과가 rot_z와 다름"

#def axis_angle_from_matrix(R, atol=1e-8):
    # TODO: 문제 6-4
#    raise NotImplementedError("axis_angle_from_matrix 를 구현하세요")
