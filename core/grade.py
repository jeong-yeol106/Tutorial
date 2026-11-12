"""학기별 평균 평점 및 누적 평점 계산 순수 함수 모듈."""

from core.models import GRADE_POINTS, PASS_FAIL_GRADES, Course


def calculate_semester_gpa(
    courses: list[Course],
    grade_points: dict[str, float] = GRADE_POINTS,
) -> tuple[float, int]:
    """과목 목록을 입력받아 학기 평균 평점과 계산 반영 총 학점을 반환한다."""
    total_score: float = 0.0
    total_credits: int = 0

    for course in courses:
        grade = course.grade.upper()
        if grade in PASS_FAIL_GRADES or grade not in grade_points:
            continue
        point = grade_points[grade]
        total_score += point * course.credits
        total_credits += course.credits

    if total_credits == 0:
        return 0.0, 0

    return total_score / total_credits, total_credits


def calculate_cumulative_gpa(
    courses: list[Course],
    grade_points: dict[str, float] = GRADE_POINTS,
) -> tuple[float, int]:
    """전체 과목 목록을 합산하여 전체 누적 평점과 총 학점을 반환한다."""
    return calculate_semester_gpa(courses, grade_points=grade_points)


def calculate_combined_gpa(
    prev_gpa: float,
    prev_credits: int,
    this_gpa: float,
    this_credits: int,
) -> tuple[float, int]:
    """기존 성적과 이번 학기 성적을 가중 합산하여 새로운 누적 평점을 계산한다."""
    total_credits = prev_credits + this_credits
    if total_credits == 0:
        return 0.0, 0

    total_score = (prev_gpa * prev_credits) + (this_gpa * this_credits)
    return total_score / total_credits, total_credits


def format_gpa(gpa: float) -> str:
    """평점을 화면 표시용 소수 둘째 자리 문자열로 변환한다."""
    return f"{gpa:.2f}"
