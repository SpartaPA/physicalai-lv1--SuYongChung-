"""문제 6 — 좌표 변환 체인 모듈. (학생 작성용 템플릿)

base -> link -> camera 로 이어지는 동차변환 체인을 구성하고,
카메라 기준 좌표를 로봇 base 기준으로 바꾼다.
모듈 4(픽앤플레이스 미니 프로젝트)에서 그대로 import 해 쓰게 되므로,
공개 함수 이름과 반환 형식을 이 템플릿 그대로 유지한다.
"""

from __future__ import annotations

import numpy as np

from .rotation import axis_angle_from_matrix, rot_x, rot_y, rot_z
from .transform import inv_T, make_T, transform_points

__all__ = ["CoordinateChain", "default_chain", "camera_point_to_base", "base_point_to_camera"]


class CoordinateChain:
    """부모 -> 자식 동차변환을 이름으로 등록하고, 임의의 두 프레임 사이 변환을 만든다.

    TF2 의 축소판이라고 보면 된다.

    Examples
    --------
    >>> chain = CoordinateChain("base")
    >>> chain.add("base", "link", T_base_link)
    >>> chain.add("link", "camera", T_link_camera)
    >>> T = chain.T("base", "camera")     # camera 좌표 -> base 좌표
    """

    def __init__(self, root: str = "base"):
        self.root = root
        self._parent: dict[str, str] = {}                 # child -> parent
        self._T: dict[tuple[str, str], np.ndarray] = {}   # (parent, child) -> T

    def add(self, parent: str, child: str, T) -> "CoordinateChain":
        """parent 기준으로 표현된 child 프레임의 자세 T(parent<-child) 를 등록한다.

        체이닝이 되도록 self 를 돌려준다. 4x4 가 아니면 ValueError.
        """
        T = np.asarray(T, dtype=float)
        if T.shape != (4, 4):
            raise ValueError(f"4x4 동차변환이 필요합니다. 받은 shape={T.shape}")
        self._parent[child] = parent
        self._T[(parent, child)] = T
        return self

    def get(self, parent: str, child: str) -> np.ndarray:
        """등록해 둔 T(parent <- child) 를 그대로 돌려준다."""
        return self._T[(parent, child)]

    def frames(self) -> list[str]:
        """등록된 프레임 이름 목록 (root 포함)."""
        return [self.root] + list(self._parent.keys())

    # ------------------------------------------------------ 여기부터 구현

    def _path_to_root(self, frame: str) -> list[str]:
        """frame 에서 root 까지의 경로 [frame, ..., root] 를 만든다.

        root 에 연결되어 있지 않으면 KeyError.
        """
        # TODO: 문제 6-1
        path = [] # 빈 리스트 준비
        current = frame # 시작점

        path.append(current) # 경로에 넣기

        while current != self.root: # root에 도착할 때까지 반복
            current = self._parent[current] # 부모 찾기
            path.append(current) # 경로에 넣기

        return path

    def T_from_root(self, frame: str) -> np.ndarray:
        """root 기준 frame 의 자세 T(root <- frame).

        경로를 따라가며 등록된 변환을 곱한다. 곱하는 **순서**에 주의할 것:
        윗첨자/아랫첨자가 이웃끼리 상쇄되도록 놓으면 틀리지 않는다.
            T(base<-camera) = T(base<-link) @ T(link<-camera)
        """
        # TODO: 문제 6-1
        # 1) frame에서 root까지 경로 구하기
        # 예: "camera" → ["camera", "link", "base"]
        path = self._path_to_root(frame)

        # 2) 뒤집어서 root부터 시작하게 만들기
        #["camera", "link", "base"] → ["base", "link", "camera"]
        path.reverse()

        # 3) 항등행렬로 시작 (아무 변환도 안 한 상태)
        T = np.eye(4)

        # 4) 이웃한 쌍을 꺼내서 등록된 변환을 차례로 곱하기
        # i=0: parent="base",  child="link"   → T = I @ T(base←link)
        # i=1: parent="link",  child="camera" → T = T(base←link) @ T(link←camera)
        for i in range(len(path) - 1):
            parent = path[i] # 왼쪽 (위쪽)
            child  = path[i + 1] # 오른쪽 (아래쪽)
            T = T @ self._T[(parent, child)]  # **핵심**: 등록된 변환을 오른쪽에 곱하기

        # 5) 최종 결과: T(root ← frame)
        # 예: T(base ← camera)
        return T

    def T(self, target: str, source: str) -> np.ndarray:
        """source 좌표를 target 좌표로 바꾸는 변환 T(target <- source).

        힌트: T(target<-source) = inv(T(root<-target)) @ T(root<-source)
        """
        # TODO: 문제 6-1
        # T(target ← source) = inv(T(root ← target)) @ T(root ← source)
        T_root_target = self.T_from_root(target)  # root 기준 target
        T_root_source = self.T_from_root(source)  # root 기준 source
        return inv_T(T_root_target) @ T_root_source

    def transform(self, target: str, source: str, P, w: float = 1.0) -> np.ndarray:
        """source 프레임의 점(w=1) 또는 방향(w=0)을 target 프레임으로 변환한다.

        (3,) 와 (N,3) 을 모두 지원해야 하고, **반복문을 쓰지 않는다**.
        """
        # TODO: 문제 6-2
        T_mat = self.T(target, source)          # 변환 행렬 구하기
        return transform_points(T_mat, P, w)    # 점(군) 변환

    def axis_angle(self, target: str, source: str):
        """T(target <- source) 의 회전 부분에서 회전축과 회전각을 복원한다."""
        # TODO: 문제 6-4
        T_mat = self.T(target, source) # 4×4 변환 행렬
        R = T_mat[:3, :3] # 왼쪽 위 3×3 = 회전 부분
        return axis_angle_from_matrix(R) # 축, 각 반환


def default_chain() -> CoordinateChain:
    """과제에서 쓸 기본 체인(base -> link -> camera)을 만든다.

    지시문은 '임의의 회전·병진'을 쓰라고 하지만, 채점 수치를 맞추기 위해
    아래 값을 그대로 쓰기를 권장한다. (바꾸려면 노트북에도 그 값을 명시할 것)

    base -> link   : z축 30도 회전 후 (0.30, 0.00, 0.40) m 이동
    link -> camera : y축 -20도, x축 90도 회전(y 먼저 곱함) 후 (0.10, 0.05, 0.15) m 이동
    """
    # TODO: 문제 6-1
    #   T_base_link   = make_T(rot_z(...), [...])
    #   T_link_camera = make_T(rot_y(...) @ rot_x(...), [...])
    #   return CoordinateChain("base").add(...).add(...)
    
    # base → link: z축 22.5도 회전, (0.35, 0.05, 0.45) 이동
    T_base_link = make_T(rot_z(np.deg2rad(22.5)), [0.35, 0.05, 0.45])

    # link → camera: y축 -22.5도 먼저, x축 67.5도 나중에 곱함
    #   "y 먼저 곱함" = rot_y @ rot_x (왼쪽이 나중에 적용, 오른쪽이 먼저)
    R_link_cam = rot_y(np.deg2rad(-22.5)) @ rot_x(np.deg2rad(67.5))
    T_link_cam = make_T(R_link_cam, [0.12, 0.04, 0.18])

    return CoordinateChain("base").add("base", "link", T_base_link).add("link", "camera", T_link_cam)


def camera_point_to_base(p_cam, chain: CoordinateChain | None = None) -> np.ndarray:
    """카메라 기준 좌표 -> base 기준 좌표. (3,) 와 (N,3) 모두 지원.

    chain 이 None 이면 default_chain() 을 쓴다.
    """
    # TODO: 문제 6-1
    if chain is None:
        chain = default_chain()
    return chain.transform("base", "camera", p_cam)


def base_point_to_camera(p_base, chain: CoordinateChain | None = None) -> np.ndarray:
    """base 기준 좌표 -> 카메라 기준 좌표. 왕복 검증(문제 6-2)에 쓴다."""
    # TODO: 문제 6-2
    if chain is None:
        chain = default_chain()
    return chain.transform("camera", "base", p_base)
