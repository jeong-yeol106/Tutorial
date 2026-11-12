"""학기 및 누적 평점 계산 모듈 단위 테스트."""

import pytest
from core.grade import (
    calculate_combined_gpa,
    calculate_cumulative_gpa,
    calculate_semester_gpa,
    format_gpa,
)
from core.models import Course


def test_calculate_semester_gpa_specification_example() -> None:
    """제안서 예시 데이터에 대한 학기 평균 평점 계산 검증 (4.333...)."""
    courses = [
        Course(name="프로그래밍", credits=3, grade="A+"),
        Course(name="미분적분학", credits=3, grade="A"),
        Course(name="대학영어 1", credits=3, grade="A+"),
    ]
    # (3*4.5 + 3*4.0 + 3*4.5) / 9 = (13.5 + 12.0 + 13.5) / 9 = 39.0 / 9 = 4.333333333333333
    gpa, credits_sum = calculate_semester_gpa(courses)
    assert credits_sum == 9
    assert gpa == pytest.approx(4.333333333333333, rel=1e-5)
    assert format_gpa(gpa) == "4.33"


def test_calculate_semester_gpa_with_pass_fail() -> None:
    """P/F 과목은 평점 계산과 이수 학점 분모에서 제외되어야 한다."""
    courses = [
        Course(name="데이터베이스", credits=3, grade="B+"),
        Course(name="사회봉사", credits=1, grade="P"),
    ]
    # B+(3.5) * 3 = 10.5 / 3 = 3.5
    gpa, credits_sum = calculate_semester_gpa(courses)
    assert credits_sum == 3
    assert gpa == pytest.approx(3.5)


def test_calculate_semester_gpa_zero_credits() -> None:
    """과목이 없거나 P 과목만 있어 반영 학점이 0인 경우 0.0과 0을 반환한다."""
    courses = [Course(name="진로탐색", credits=1, grade="P")]
    gpa, credits_sum = calculate_semester_gpa(courses)
    assert gpa == 0.0
    assert credits_sum == 0


def test_calculate_combined_gpa() -> None:
    """기존 누적 성적과 이번 학기 성적의 가중 합산 계산을 검증한다."""
    # 기존 3.0 / 30학점 + 이번 4.0 / 10학점 -> (90 + 40) / 40 = 130 / 40 = 3.25
    cum_gpa, total_credits = calculate_combined_gpa(3.0, 30, 4.0, 10)
    assert total_credits == 40
    assert cum_gpa == pytest.approx(3.25)


def test_calculate_combined_gpa_zero_credits() -> None:
    """총 학점이 0인 경우 0.0과 0을 반환한다."""
    cum_gpa, total_credits = calculate_combined_gpa(0.0, 0, 0.0, 0)
    assert cum_gpa == 0.0
    assert total_credits == 0
