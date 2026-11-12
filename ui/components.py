"""Streamlit 화면 표시용 뷰 컴포넌트 모듈."""

import pandas as pd
import streamlit as st
from core.grade import (
    calculate_cumulative_gpa,
    calculate_semester_gpa,
    format_gpa,
)
from core.models import GRADE_POINTS, Course


def render_grade_summary_metrics(
    semester_courses: list[Course],
    all_courses: list[Course],
) -> None:
    """학기 평균 평점 및 전체 누적 평점 지표 카드를 렌더링한다."""
    sem_gpa, sem_credits = calculate_semester_gpa(semester_courses)
    cum_gpa, total_credits = calculate_cumulative_gpa(all_courses)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="선택 학기 취득 학점", value=f"{sem_credits} 학점")
    with col2:
        st.metric(label="선택 학기 평균 평점", value=f"{format_gpa(sem_gpa)} / 4.5")
    with col3:
        st.metric(label="전체 총 이수 학점", value=f"{total_credits} 학점")
    with col4:
        st.metric(label="전체 누적 평점", value=f"{format_gpa(cum_gpa)} / 4.5")


def create_course_dataframe(courses: list[Course]) -> pd.DataFrame:
    """과목 목록을 제안서 표 형식에 맞춘 Pandas DataFrame으로 변환한다."""
    data = []
    for c in courses:
        grade = c.grade.upper()
        pt = GRADE_POINTS.get(grade, 0.0) if grade not in {"P", "NP", "S", "U"} else 0.0
        weighted_score = pt * c.credits
        data.append(
            {
                "과목 ID": c.id,
                "과목명": c.name,
                "이수 학점": c.credits,
                "성적 등급": c.grade,
                "평점": f"{pt:.1f}" if grade not in {"P", "NP"} else "P/F",
                "가중 점수": f"{weighted_score:.1f}" if grade not in {"P", "NP"} else "-",
            }
        )
    return pd.DataFrame(data)
