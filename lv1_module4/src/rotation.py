"""문제 2·3 — 회전 행렬 모듈. (학생 작성용 템플릿)

축별 회전 행렬, 로드리게스 공식(임의 축 회전), Gram-Schmidt 재직교화,
회전행렬 판정과 고유값 분해 기반 축·각 복원을 직접 구현한다.

문제 1 에서 만든 `src/vectors.py` 를 그대로 재사용한다.
"""

from __future__ import annotations

import numpy as np

from .vectors import det, normalize, skew

__all__ = [
    "rot_x",
    "rot_y",
    "rot_z",
    "rodrigues",
    "gram_schmidt",
    "orthogonality_error",
    "is_rotation",
    "axis_angle_from_matrix",
    "quaternion_from_axis_angle",
]


# ------------------------------------------------------------ 축별 회전 행렬

def rot_x(theta: float) -> np.ndarray:
    """x축 기준 회전 행렬 (theta 는 **라디안**). x 성분은 보존된다."""
    # TODO: 문제 2-1
    c, s = np.cos(theta), np.sin(theta)
    return np.array([
        [1, 0, 0],
        [0, c, -s],
        [0, s, c],
    ])


def rot_y(theta: float) -> np.ndarray:
    """y축 기준 회전 행렬 (theta 는 라디안). y 성분은 보존된다.

    부호 배치가 x·z 와 반대로 보이는 이유는 노트북 2-1 에서 설명한다.
    """
    # TODO: 문제 2-1
    c, s = np.cos(theta), np.sin(theta)
    return np.array([
        [c, 0, s],
        [0, 1, 0],
        [-s, 0, c],
    ])


def rot_z(theta: float) -> np.ndarray:
    """z축 기준 회전 행렬 (theta 는 라디안). z 성분은 보존된다."""
    # TODO: 문제 2-1
    c, s = np.cos(theta), np.sin(theta)
    return np.array([
        [c, -s, 0],
        [s, c, 0],
        [0, 0, 1],
    ])
    


def rodrigues(axis, theta: float) -> np.ndarray:
    """로드리게스 공식으로 임의 축 회전 행렬을 만든다.

        R = I + sin(theta) * K + (1 - cos(theta)) * K @ K,   K = [k]_x

    - 축은 함수 안에서 단위벡터로 정규화한다
      (정규화되지 않은 축을 넣어도 같은 결과가 나와야 한다).
    - 문제 1 의 `skew` 를 반드시 사용한다.
    """
    # TODO: 문제 2-5
    # 1) 축을 단위벡토로 정규화
    k = normalize(np.asarray(axis, dtype = float))
    # 2) skew 행렬 만들기
    K = skew(k)
    # 3) 로드리게스 공식 적용
    R = np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * K @ K
    return R


# ------------------------------------------------------------- 재직교화 관련

def gram_schmidt(A) -> np.ndarray:
    """**열벡터**에 대해 Gram-Schmidt 직교정규화를 수행한다.

        q1 = a1 / |a1|
        vj = aj - sum_{i<j} (qi · aj) qi
        qj = vj / |vj|

    각 열에서 앞선 열 방향 성분(정사영)을 빼고 정규화하는 것이며,
    문제 1 의 project / reject 와 같은 연산의 반복이다.

    수치적으로는 성분을 빼자마자 갱신하는 modified Gram-Schmidt 가 더 안정적이다.
    앞선 열들에 종속인 열이 있으면 ValueError.
    """
    # TODO: 문제 3-2
    A = np.array(A, dtype=float)
    n = A.shape[1] # 열 개수 (3)
    Q = np.zeros_like(A) # 결과 저장할 빈 행렬. A와 같은 모양의 0으로 채워진 행렬

    for j in range(n): # 열 하나씩(j = 0, 1, 2)
        v = A[:, j].copy() # j번째 열 꺼내서 작업용 변수에 복사

        for i in range(j): # 이미 확정된 q들에 대해
            v = v - np.dot(Q[:, i], v) * Q[:, i] # 내적 q·v = p.dot(Q[:, i] * v)

        norm = np.sqrt(np.sum(v * v)) # 길이 구하기
        if norm < 1e-12: # 길이가 0이면 종속
            raise ValueError("열벡터가 종속입니다.")

        Q[:, j] = v / norm # 길이 1로 정규화해서 저장

    # det 보정: 축이 뒤집혀있으면 마지막 열 부호 바꾸기
    if det(Q) < 0:
        Q[:, j] *= -1

    return Q




def orthogonality_error(R) -> float:
    """직교성 이탈 지표: || R^T R - I ||_F  (프로베니우스 노름).

    완전한 직교행렬이면 0 이고, 클수록 직교성이 무너진 것이다.
    """
    # TODO: 문제 3-1
    # 1. R을 numpy 배열로 확보 
    R = np.asarray(R, dtype=float)

    # 2. R^T R 계산 (행렬 곱)
    RtR = R.T @ R

    # 3. 단위행렬 만들기
    I = np.eye(R.shape[0])

    # 4. 오차 행렬 = R^T - I
    diff = RtR - I

    # 5. 프로베니우스 노름 = 모든 원소 제곱(diff ** 2로 표현해도 된다.) -> 합 -> 루트
    error = np.sqrt(np.sum(diff * diff))

    return float(error)



def is_rotation(R, atol: float = 1e-8) -> bool:
    """회전행렬 판정: 직교(R^T R = I) **그리고** det(R) = +1 이면 True.

    det = -1 이면 직교이긴 하지만 반사가 섞여 있어 회전이 아니다.
    3x3 이 아니면 False.
    """
    # TODO: 문제 3-2
    R = np.asarray(R, dtype=float)

    # 조건 1. 3 x 3 행렬인가?
    if R.shape != (3, 3):
        return False

    # 조건 2. 직교행렬인가? (R^T R = I)
    if orthogonality_error(R) > atol:
        return False

    # 조건 3. det = +1인가? (반사가 아니라 회전)
    if abs(det(R) - 1.0) > atol:
        return False

    return True


# --------------------------------------------------- 회전축·회전각·쿼터니언

def axis_angle_from_matrix(R, atol: float = 1e-8):
    """고유값 분해로 회전축을, 대각합으로 회전각을 복원한다.

    - 회전축은 고유값 1 에 대응하는 실수 고유벡터다 (R k = k).
      -> 여기서는 `np.linalg.eig` 를 써도 된다 (검산이 아니라 축 복원이 목적).
    - 회전각은 trace(R) = 1 + 2 cos(theta) 에서 구한다.
    - arccos 의 치역이 [0, pi] 라 '어느 쪽으로 도는지'는 알 수 없고,
      고유벡터도 부호가 정해지지 않는다. 반대칭 성분
      R - R^T = 2 sin(theta) [k]_x 를 이용해 부호를 맞춘다.
    - theta = 0 (회전 없음) 과 theta = pi (sin = 0) 는 따로 처리해야 한다.
      두 경우에 어떤 규약을 쓸지 정하고 주석으로 남긴다.

    Returns
    -------
    axis : 단위 회전축 (3,)
    angle : 회전각 [rad], 0 <= angle <= pi
    """
    # TODO: 문제 6-4
    R = np.asarray(R, dtype=float)

    # ── 1) trace로 회전각 구하기 ──
    #    trace(R) = 1 + 2·cos(θ)  →  cos(θ) = (trace - 1) / 2
    cos_theta = (np.trace(R) - 1.0) / 2.0
    cos_theta = np.clip(cos_theta, -1.0, 1.0)  # 부동소수점 보호
    theta = float(np.arccos(cos_theta))

    # ── 2) 특수 경우: θ ≈ 0 (회전 없음) ──
    # 안 돌았으면 축이 정의 안 됨 → 규약으로 z축 반환
    if theta < atol:
        return np.array([0.0, 0.0, 1.0]), 0.0

    # ── 3) 고유값 분해로 회전축 찾기 ──
    # 고유값이 1인 고유벡터 = 회전축 (돌려도 안 움직이는 방향)
    eigvals, eigvecs = np.linalg.eig(R)

    # 고유값 중 1에 가장 가까운 놈의 인덱스
    idx = np.argmin(np.abs(eigvals - 1.0))

    # 그 고유벡터 (복소수일 수 있으니 실수부만 취함)
    axis = eigvecs[:, idx].real

    # 단위벡터로 정규화
    axis = normalize(axis)

    # ── 4) 특수 경우: θ ≈ π (180도) ──
    # sin(θ) ≈ 0이라 R-R^T로 부호 결정 불가
    # 규약: 첫 번째 유의미한 성분이 양수가 되도록
    if abs(theta - np.pi) < atol:
        for j in range(3):
            if abs(axis[j]) > atol: # 0이 아닌 첫 성분 찾기
                if axis[j] < 0: # 음수면 축 전체 뒤집기
                    axis = -axis
                break
        return axis, theta

    # ── 5) 일반 경우: R - R^T 로 부호 결정 ──
    # R - R^T = 2·sin(θ)·skew(k) 이므로
    # 여기서 축 방향 성분을 꺼낼 수 있다
    v = np.array([
        R[2, 1] - R[1, 2],    # 2·sin(θ)·k₁
        R[0, 2] - R[2, 0],    # 2·sin(θ)·k₂
        R[1, 0] - R[0, 1],    # 2·sin(θ)·k₃
    ])

    # v와 axis가 반대 방향이면 축을 뒤집는다
    if np.dot(v, axis) < 0:
        axis = -axis

    return axis, theta


def quaternion_from_axis_angle(axis, angle: float) -> np.ndarray:
    """축-각에서 단위 쿼터니언을 만든다.

        q = (k * sin(theta/2), cos(theta/2))

    반환 순서는 SciPy `Rotation.as_quat()` 와 같은 **(x, y, z, w)** 로 맞춘다
    (그래야 문제 6-5 에서 바로 비교할 수 있다).
    """
    # TODO: 문제 6-5
    axis = normalize(np.asarray(axis, dtype=float))  # 단위벡터 보장
    half = angle / 2.0
    # (x, y, z, w) 순서 — SciPy와 동일
    return np.array([
        axis[0] * np.sin(half),   # x
        axis[1] * np.sin(half),   # y
        axis[2] * np.sin(half),   # z
        np.cos(half),             # w
    ])
