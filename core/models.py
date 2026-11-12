"""과목 및 목표 학점 계산에 사용되는 데이터 모델과 도메인 상수 정의."""

from dataclasses import dataclass
from typing import Optional

# 4.5 만점 기준 성적 등급별 평점 환산표
GRADE_POINTS: dict[str, float] = {
    "A+": 4.5,
    "A0": 4.0,
    "A": 4.0,
    "B+": 3.5,
    "B0": 3.0,
    "B": 3.0,
    "C+": 2.5,
    "C0": 2.0,
    "C": 2.0,
    "D+": 1.5,
    "D0": 1.0,
    "D": 1.0,
    "F": 0.0,
}

# Pass/Fail 등 평점 계산 제외 등급
PASS_FAIL_GRADES: set[str] = {"P", "NP", "S", "U"}

# 기본 최대 평점
DEFAULT_MAX_GPA: float = 4.5

# 허용 이수 학점 범위 (1~4학점)
ALLOWED_CREDITS: set[int] = {1, 2, 3, 4}


@dataclass
class Course:
    """과목명, 이수 학점, 성적 등급을 관리하는 데이터 클래스."""

    name: str
    credits: int
    grade: str
    semester: str = ""
    id: Optional[int] = None


@dataclass
class GoalResult:
    """목표 학점 역산 및 시뮬레이션 결과를 표현하는 데이터 클래스."""

    required_gpa: Optional[float]
    status: str
    message: str
