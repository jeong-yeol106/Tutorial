"""목표 학점 달성을 위한 필요 학점 역산 모듈."""

from core.models import DEFAULT_MAX_GPA, GoalResult


def required_gpa(
    prev_gpa: float,
    prev_credits: int,
    this_credits: int,
    target: float,
    max_gpa: float = DEFAULT_MAX_GPA,
) -> GoalResult:
    """목표 누적 평점 달성에 필요한 이번 학기 평균 평점을 역산한다."""
    if this_credits <= 0:
        return GoalResult(
            required_gpa=None,
            status="오류",
            message="이번 학기 예정 학점은 1학점 이상이어야 합니다.",
        )

    if prev_credits < 0 or prev_gpa < 0.0 or target < 0.0:
        return GoalResult(
            required_gpa=None,
            status="오류",
            message="학점과 평점은 0 이상이어야 합니다.",
        )

    total_credits = prev_credits + this_credits
    needed = ((target * total_credits) - (prev_gpa * prev_credits)) / this_credits

    if needed > max_gpa:
        return GoalResult(
            required_gpa=needed,
            status="달성 불가",
            message=f"필요 평점 {needed:.2f}점으로 만점({max_gpa:.1f})을 초과하여 현재 조건에서 달성 어려움",
        )

    if needed <= 0.0:
        return GoalResult(
            required_gpa=needed,
            status="이미 달성",
            message="이번 학기에 성적을 취득하지 않아도 이미 목표 학점을 달성 가능합니다.",
        )

    return GoalResult(
        required_gpa=needed,
        status="달성 가능",
        message=f"이번 학기에 평균 {needed:.2f}점 이상을 취득해야 목표에 도달합니다.",
    )
