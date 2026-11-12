"""성적 시뮬레이션 및 시나리오 비교 단위 테스트."""

import pytest
from core.models import Course
from core.simulation import compare_scenarios, simulate_semester


def test_simulate_semester_override() -> None:
    """과목별 성적 변경 시뮬레이션 계산을 검증한다."""
    courses = [
        Course(name="알고리즘", credits=3, grade="B0"),
        Course(name="운영체제", credits=3, grade="B0"),
    ]
    # 원래 (3.0*3 + 3.0*3) / 6 = 3.0
    gpa_orig, _ = simulate_semester(courses, {})
    assert gpa_orig == pytest.approx(3.0)

    # 알고리즘을 A+로 상향 -> (4.5*3 + 3.0*3) / 6 = 22.5 / 6 = 3.75
    gpa_sim, credits_sum = simulate_semester(courses, {"알고리즘": "A+"})
    assert credits_sum == 6
    assert gpa_sim == pytest.approx(3.75)


def test_compare_scenarios() -> None:
    """여러 시나리오(낙관적, 보수적)를 비교하여 목표 달성 여부를 검증한다."""
    courses = [
        Course(name="컴퓨터구조", credits=3, grade="B+"),
        Course(name="자료구조", credits=3, grade="B+"),
    ]
    scenarios = {
        "최상": {"컴퓨터구조": "A+", "자료구조": "A+"},  # 학기 4.5
        "유지": {"컴퓨터구조": "B+", "자료구조": "B+"},  # 학기 3.5
    }
    # 기존 3.0 / 30학점, 이번 6학점, 목표 3.20
    # 최상: (3.0*30 + 4.5*6) / 36 = (90 + 27) / 36 = 117 / 36 = 3.25 >= 3.20 (달성)
    # 유지: (3.0*30 + 3.5*6) / 36 = (90 + 21) / 36 = 111 / 36 = 3.0833 < 3.20 (미달성)
    results = compare_scenarios(
        courses=courses,
        scenarios=scenarios,
        prev_gpa=3.0,
        prev_credits=30,
        target=3.20,
    )

    assert results["최상"].is_achieved is True
    assert results["최상"].cumulative_gpa == pytest.approx(3.25)
    assert results["유지"].is_achieved is False
    assert results["유지"].cumulative_gpa == pytest.approx(3.0833333, rel=1e-4)
