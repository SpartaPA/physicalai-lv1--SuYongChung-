"""문제 3 — 쿼터니언 변환과 SLERP. (학생 작성용 템플릿)

규약
----
- 쿼터니언은 길이 4 배열 **(x, y, z, w)** 다. 모듈 ③ 의 `quaternion_from_axis_angle` 과
  SciPy `Rotation.as_quat()` 와 같은 순서다. w 가 스칼라(실수부)다.
- q 와 -q 는 같은 회전이다 (이중 덮개). 비교할 때는 부호를 무시하거나 |q . q_ref| 를 본다.
- 보간은 항상 **짧은 호**를 택한다: q0 . q1 < 0 이면 q1 의 부호를 뒤집고 시작한다.

SciPy 는 검산(비교) 용도로만 쓴다. 이 파일 안에서는 numpy 만 사용한다.
"""

from __future__ import annotations

import numpy as np

__all__ = ["matrix_to_quaternion", "quaternion_to_matrix", "slerp", "lerp_quat", "quat_angle"]


def matrix_to_quaternion(R) -> np.ndarray:
    """회전행렬 (3,3) -> 단위 쿼터니언 (x, y, z, w).

    권장 방법 (Shepperd): trace 가 양수이면 w 부터, 아니면 대각성분이 가장 큰 축부터 계산해
    0 으로 나누는 일을 피한다. 180도 회전(trace = -1)에서도 동작해야 한다.

        t = trace(R)
        t > 0        : s = 2 sqrt(1 + t);      w = s/4; x = (R21 - R12)/s; ...
        R00 이 최대  : s = 2 sqrt(1 + R00 - R11 - R22);  x = s/4; w = (R21 - R12)/s; ...
        (R11, R22 최대인 경우도 같은 꼴)

    반환값은 반드시 정규화하고, w >= 0 이 되도록 부호를 맞춘다 (비교가 편해진다).
    """
    # TODO: 문제 3-1
    R = np.asarray(R, dtype=float)
    tr = np.trace(R) # R00 + R11 + R22 
    # trace > 0 -> w가 가장 큼 -> w부터 계산 / R00이 최대 -> x가 가장 큼 -> x부터 계산 / R11이 최대 -> y가 가장 큼 -> y부터 계산 / R22이 최대 -> z가 가장 큼 -> z부터 계산
    if tr > 0:
        s = 2.0 * np.sqrt(1.0 + tr) # s = 4w
        w = s / 4.0
        x = (R[2, 1] - R[1, 2]) / s
        y = (R[0, 2] - R[2, 0]) / s
        z = (R[1, 0] - R[0, 1]) / s
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = 2.0*np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) # s  = 4x
        x = s / 4.0
        w = (R[2, 1] - R[1, 2]) / s
        y = (R[0, 1] + R[1, 0]) / s
        z = (R[0, 2] + R[2, 0]) / s
    elif R[1, 1] > R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) # s = 4y
        y = s /4.0
        w = (R[0, 2] - R[2, 0]) / s
        x = (R[0, 1] + R[1, 0]) / s
        z = (R[1, 2] + R[2, 1]) / s
    else:
        s = 2.0 * np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1])  # s = 4z
        z = s / 4.0
        w = (R[1, 0] - R[0, 1]) / s
        x = (R[0, 2] + R[2, 0]) / s
        y = (R[1, 2] + R[2, 1]) / s

    q = np.array([x, y, z, w])
    q = q / np.linalg.norm(q) # 정규화
    if q[3] < 0:
        q = -q
    return q


def quaternion_to_matrix(q) -> np.ndarray:
    """단위 쿼터니언 (x, y, z, w) -> 회전행렬 (3,3).

        R = [[1 - 2(y^2 + z^2),   2(xy - zw),        2(xz + yw)],
             [2(xy + zw),         1 - 2(x^2 + z^2),  2(yz - xw)],
             [2(xz - yw),         2(yz + xw),        1 - 2(x^2 + y^2)]]

    입력이 정확히 단위가 아닐 수 있으므로 먼저 정규화한다. q 와 -q 는 같은 R 을 준다.
    """
    # TODO: 문제 3-1
    q = np.asarray(q, dtype=float)
    q = q / np.linalg.norm(q) # 정규화
    x, y, z, w = q

    R = np.array([
        [1 - 2*(y*y + z*z),   2*(x*y - z*w),       2*(x*z + y*w)],
        [2*(x*y + z*w),       1 - 2*(x*x + z*z),   2*(y*z - x*w)],
        [2*(x*z - y*w),       2*(y*z + x*w),       1 - 2*(x*x + y*y)],
    ])
    return R


def quat_angle(q0, q1) -> float:
    """두 단위 쿼터니언이 나타내는 회전 사이의 각도 [rad], 0 <= angle <= pi.

        angle = 2 * arccos(|q0 . q1|)
    """
    # TODO: 문제 3-2 (slerp 안에서 재사용)
    q0 = np.asarray(q0, dtype=float)
    q1 = np.asarray(q1, dtype=float)

    # 내적: q0·q1 = cos(Ω), 여기서 Ω = θ/2 (θ가 실제 회전각)
    # abs를 씌우는 이유: q와 -q는 같은 회전이니까 부호 무시
    # clip(0, 1): 부동소수점 오차로 1.0000000001 같은 값이 나오면 arccos가 NaN 뱉으니까 방지
    d = np.clip(np.abs(np.dot(q0, q1)), 0.0, 1.0)

    # 실제 회전각 θ = 2Ω = 2·arccos(|q0·q1|)
    return 2.0 * np.arccos(d)


def slerp(q0, q1, t: float, eps: float = 1e-8) -> np.ndarray:
    """구면 선형 보간 (Spherical Linear intERPolation).

        d = q0 . q1                      (d < 0 이면 q1 = -q1, d = -d 로 짧은 호 선택)
        omega = arccos(d)
        q(t) = [sin((1-t) omega) q0 + sin(t omega) q1] / sin(omega)

    경계 상황
    - 두 자세가 거의 같아 d > 1 - eps 이면 sin(omega) ~ 0 이라 나눗셈이 불안정하다.
      이때는 선형 보간 후 정규화로 대체한다.
    - d 는 부동소수점 오차로 1 을 살짝 넘을 수 있으므로 clip 한다.

    반환값은 단위 쿼터니언이어야 한다. t = 0 이면 q0, t = 1 이면 (부호를 맞춘) q1.
    """
    # TODO: 문제 3-2 · 3-5
    q0 = np.asarray(q0, dtype=float)
    q1 = np.asarray(q1, dtype=float)

    # 내적 d = cos(Ω) — 두 쿼터니언이 얼마나 가까운지
    # d=1이면 같은 자세, d=0이면 90도, d=-1이면 같은 자세인데 부호만 반대'
    d = np.dot(q0, q1)

    # --- 짧은 호 선택 ---
    # d < 0이면 q1과 -q1 중 -q1이 q0에 더 가까운 쪽
    if d < 0.0:
        q1 = -q1 # q1 부호 뒤집기(같은 회전이지만 가까운 쪽)
        d = -d # 내적도 부호 뒤집어서 양수로

    # 부동소수점 오차로 d가 1을 살짝 넘을 수 있으니 np.clip으로 잘라준다.
    d = np.clip(d, 0.0, 1.0)

    # Ω ≈ 0이면 sin(Ω) ≈ 0 → 아래 공식에서 0으로 나누기 발생
    # 이때는 그냥 직선 보간하고 정규화하면 충분하다(각도가 거의 0이므로)
    if d > 1.0 - eps:
        q = (1.0 - t) * q0 + t * q1 # 성분별 직선 보간
        return q / np.linalg.norm(q) # 단위구 위로 올려놓기

    # --- SLERP 본체 ---
    # Ω = arccos(d) — 두 쿼터니언 사이 호의 "반각"
    omega = np.arccos(d)

    # sin(Ω) — 나눗셈용. 위에서 d ≈ 1인 경우를 이미 걸렀으니 여기선 0이 아님
    sin_omega = np.sin(omega)

    # 가중치 계산
    # s0: t=0이면 1, t=1이면 0 → q0의 비중
    # s1: t=0이면 0, t=1이면 1 → q1의 비중
    # sin을 쓰기 때문에 "구 표면을 따라" 일정 속도로 움직임
    s0 = np.sin((1.0 - t) * omega) / sin_omega
    s1 = np.sin(t * omega) / sin_omega

    # 가중합 - 구 표면 위의 보간 결과
    q = s0 * q0 + s1 * q1

    # 부동소수점 오차 대비 정규화(단위 쿼터니언)
    return q / np.linalg.norm(q)



def lerp_quat(q0, q1, t: float, normalize: bool = False) -> np.ndarray:
    """성분별 단순 선형 보간 (비교용).

        q(t) = (1 - t) q0 + t q1          (q0 . q1 < 0 이면 q1 부호를 먼저 뒤집는다)

    normalize=False 이면 정규화하지 않은 값을 그대로 돌려준다 — 크기가 1 에서 얼마나
    벗어나는지 관찰하는 데 쓴다. normalize=True 이면 정규화한다 (NLERP).
    """
    # TODO: 문제 3-4
    q0 = np.asarray(q0, dtype=float)
    q1 = np.asarray(q1, dtype=float)

    # 짧은 호 선택(slerp와 같은 이유)
    if np.dot(q0, q1) < 0.0:
        q1 = -q1

    # 성분별 직선 보간
    q = (1.0 - t) * q0 + t * q1

    if normalize:
        q = q / np.linalg.norm(q)

    return q

