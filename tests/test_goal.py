"""목표 학점 역산 모듈 단위 테스트."""

import pytest
from core.goal import required_gpa


def test_required_gpa_specification_standard_case() -> None:
    """기획서 및 규칙 표준 예시 검증: 기존 3.80/30학점, 이번 18학점, 목표 4.00 -> 필요 평점 약 4.33."""
    # (4.00 * (30 + 18) - 3.80 * 30) / 18 = (192 - 114) / 18 = 78 / 18 = 4.333333333333333
    result = required_gpa(
        prev_gpa=3.80, prev_credits=30, this_credits=18, target=4.00
    )
    assert result.status == "달성 가능"
    assert result.required_gpa is not None
    assert result.required_gpa == pytest.approx(4.333333333333333, rel=1e-5)
    assert "4.33" in result.message


def test_required_gpa_unachievable_case() -> None:
    """필요 평점이 만점(4.5)을 초과하는 경우 '달성 불가' 상태와 안내 메시지를 반환한다."""
    # 기존 2.0 / 30학점, 이번 10학점, 목표 4.0 -> (4.0 * 40 - 2.0 * 30) / 10 = (160 - 60) / 10 = 10.0 > 4.5
    result = required_gpa(prev_gpa=2.0, prev_credits=30, this_credits=10, target=4.0)
    assert result.status == "달성 불가"
    assert result.required_gpa is not None
    assert result.required_gpa == pytest.approx(10.0)
    assert "현재 조건에서 달성 어려움" in result.message


def test_required_gpa_already_achieved_case() -> None:
    """필요 평점이 0.0 이하인 경우 '이미 달성' 상태와 안내 메시지를 반환한다."""
    # 기존 4.0 / 30학점, 이번 10학점, 목표 3.0 -> (3.0 * 40 - 4.0 * 30) / 10 = (120 - 120) / 10 = 0.0
    result = required_gpa(prev_gpa=4.0, prev_credits=30, this_credits=10, target=3.0)
    assert result.status == "이미 달성"
    assert result.required_gpa is not None
    assert result.required_gpa <= 0.0
    assert "이미 목표 학점을 달성 가능" in result.message


def test_required_gpa_zero_this_credits_error() -> None:
    """이번 학기 학점이 0 이하인 경우 오류 상태와 명확한 메시지를 반환한다."""
    result = required_gpa(prev_gpa=3.5, prev_credits=30, this_credits=0, target=4.0)
    assert result.status == "오류"
    assert result.required_gpa is None
    assert "1학점 이상" in result.message


def test_required_gpa_negative_input_error() -> None:
    """음수 입력값이 전달된 경우 오류를 반환한다."""
    result = required_gpa(
        prev_gpa=-1.0, prev_credits=30, this_credits=15, target=4.0
    )
    assert result.status == "오류"
    assert result.required_gpa is None
