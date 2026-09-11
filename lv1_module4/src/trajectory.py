"""문제 4 — 궤적 보간. (학생 작성용 템플릿)

경유점(waypoint)을 지나는 궤적을 선형 보간 / 큐빅 스플라인으로 만들고,
시작·끝에서 속도와 가속도가 0 이 되는 5차 다항식 프로파일을 구현한다.

입력 규약
--------
- t_wp : (M,) 경유점 시각, 오름차순
- q_wp : (M,) 스칼라 궤적 또는 (M, D) 다차원 궤적 (예: 3차원 위치는 D = 3)
- t    : (N,) 평가할 시각 (t_wp[0] <= t <= t_wp[-1])
- 반환 : q_wp 가 (M,) 이면 (N,), (M, D) 이면 (N, D)

큐빅 스플라인은 `scipy.interpolate.CubicSpline` 을 써도 된다 (axis=0).
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline

__all__ = ["linear_interp", "cubic_spline_interp", "quintic_profile", "finite_diff"]


def linear_interp(t_wp, q_wp, t) -> np.ndarray:
    """경유점 사이를 직선으로 잇는 보간. 각 차원마다 `np.interp` 를 쓰면 된다.

    위치는 이어지지만 경유점에서 속도가 불연속(꺾임)이다.
    """
    # TODO: 문제 4-1
    t_wp = np.asarray(t_wp, dtype=float)
    q_wp = np.asarray(q_wp, dtype=float)
    t = np.asarray(t, dtype=float)

    if q_wp.ndim == 1:
        # 1차원: np.interp 바로 사용
        return np.interp(t, t_wp, q_wp)
    else:
        # 다차원 (M, D): 열마다 독립적으로 보간
        return np.column_stack([
            np.interp(t, t_wp, q_wp[:, k])
            for k in range(q_wp.shape[1])
        ])


def cubic_spline_interp(t_wp, q_wp, t, bc_type: str = "natural") -> np.ndarray:
    """경유점을 지나는 큐빅 스플라인 보간 (위치·속도·가속도가 모두 연속, C2).

    bc_type : 양끝 경계 조건. "natural" (양끝 가속도 0) 또는 "clamped" (양끝 속도 0).
    """
    # TODO: 문제 4-1
    t_wp = np.asarray(t_wp, dtype=float)
    q_wp = np.asarray(q_wp, dtype=float)
    t = np.asarray(t, dtype=float)

    # axis=0: 행(시간축)을 따라 보간 ->1D / 다차원 모두 처리
    cs = CubicSpline(t_wp, q_wp, axis=0, bc_type=bc_type)
    return cs(t)


def quintic_profile(t, t0: float, tf: float, q0, qf,
                    v0=0.0, vf=0.0, a0=0.0, af=0.0):
    """5차 다항식 궤적 q(t) 와 그 도함수 (q, qd, qdd) 를 돌려준다.

    경계 조건 6개 — q(t0)=q0, q(tf)=qf, qd(t0)=v0, qd(tf)=vf, qdd(t0)=a0, qdd(tf)=af —
    로 계수 6개 (c0 ~ c5) 를 정한다. 경계 속도·가속도가 모두 0 인 기본형은

        tau = (t - t0) / (tf - t0)
        s(tau) = 10 tau^3 - 15 tau^4 + 6 tau^5
        q(t) = q0 + (qf - q0) s(tau)

    로 닫힌 꼴이 있고, 일반형은 6x6 선형계를 풀면 된다. 어느 쪽으로 구현해도 된다.
    q0, qf 가 스칼라이면 (N,), (D,) 이면 (N, D) 를 돌려준다.

    Returns
    -------
    q, qd, qdd : 위치, 속도, 가속도 (해석적 미분. 유한차분이 아니다)
    """
    # TODO: 문제 4-4
    t   = np.asarray(t,  dtype=float)
    q0  = np.asarray(q0, dtype=float)
    qf  = np.asarray(qf, dtype=float)

    T   = tf - t0                          # 총 시간
    tau = np.clip((t - t0) / T, 0.0, 1.0) # 정규화된 시간 [0, 1]

    # 5차 다항식 s(τ)와 도함수
    s   =  10*tau**3 - 15*tau**4 +  6*tau**5
    sd  =  30*tau**2 - 60*tau**3 + 30*tau**4   # ds/dτ
    sdd =  60*tau    -180*tau**2 +120*tau**3   # d²s/dτ²

    dq = qf - q0  # 이동량

    # 다차원 대응: tau (N,) × dq (D,) → (N, D)
    if dq.ndim == 0:
        # 스칼라
        q   = q0 + dq * s
        qd  = dq * sd  / T
        qdd = dq * sdd / T**2
    else:
        # 벡터 (D,): s를 (N,1)로 브로드캐스팅
        q   = q0 + dq * s[:, None]
        qd  = dq * sd[:, None]  / T
        qdd = dq * sdd[:, None] / T**2

    return q, qd, qdd


def finite_diff(y, t) -> np.ndarray:
    """시간축(axis 0)에 대한 수치 미분. `np.gradient(y, t, axis=0)` 를 쓰면 된다.

    y : (N,) 또는 (N, D),  t : (N,)
    속도 = finite_diff(q, t),  가속도 = finite_diff(속도, t)
    """
    # TODO: 문제 4-2
    return np.gradient(np.asarray(y, dtype=float),
                       np.asarray(t, dtype=float),
                       axis=0) # np.gradient가 시간축(axis=0)을 따라 수치 미분해준다.
