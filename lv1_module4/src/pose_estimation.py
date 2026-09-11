"""문제 5 — 점군 자세 추정: PCA · Kabsch · 최소제곱 평면 피팅. (학생 작성용 템플릿)

- `pca_axes`        : 공분산 고유분해로 물체의 주축 3개를 뽑는다
- `kabsch`          : 대응이 알려진 두 점군 사이의 최적 회전·병진을 SVD 로 구한다
- `fit_plane_lstsq` : 최소제곱으로 평면을 피팅하고 점별 잔차를 돌려준다
- `remove_outliers` : 잔차가 큰 점을 걸러낸다

`rotation_angle_deg` 는 제공 코드다 (두 회전행렬 사이 각도).
"""

from __future__ import annotations

import numpy as np

__all__ = ["pca_axes", "kabsch", "fit_plane_lstsq", "remove_outliers", "rotation_angle_deg"]


def rotation_angle_deg(R_a, R_b) -> float:
    """두 회전행렬 사이의 각도 [deg] — R_a^T R_b 의 회전각. (제공 코드)"""
    R_rel = np.asarray(R_a, dtype=float).T @ np.asarray(R_b, dtype=float)
    cos_theta = np.clip((np.trace(R_rel) - 1.0) / 2.0, -1.0, 1.0)
    return float(np.rad2deg(np.arccos(cos_theta)))


def pca_axes(P):
    """점군 (N,3) 의 주축을 고유분해로 뽑는다.

    1. centroid = P 의 평균, X = P - centroid
    2. C = X^T X / (N - 1)   (3x3 공분산)
    3. C 를 고유분해 (`np.linalg.eigh` — 대칭행렬 전용, 실수 고유값)
    4. 고유값 **내림차순**으로 정렬해 axes 의 열 0,1,2 가 각각 긴 축 -> 짧은 축이 되게 한다
    5. det(axes) = +1 이 되도록 (오른손 좌표계) 필요하면 마지막 열의 부호를 뒤집는다

    Returns
    -------
    axes : (3,3) 열이 주축 (단위벡터, 서로 직교, det = +1) — 회전행렬로 그대로 쓸 수 있다
    eigvals : (3,) 내림차순 고유값 (각 축 방향 분산)
    centroid : (3,) 점군 중심
    """
    # TODO: 문제 5-1
    P = np.asarray(P, dtype=float)
    centroid = P.mean(axis=0)
    X = P - centroid
    C = X.T @ X / (len(P) - 1)

    vals, vecs = np.linalg.eigh(C)
    # eigh -> 오른차순이므로 뒤집어서 내림차순
    idx = np.argsort(vals)[::-1]
    eigvals = vals[idx]
    axes = vecs[:, idx]

    # 오른손 좌표계 보장
    if np.linalg.det(axes) < 0:
        axes[:, -1] *= -1

    return axes, eigvals, centroid


def kabsch(P, Q):
    """대응이 알려진 두 점군 P, Q (N,3) 에 대해 Q ~ P @ R.T + t 를 만족하는 (R, t) 를 구한다.

    1. 두 점군의 중심 cP, cQ 를 빼서 X = P - cP, Y = Q - cQ
    2. H = X^T Y  (3x3 교차 공분산)
    3. U, S, Vt = svd(H)
    4. d = sign(det(V U^T)) — 반사가 나오면 (-1) 보정: D = diag(1, 1, d)
    5. R = V D U^T,  t = cQ - R cP

    Returns
    -------
    R : (3,3) 회전행렬 (det = +1)
    t : (3,) 병진
    """
    # TODO: 문제 5-3
    P = np.asarray(P, dtype=float)
    Q = np.asarray(Q, dtype=float) # 관측 점군 (N, 3) - P를 회전 + 병진하면 Q가 된다.

    cP = P.mean(axis=0) # P의 무게중심 (3, )
    cQ = Q.mean(axis=0) # Q의 무게중심 (3, )
    X = P - cP # P에서 중심을 뺀 것 - 원점 기준으로 맞춤
    Y = Q - cQ # Q에서 중심을 뺀 것 - 이제 두 점군 모두 원점 중심

    # "P의 각 방향이 Q의 어느 방향과 얼마나 같이 움직이냐"를 담은 3 x 3 행렬 -> 분해하면 최적 회전이 나온다
    H = X.T @ Y

    # H = U S V^T로 분해
    # U: P쪽 기저, S: 각 방향의 스케일, Vt: Q쪽 기저(주의: V^T가 나옴)
    U, S, Vt = np.linalg.svd(H)
    V = Vt.T # svd가 V^T를 돌려주므로 전치해서 V를 복원

    # V U^T가 순수한 회전인지 반사인지 확인
    # det = +1이면 회전(정상), det = -1이면 반사가 섞인 것
    d = np.sign(np.linalg.det(V @ U.T))

    # d = -1일 때 마지막 열의 부호를 뒤집어서 반사를 회전으로 강제 교정
    # d = +1이면 D = diag(1, 1, 1) = 항등행렬이라 아무 영향 없다.
    D = np.diag([1.0, 1.0, d])

    # 최적 회전행렬 (det = +1 보장)
    R = V @ D @ U.T

    # 두 무게중심이 일치하도록 병진 계산
    # R로 cP를 돌린 위치가 cQ와 같아야 하므로: t = cQ - R @ cP
    t = cQ - R @ cP

    return R, t



def fit_plane_lstsq(P):
    """점군 (N,3) 에 평면 n . p + d = 0 을 최소제곱으로 피팅한다.

    권장 방법 (정규방정식): z = a x + b y + c 로 두고
        A = [x, y, 1],  b = z,   (A^T A) [a, b, c]^T = A^T b
    를 풀면 평면 a x + b y - z + c = 0 이므로 법선 n = (a, b, -1) 을 정규화한다.
    (평면이 z축과 나란하면 이 모델은 못 쓴다 — 그런 경우 SVD 로 최소 분산 방향을 쓴다.)

    Returns
    -------
    normal : (3,) 단위 법선
    d : float — 평면 상수 (n . p + d = 0)
    residuals : (N,) 각 점의 부호 있는 평면까지의 거리 n . p + d
    """
    # TODO: 문제 5-5
    P = np.asarray(P, dtype=float)
    x, y, z = P[:, 0], P[:, 1], P[:, 2]

    # A = [x, y, 1],  b_vec = z
    A = np.column_stack([x, y, np.ones(len(P))])
    b_vec = z

    # 정규방정식: (A^T A) @ params = A^T @ b_vec
    # params = [a, b, c]  →  z = ax + by + c
    ATA = A.T @ A
    ATb = A.T @ b_vec

    # A^T A 를 직접 풀기 (np.linalg.solve 는 검산용이므로 명시)
    # 정규방정식 직접 풀이 (검산: np.linalg.solve)
    params = np.linalg.solve(ATA, ATb)  # 검산용 — 직접 구현 아님을 명시
    a, b, c = params

    # 평면: ax + by - z + c = 0  →  법선 방향 (a, b, -1)
    normal_raw = np.array([a, b, -1.0])
    normal = normal_raw / np.linalg.norm(normal_raw)

    # 평면 상수: n · p + d = 0  →  d = -n · (한 점)
    d = float(-normal @ P.mean(axis=0))

    # 부호 있는 잔차: 각 점의 평면까지의 거리
    residuals = P @ normal + d

    return normal, d, residuals



def remove_outliers(P, residuals, k: float = 3.0):
    """잔차가 큰 점을 제거한다.

    기준: |residual| < k * sigma. sigma 는 이상치에 강한 추정치를 권장한다
        sigma = 1.4826 * median(|residual - median(residual)|)      (MAD)
    (단순 std 를 쓰면 이상치가 sigma 자체를 키워 걸러지지 않을 수 있다.)

    Returns
    -------
    P_clean : (M,3) 남은 점
    mask : (N,) bool — True 가 남긴 점. P 와 대응 점군에 같은 mask 를 적용해야 Kabsch 대응이 유지된다
    """
    # TODO: 문제 5-5
    P = np.asarray(P, dtype=float)
    residuals = np.asarray(residuals, dtype=float)

    # MAD 기반 sigma 추정 (이상치에 강건)
    med = np.median(residuals)
    mad = np.median(np.abs(residuals - med))
    sigma = 1.4826 * mad

    # |잔차| < k * sigma 인 점만 남김
    mask = np.abs(residuals) < k * sigma

    return P[mask], mask
