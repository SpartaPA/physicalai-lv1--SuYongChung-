"""문제 1 — 벡터 연산 모듈. (학생 작성용 템플릿)

내적 · 사이각 · 정규화 · 정사영 · 반대칭행렬(외적) · 평면 법선과
가우스 소거 기반의 rank / 행렬식 / 역행렬을 **직접** 구현한다.

규칙
----
- `np.linalg` 는 노트북에서 **검산용으로만** 쓰고, 이 모듈 안에서는 쓰지 않는다.
  (`inverse_gauss_jordan` 이 던지는 `np.linalg.LinAlgError` 예외 타입만 예외)
- 각 함수의 docstring 에 적힌 계약(입력/출력/예외)을 그대로 지킨다.
  노트북의 검증 셀과 `tests/` 가 이 계약을 기준으로 채점된다.
- 구현을 마치면 `raise NotImplementedError(...)` 줄을 지운다.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "as_vector",
    "dot",
    "norm",
    "angle_between",
    "normalize",
    "project",
    "reject",
    "skew",
    "cross",
    "plane_normal",
    "row_echelon",
    "rank",
    "det",
    "gauss_eliminate",
    "inverse_gauss_jordan",
]


# ---------------------------------------------------------------- 기본 연산

def as_vector(v) -> np.ndarray:
    """입력(리스트/튜플/배열)을 1차원 float 배열로 변환한다.

    1차원이 아니면 ValueError 를 던진다.

    [구현 예시] 아래 세 줄이 이 파일에서 기대하는 코드 스타일이다.
    나머지 함수도 이런 식으로 채워 넣으면 된다.
    """
    arr = np.asarray(v, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"1차원 벡터가 필요합니다. 받은 shape={arr.shape}")
    return arr


def dot(a, b) -> float:
    """내적. sum(a_i * b_i) 를 직접 계산한다 (`np.dot` 사용 금지).

    두 벡터의 차원이 다르면 ValueError.
    """
    # TODO: 문제 1-1
    a, b = as_vector(a), as_vector(b)
    return float(np.sum(a * b))


def norm(v) -> float:
    """유클리드 노름. sqrt(v·v) — 위에서 만든 dot 을 재사용한다."""
    # TODO: 문제 1-1
    v = as_vector(v)
    return float(np.sqrt(dot(v,v)))


def angle_between(a, b, degrees: bool = True) -> float:
    """두 벡터 사이각. degrees=True 면 도(°), False 면 라디안.

    cos(theta) = (a·b) / (|a||b|)

    주의 1. 영벡터가 들어오면 사이각이 정의되지 않는다 -> ValueError.
    주의 2. 부동소수점 오차로 |cos| 가 1 을 아주 조금 넘으면 arccos 가 nan 을 낸다.
            [-1, 1] 로 clip 해야 무작위 입력에서도 안전하다.
    """
    # TODO: 문제 1-1
    a, b = as_vector(a), as_vector(b)
    na, nb = norm(a), norm(b)
    if na == 0.0 or nb == 0.0:
        raise ValueError("영벡터가 들어오면 사이각이 정의되지 않습니다.")
    cos_theta = np.clip(dot(a, b) / (na * nb), -1.0, 1.0)
    theta = np.arccos(cos_theta)
    return float(np.degrees(theta) if degrees else float(theta))


def normalize(v, eps: float = 1e-12) -> np.ndarray:
    """단위벡터로 정규화한다. v / |v|

    영벡터를 어떻게 처리할지는 **문제 1-2 에서 직접 정한다.**
    노트북 1-2 에서 (1) 아무 처리 없이 나눴을 때 무슨 일이 나는지 관찰하고,
    (2) 선택한 처리 방식과 근거를 마크다운에 적은 뒤, 그 방식대로 여기에 구현한다.
    선택에 따라 노트북/테스트의 검증 코드도 그 방식에 맞춰 작성한다.
    """
    # TODO: 문제 1-2
    v = as_vector(v)
    n = norm(v)
    if n == 0:
        raise ValueError("영벡터는 정규화 할 수 없습니다.")
    return v / n


def project(a, b) -> np.ndarray:
    """a 를 b 방향으로 정사영한 성분.

        proj_b(a) = (a·b / b·b) * b

    분모가 |b|^2 이므로 b 를 미리 정규화할 필요는 없다.
    b 가 영벡터면 ValueError.
    """
    # TODO: 문제 1-3
    a, b = as_vector(a), as_vector(b)
    denom = dot(b, b)
    if denom == 0:
        raise ValueError("영벡터 방향으로는 정사영할 수 없습니다.")
    return (dot(a, b) / denom) * b


def reject(a, b) -> np.ndarray:
    """a 에서 b 방향 성분을 뺀 나머지(수직 성분). a = project + reject 가 성립해야 한다."""
    # TODO: 문제 1-3
    a = as_vector(a)
    return a - project(a, b)


def skew(a) -> np.ndarray:
    """3차원 벡터 a 에 대응하는 반대칭행렬 [a]_x 를 만든다.

        [a]_x = [[  0, -a3,  a2],
                 [ a3,   0, -a1],
                 [-a2,  a1,   0]]

    만족해야 하는 성질: [a]_x @ b == a x b,  [a]_x.T == -[a]_x
    3차원이 아니면 ValueError.
    """
    # TODO: 문제 1-4
    a1, a2, a3 = as_vector(a)
    return np.array([
        [0, -a3, a2],
        [a3, 0, -a1],
        [-a2, a1, 0],
        ])


def cross(a, b) -> np.ndarray:
    """외적을 **반대칭행렬 곱으로** 계산한다 (`np.cross` 사용 금지)."""
    # TODO: 문제 1-4
    a, b = as_vector(a), as_vector(b)
    return skew(a) @ b


def plane_normal(P1, P2, P3) -> np.ndarray:
    """세 점이 이루는 평면의 **단위** 법선 벡터.

    두 모서리 벡터(P2-P1, P3-P1)의 외적이 평면에 수직이다.
    세 점이 일직선이면 외적이 영벡터가 되어 평면이 하나로 정해지지 않는다 -> ValueError.
    """
    # TODO: 문제 1-5
    P1, P2, P3 = as_vector(P1), as_vector(P2), as_vector(P3)
    n = cross(P2 - P1, P3 - P1)
    if norm(n) == 0:
        raise ValueError("세 점이 일직선 위에 있어 평면을 정의할 수 없습니다.")
    return normalize(n)
    


# ------------------------------------------------- 가우스 소거 기반 선형대수

def row_echelon(M, pivoting: bool = True, tol = 1e-10):
    """행 사다리꼴(row echelon form) 로 만든다.

    Parameters
    ----------
    pivoting : True 면 부분 피벗팅(각 열에서 절댓값이 가장 큰 행을 피벗으로 올림)

    Returns
    -------
    U : (m, n) 상삼각 형태 행렬
    pivot_cols : 피벗이 선 열 인덱스 리스트
    n_swaps : 행 교환 횟수 (행렬식 부호 계산에 필요)

    힌트: 0 인지 판정할 때는 `== 0` 대신 허용오차(tol)를 쓴다.
          예) tol = max(m, n) * np.finfo(float).eps * max(1.0, np.max(np.abs(U)))
    """
    # TODO: 문제 1-6 / 문제 4
    A = np.array(M, dtype = float)
    n_rows, n_cols = A.shape
    pivot_cols = []
    pivot_row = 0
    n_swaps = 0

    for col in range(n_cols):
        if pivot_row >= n_rows:
            break
        if pivoting:
            max_row = pivot_row + int(np.argmax(np.abs(A[pivot_row:, col]))) 
            # A[pivot_row:, col]: 현재 열에서 pivot_row 아래쪽 값들만 꺼낸다.
            # A는 배열, 배열을 슬라이싱 할 때 A[:]형태 A[pivot_row:, col]은 A[0, col]의 뜻과 동일
            # np.argmax(): 가장 큰 값이 몇 번째 있나?
        else:
            max_row = pivot_row
        if abs(A[max_row,col]) < tol: # 열에서 가장 큰 값이 0에 가까울 때 건너뛰어라
            continue
        if max_row != pivot_row: # max_row를 위로 올리기
            A[[pivot_row, max_row]] = A[[max_row, pivot_row]]
            n_swaps += 1
        A[pivot_row] = A[pivot_row] / A[pivot_row, col] # 피벗 값으로 그 행 전체를 나눠서 피벗 자리를 1로 만들기 -> 소거를 용이하게 하기 위함
        for r in range(n_rows): 
            if r != pivot_row: # 피벗 행 자지 자신은 건너뛴다. 자기 자신을 자기로 빼면 전부 0이 된다.
                A[r] -= A[r, col] * A[pivot_row] # 소거 연산
        pivot_cols.append(col) # 이 열에서 피벗을 찾았다는 뜻
        pivot_row += 1

    return A, pivot_cols, n_swaps
        

def rank(A, tol=1e-10):
    """행 사다리꼴의 피벗 개수 = rank."""
    """rank = 피벗 개수"""
    # TODO: 문제 1-6
    _, pivot_cols, _ = row_echelon(A, tol=tol) # row_echelon의 결과 세 개를 받는다. 단 '_' 표시는 **이 값은 안 쓴다는 뜻**
    return len(pivot_cols)

def det(M, tol=1e-10):
    """행렬식 = 소거 중 대각성분 곱 × (-1)^행교환."""
    A = np.array(M, dtype=float)
    n_rows, n_cols = A.shape
    if n_rows != n_cols:
        raise ValueError("정사각행렬이 아닙니다.")

    sign = 1.0
    for col in range(n_rows): # 위의 row_echelonㅘ 같다. 열을 왼쪽 부터 처리
        max_row = col + int(np.argmax(np.abs(A[col:, col]))) # row_echelon에서 했던 것과 같다. pivot_row 대신 col을 쓰는 이유는 정사각행렬이라 열 번호 = 행번호이기 때문
        if abs(A[max_row, col]) < tol:
            return 0.0 # row_echelon에서는 continue를 썼으나 여기서는 피벗이 하나라도 없으면 = 특이행렬 = 행렬식은 0
        if max_row != col:
            A[[col, max_row]] = A[[max_row, col]]
            sign *= -1.0 # n_swaps += 1 대신 sign *= -1.0으로 부호를 추적
        for r in range(col +1, n_rows): # 아래쪽 행만 소거. row_echelon에서는 위아래 전부 소거했는데 det는 아래만 소거해도 충분
            factor = A[r, col] / A[col, col] # row_echelon은 피벗을 먼저 1로 만들었지만 대신 몇 배 빼야 하나 직접 계산함. **행 전체를 나누면 대각값이 바뀌어서 나중에 곱할 때 틀려짐**
            A[r] -= factor * A[col]
    return float(sign * np.prod(np.diag(A))) # np.diag(A): 대각선 값만 꺼낸다, np.prod(...): 전부 곱한다.


def gauss_eliminate(A, b, pivoting: bool = True, verbose: bool = False):
    """가우스 소거법 + 후진대입으로 Ax = b 를 푼다.

    Parameters
    ----------
    pivoting : True 면 부분 피벗팅을 적용한다. False 면 피벗을 그대로 쓴다
               (문제 4-4 에서 두 경우의 오차를 비교하므로 **둘 다 동작해야 한다**).
    verbose  : True 면 각 소거 단계의 첨가행렬 [A|b] 를 출력한다
               (문제 4-1 이 요구하는 '단계별 출력').

    Returns
    -------
    x : 해 벡터
    steps : 단계별 첨가행렬 [A|b] 스냅샷 리스트 (초기 상태 포함)

    피벗이 0 이면 해가 유일하지 않다 -> ZeroDivisionError.
    """
    # TODO: 문제 4-1
    A = np.array(A, dtype=float) # 원본 안 건드리기 위해 복사
    b = np.array(b, dtype=float)
    n = A.shape[0] # 행 개수 (= 변수 개수)

    # 첨가행렬 [A | b] 만들기
    Aug = np.hstack([A, b.reshape(-1, 1)]) # np.hstack으로 두 배열을 옆으로 붙일 수 있다. b는 1차원이므로 열벡터로 바꿔야 붙일 수 있다 -> b.reshape(-1, 1)을 사용해서 세로로 세운다. 
    steps = [Aug.copy()]                   # 여기서 -1은 "알아서 계산해"라는 뜻이다.

    if verbose: # verbose = True면 각 단계를 출력하라는 뜻
        print("초기 첨가행렬: ")
        print(Aug, "\n")

    # 전방 소거: 아래쪽만 0으로 만들기
    for col in range(n): 
        if pivoting: # 1) 부분 피벗팅: 이 열에서 가장 큰 놈을 위로 올리기
            max_row = col + int(np.argmax(np.abs(Aug[col:, col]))) # Aug[행, 열]에서 col: 은 "col번 행부터 끝까지"라는 뜻 → Aug[col:, col]은 현재 열의 아래쪽 값만 꺼냄
            if max_row != col:
                Aug[[col, max_row]] = Aug[[max_row, col]]
                if verbose:
                    print(f"행 교환: {col}행 ↔ {max_row}행 교환")
                    print(Aug, "\n")

        # 2) 피벗이 0이면 못 푼다.
        if abs(Aug[col, col]) < 1e-12: 
            raise ZeroDivisionError(f"피벗이 0 (열 {col})")

        # 3) 아래쪽 행만 소거 <- row_echelon과의 차이
        for r in range(col + 1, n):
            factor = Aug[r, col] / Aug[col, col] # Aug[r, col]은 없앨 행의 값. Aug[col, col]을 피벗 값(기준) **행 전체를 나누면 대각값이 바뀌어서 나중에 곱할 때 틀려짐**
            Aug[r] -= factor * Aug[col]

        steps.append(Aug.copy()) # steps 리스트 끝에 하나 추가
        if verbose:
            print(f"열 {col} 소거 완료:")
            print(Aug, "\n")

    # ) 후진대입: 맨 아래부터 거꾸로 올라간다.
    x = np.zeros(n)
    for i in range(n-1, -1, -1): # i = n-1, n-2, ...... , 0
        # Aug[i, n] = 우변(b쪽)
        # Aug[i, i] = 대각선(이 변수의 개수)
        # Aug[i, i+1:n] * x[i+1:n] = 이미 구한 변수들의 기여분
        x[i] = (Aug[i, n] - np.sum(Aug[i, i+1:n] * x[i+1:n])) / Aug[i, i] # x[i] = (우변 - 이미 아는 것들의 합) / 대각선 값

    return x, steps


def inverse_gauss_jordan(A) -> np.ndarray:
    """가우스-조던 소거로 역행렬을 구한다. [A|I] -> [I|A^-1].

    정사각이 아니면 ValueError, 특이행렬이면 np.linalg.LinAlgError.
    (`np.linalg.inv` 를 부르지 말고 소거로 직접 구한다)
    """
    # TODO: 문제 4-3
    A = np.array(A, dtype=float)
    n = A.shape[0] # 행 수 

    if A.shape[0] != A.shape[1]:
        raise ValueError("정사각행렬이 아닙니다.")

    Aug = np.hstack([A, np.eye(n)])
    U, pivot_cols, _ = row_echelon(Aug)

    if len(pivot_cols) < n:
        raise np.linalg.LinAlgError("특이행렬이라 역행렬이 없습니다.")

    return U[:, n:] # 모든 행의 n번 열부터 끝까지
