"""문제 5 — 4x4 동차변환 모듈. (학생 작성용 템플릿)

동차변환 생성/역변환, 점과 방향의 구분, 벡터화된 점군 변환,
정규방정식 기반 최소자승법을 직접 구현한다.
"""

from __future__ import annotations

import numpy as np

from .vectors import inverse_gauss_jordan

__all__ = [
    "make_T",
    "inv_T",
    "inv_T_batch",
    "to_homogeneous",
    "transform_point",
    "transform_direction",
    "transform_points",
    "least_squares_normal_equation",
    "rmse",
]


def make_T(R, t) -> np.ndarray:
    """회전 R(3x3)과 병진 t(3,)로 4x4 동차변환을 만든다.

        T = [[R, t],
             [0, 1]]

    R 이 3x3 이 아니면 ValueError.
    """
    # TODO: 문제 5-1
    R = np.asarray(R, dtype=float)
    t = np.asarray(t, dtype=float)
    if R.shape != (3, 3):
        raise ValueError("R은 3x3이어야 합니다.")
    
    T = np.eye(4)
    T[:3, :3] = R # 왼쪽 위 3 x 3
    T[:3, 3] = t
    # 마지막 행은 이미 [0, 0, 0, 1]
    # T = np.block([[R, t.reshape(3,1)], [np.zeros((1,3)), np.ones((1,1))]])를 사용해도 되지만  슬라이싱 방법이 가장 깔끔하다.
    return T


def inv_T(T) -> np.ndarray:
    """동차변환의 역변환. **일반 역행렬 함수를 쓰지 않고** 공식으로 구한다.

        T^-1 = [[R^T, -R^T t],
                [  0,      1]]

    유도: T^-1 을 [[S, u], [0, 1]] 로 두고 T T^-1 = I 를 풀면
          R S = I -> S = R^T (R 이 직교),  R u + t = 0 -> u = -R^T t.

    4x4 가 아니면 ValueError.
    """
    # TODO: 문제 5-1
    T = np.asarray(T, dtype=float)
    if T.shape != (4, 4):
        raise ValueError("4x4 행렬이어야 합니다.")
    
    R = T[:3, :3]       # T에서 회전 부분 꺼내기
    t = T[:3, 3]        # T에서 병진 부분 꺼내기
    
    T_inv = np.eye(4)
    T_inv[:3, :3] = R.T          # R의 전치
    T_inv[:3, 3] = -R.T @ t     # -R^T * t
    
    return T_inv



def inv_T_batch(Ts) -> np.ndarray:
    """(N, 4, 4) 동차변환 묶음을 **반복문 없이** 한 번에 역변환한다.

    `inv_T` 와 같은 공식을 배치 축으로 확장한 것이다.
    문제 5-4 의 속도 비교에서 쓴다 — 단건 호출은 파이썬/NumPy 호출 오버헤드가
    지배해서 연산량 차이가 드러나지 않기 때문이다.

    힌트: 전치는 `np.swapaxes(..., 1, 2)`, 배치 행렬-벡터 곱은
          `np.einsum("nij,nj->ni", ...)` 로 쓸 수 있다.
    """
    # TODO: 문제 5-4
    Ts = np.asarray(Ts, dtype=float)
    N = len(Ts)

    # 1) N개의 회전(R)과 이동(t)을 한번에 꺼내기
    Rs = Ts[:, :3, :3] # (N,3,3) 회전들
    ts = Ts[:, :3, 3]  # (N,3)   이동들

    # 2) N개의 R을 한번에 전치 (R.T를 N번 하는 것과 같다)
    Rt = np.swapaxes(Rs, 1, 2) # (N,3,3) 전치들
    # 3) N개의 -R^T @ t를 한번에 계산 (for문 없는 배치 행렬-벡터 곱)
    #    "nij,nj->ni" = n번째 행렬(ij) × n번째 벡터(j) → n번째 결과(i)
    #     = "각 n에 대해 행렬(ij) @ 벡터(j) = 결과(i)"
    #     = for문 없는 배치 행렬곱
    new_t = np.einsum("nij,nj->ni", Rt, -ts)  # (N,3)   -R^T @ t

    # 4) 결과 4×4 행렬 N개 조립 (np.eye(4)로 마지막 행 [0,0,0,1] 확보)
    result = np.broadcast_to(np.eye(4), (N, 4, 4)).copy()
    result[:, :3, :3] = Rt                    # 회전부 넣기
    result[:, :3, 3] = new_t                  # 병진부 넣기
    
    return result


def to_homogeneous(P, w: float = 1.0) -> np.ndarray:
    """(3,) 또는 (N,3) 좌표에 마지막 성분 w 를 붙인다.

    w = 1 이면 점(위치), w = 0 이면 방향(벡터).
    """
    # TODO: 문제 5-2
    P = np.asarray(P, dtype=float)
    if P.ndim == 1:                        # (3,) → (4,)
        return np.append(P, w)
    else:                                  # (N,3) → (N,4)
        col = np.full((P.shape[0], 1), w)  # w로 채운 열 (N,1)
        return np.hstack([P, col])         # 옆으로 붙이기


def transform_point(T, p) -> np.ndarray:
    """점 변환 (w = 1): 회전과 병진이 모두 적용된다. 반환은 (3,)."""
    # TODO: 문제 5-2
    p_h = to_homogeneous(p, 1.0) # [x, y, z] → [x, y, z, 1]
    result = T @ p_h # 4 x 4 @ 4 = 4
    return result[:3]


def transform_direction(T, v) -> np.ndarray:
    """방향 변환 (w = 0): 회전만 적용되고 병진은 무시된다. 반환은 (3,)."""
    # TODO: 문제 5-2
    v_h = to_homogeneous(v, 0.0) 
    result = T @ v_h 
    return result[:3]


def transform_points(T, P, w: float = 1.0) -> np.ndarray:
    """(N,3) 점군을 **반복문 없이** 한 번에 변환한다. (3,) 입력도 받아야 한다.

    힌트: (T @ P_h.T).T 대신 P_h @ T.T 를 쓰면 전치가 한 번으로 끝나고 메모리 접근도 행 방향이라 캐시에 유리하다."""
    # TODO: 문제 5-2 / 6-2
    P = np.asarray(P, dtype=float)
    squeeze = (P.ndim == 1)          # ← 원래 1차원이었나 기억
    if squeeze:
        P = P.reshape(1, -1)         # (3, ) -> (1, 3)
    
    P_h = to_homogeneous(P, w)       # 1. 동차좌표
    result = P_h @ T.T               # 2. 행렬곱
    result = result[:, :3]           # 3. 아 3열
    
    return result[0] if squeeze else result  # 기억해둔 걸로 판단, True면 result[0], False면 if문 반환


def least_squares_normal_equation(A, b):
    """정규방정식 (A^T A) x = A^T b 를 직접 세워 최소자승해를 구한다.

    - (A^T A) 의 역행렬은 문제 4 에서 만든 `inverse_gauss_jordan` 으로 구한다
      (`np.linalg.lstsq` 는 노트북에서 **비교 대상**으로만 쓴다).
    - 근거: 잔차 r = b - A x 가 최소일 때 r 은 A 의 열공간에 수직이므로 A^T r = 0.

    Returns
    -------
    x : 최소자승해
    residual : b - A x
    """
    # TODO: 문제 5-5
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)

    # 1) A^T A 계산 — (120,12)^T @ (120,12) = (12,12)
    # 120개 방정식을 12개 미지수 기준으로 압축하는 것
    AtA = A.T @ A

    # 2) A^T b 계산 — (120,12)^T @ (120,) = (12,)
    # 관측값 b도 같은 방식으로 압축
    Atb = A.T @ b

    # 3) (A^T A)의 역행렬 — 문제 4에서 만든 가우스-조던 소거 사용
    # np.linalg.inv 쓰면 안 됨 (직접 구현이 과제 요구사항)
    AtA_inv = inverse_gauss_jordan(AtA)

    # 4) 최소자승해: x = (A^T A)^-1 @ A^T b
    # 오차 제곱합이 최소가 되는 x
    x = AtA_inv @ Atb

    # 5) 잔차: r = b - Ax (실제 관측 - 예측)
    # 이 잔차가 A의 열공간에 수직이면 최소자승해가 맞다.
    residual = b - A @ x

    return x, residual


def rmse(residual) -> float:
    """잔차의 RMSE = sqrt(mean(r^2))."""
    # TODO: 문제 5-5
    # RMSE = Root Mean Squared Error (평균 제곱근 오차)
    #
    # 순서: 제곱 → 평균 → 루트
    #   r = [0.1, -0.2, 0.15] 이면
    #   제곱:  [0.01, 0.04, 0.0225]
    #   평균:  0.0242
    #   루트:  0.1556
    #
    # 잔차가 양수/음수 섞여있어도 크기를 하나의 숫자로 요약해준다.
    r = np.asarray(residual, dtype=float)
    return float(np.sqrt(np.mean(r * r)))
