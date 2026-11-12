"""과목별 성적 변경에 따른 시뮬레이션 및 시나리오 비교 모듈."""

from dataclasses import dataclass
from typing import Any

from core.grade import calculate_combined_gpa, calculate_semester_gpa
from core.models import GRADE_POINTS, Course


@dataclass
class ScenarioResult:
    """시나리오별 시뮬레이션 결과를 담는 데이터 클래스."""

    name: str
    semester_gpa: float
    cumulative_gpa: float
    total_credits: int
    is_achieved: bool
    status: str
    message: str


def simulate_semester(
    courses: list[Course],
    grade_overrides: dict[str, str],
    grade_points: dict[str, float] = GRADE_POINTS,
) -> tuple[float, int]:
    """예상 성적 등급을 변경하여 시뮬레이션된 학기 평균 평점과 학점을 반환한다."""
    simulated_courses: list[Course] = []
    for c in courses:
        new_grade = grade_overrides.get(c.name, c.grade)
        simulated_courses.append(
            Course(
                name=c.name,
                credits=c.credits,
                grade=new_grade,
                semester=c.semester,
                id=c.id,
            )
        )
    return calculate_semester_gpa(simulated_courses, grade_points=grade_points)


def compare_scenarios(
    courses: list[Course],
    scenarios: dict[str, dict[str, str]],
    prev_gpa: float,
    prev_credits: int,
    target: float,
    grade_points: dict[str, float] = GRADE_POINTS,
) -> dict[str, ScenarioResult]:
    """여러 성적 시나리오를 비교하여 목표 달성 여부와 평점 결과를 반환한다."""
    results: dict[str, ScenarioResult] = {}

    for name, overrides in scenarios.items():
        sem_gpa, sem_credits = simulate_semester(
            courses, overrides, grade_points=grade_points
        )
        cum_gpa, total_credits = calculate_combined_gpa(
            prev_gpa, prev_credits, sem_gpa, sem_credits
        )
        is_achieved = cum_gpa >= target
        status = "달성" if is_achieved else "미달성"
        diff = cum_gpa - target
        sign = "+" if diff >= 0 else ""
        message = (
            f"학기 평점 {sem_gpa:.2f}, 누적 평점 {cum_gpa:.2f} (목표 대비 {sign}{diff:.2f})"
        )

        results[name] = ScenarioResult(
            name=name,
            semester_gpa=sem_gpa,
            cumulative_gpa=cum_gpa,
            total_credits=total_credits,
            is_achieved=is_achieved,
            status=status,
            message=message,
        )

    return results
