"""GradePlan 웹 애플리케이션 진입점 및 메인 화면 모듈."""

import streamlit as st
from core.goal import required_gpa
from core.grade import (
    calculate_combined_gpa,
    calculate_cumulative_gpa,
    calculate_semester_gpa,
    format_gpa,
)
from core.models import DEFAULT_MAX_GPA, Course
from core.simulation import compare_scenarios, simulate_semester
from db.database import (
    add_course,
    delete_course,
    get_all_semesters,
    get_courses,
    init_db,
    update_course,
)
from db.graph import create_gpa_trend_chart
from ui.components import create_course_dataframe, render_grade_summary_metrics

# 등급 선택 목록 상수
GRADE_OPTIONS = ["A+", "A", "B+", "B", "C+", "C", "D+", "D", "F", "P"]


def setup_page_config() -> None:
    """Streamlit 페이지 레이아웃과 기본 설정을 초기화한다."""
    st.set_page_config(
        page_title="GradePlan - 맞춤형 성적 관리 및 학점 예측",
        page_icon="🎓",
        layout="wide",
    )


def render_header() -> None:
    """상단 헤더 타이틀과 설명을 렌더링한다."""
    st.title("🎓 GradePlan | 대학생 맞춤형 성적 관리 및 학점 예측")
    st.caption("수강 과목 성적 관리부터 목표 학점 역산, 등급 변경 시뮬레이션까지 한눈에 확인하세요.")
    st.divider()


def tab_course_management(all_semesters: list[str]) -> None:
    """과목별 성적 등록, 수정, 삭제 및 조회 탭 화면을 렌더링한다."""
    st.subheader("1. 과목별 성적 등록 및 관리")

    col_sem_select, col_sem_input = st.columns([2, 2])
    with col_sem_select:
        sem_list = all_semesters if all_semesters else ["2026-2"]
        selected_semester = st.selectbox("조회/등록 학기 선택", options=sem_list, key="selected_sem")
    with col_sem_input:
        new_sem_input = st.text_input("새로운 학기 추가 입력 (예: 2026-2)", placeholder="직접 입력 후 과목 등록")

    active_semester = new_sem_input.strip() if new_sem_input.strip() else selected_semester

    # 신규 과목 등록 폼
    with st.expander(f"➕ [{active_semester}] 신규 과목 등록하기", expanded=True):
        with st.form("add_course_form", clear_on_submit=True):
            f_col1, f_col2, f_col3, f_col4 = st.columns([3, 2, 2, 2])
            with f_col1:
                name_input = st.text_input("과목명", placeholder="예: 심화프로그래밍")
            with f_col2:
                credits_input = st.selectbox("이수 학점", options=[1, 2, 3, 4], index=2)
            with f_col3:
                grade_input = st.selectbox("성적 등급", options=GRADE_OPTIONS, index=0)
            with f_col4:
                st.write("")
                st.write("")
                submit_add = st.form_submit_button("과목 등록", use_container_width=True)

            if submit_add:
                new_course = Course(name=name_input, credits=credits_input, grade=grade_input)
                success, msg = add_course(active_semester, new_course)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # 과목 목록 및 학기 요약
    semester_courses = get_courses(active_semester)
    all_courses = get_courses()

    render_grade_summary_metrics(semester_courses, all_courses)
    st.write("")

    if semester_courses:
        st.write(f"### 📋 [{active_semester}] 수강 과목 목록")
        df = create_course_dataframe(semester_courses)
        st.dataframe(df.drop(columns=["과목 ID"]), use_container_width=True, hide_index=True)

        # 과목 수정 및 삭제
        with st.expander("🛠️ 과목 정보 수정 및 삭제"):
            c_select_col, c_act_col = st.columns([2, 3])
            course_map = {f"{c.name} ({c.credits}학점, {c.grade})": c for c in semester_courses}
            with c_select_col:
                selected_label = st.selectbox("대상 과목 선택", options=list(course_map.keys()))
                target_course = course_map[selected_label]

            with c_act_col:
                with st.form("edit_course_form"):
                    e_col1, e_col2, e_col3 = st.columns([2, 1, 1])
                    with e_col1:
                        e_name = st.text_input("과목명", value=target_course.name)
                    with e_col2:
                        e_credits = st.selectbox("학점", options=[1, 2, 3, 4], index=[1, 2, 3, 4].index(target_course.credits))
                    with e_col3:
                        e_grade = st.selectbox("등급", options=GRADE_OPTIONS, index=GRADE_OPTIONS.index(target_course.grade))

                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        submit_edit = st.form_submit_button("수정 저장", use_container_width=True)
                    with btn_col2:
                        submit_del = st.form_submit_button("과목 삭제", type="primary", use_container_width=True)

                    if submit_edit and target_course.id:
                        up_course = Course(name=e_name, credits=e_credits, grade=e_grade)
                        up_success, up_msg = update_course(target_course.id, active_semester, up_course)
                        if up_success:
                            st.success(up_msg)
                            st.rerun()
                        else:
                            st.error(up_msg)

                    if submit_del and target_course.id:
                        if delete_course(target_course.id):
                            st.success(f"과목 '{target_course.name}'이(가) 삭제되었습니다.")
                            st.rerun()
                        else:
                            st.error("삭제에 실패했습니다.")
    else:
        st.info(f"[{active_semester}]에 등록된 과목이 없습니다. 상단 폼에서 과목을 등록해보세요.")


def tab_goal_prediction() -> None:
    """목표 학점 역산 탭 화면을 렌더링한다."""
    st.subheader("2. 목표 학점 역산기")
    st.markdown(
        """
        목표 누적 평점을 달성하기 위해 **이번 학기에 몇 점의 평균 평점을 받아야 하는지** 계산합니다.  
        *(역산 공식: $\\text{필요 평점} = \\frac{\\text{목표} \\times (\\text{기존 학점} + \\text{이번 학점}) - \\text{기존 평점} \\times \\text{기존 학점}}{\\text{이번 학점}}$)*
        """
    )

    all_courses = get_courses()
    cum_gpa, total_credits = calculate_cumulative_gpa(all_courses)

    auto_load = st.button("📥 현재까지 등록된 데이터로 기존 성적 자동 채우기")

    c1, c2 = st.columns(2)
    with c1:
        prev_gpa_val = float(cum_gpa) if auto_load else 3.80
        prev_credits_val = int(total_credits) if auto_load else 30
        prev_gpa_input = st.number_input("기존 누적 평점 (4.5 만점)", min_value=0.0, max_value=4.5, value=prev_gpa_val, step=0.01)
        prev_credits_input = st.number_input("기존 평점 반영 이수 학점", min_value=0, max_value=200, value=prev_credits_val, step=1)

    with c2:
        this_credits_input = st.number_input("이번 학기 예정 학점", min_value=1, max_value=30, value=18, step=1)
        target_gpa_input = st.number_input("목표 누적 평점", min_value=0.0, max_value=4.5, value=4.00, step=0.01)

    if st.button("🚀 필요 평점 역산하기", type="primary", use_container_width=True):
        res = required_gpa(
            prev_gpa=prev_gpa_input,
            prev_credits=prev_credits_input,
            this_credits=this_credits_input,
            target=target_gpa_input,
        )

        st.write("---")
        if res.status == "달성 가능" and res.required_gpa is not None:
            st.success(f"### 🎯 이번 학기 필요 평균 평점: **{format_gpa(res.required_gpa)}** / 4.5")
            st.write(f"- {res.message}")
            st.info(f"💡 필요 평점 {res.required_gpa:.4f}점 (소수 둘째 자리 올림 시 {res.required_gpa + 0.005:.2f})")
        elif res.status == "달성 불가" and res.required_gpa is not None:
            st.warning(f"### ⚠️ 현재 조건에서 달성 어려움 (필요 평점: **{format_gpa(res.required_gpa)}**)")
            st.write(f"- {res.message}")
            st.caption("이수 학점을 늘리거나 목표 평점을 조정해보세요.")
        elif res.status == "이미 달성":
            st.info(f"### 🎉 이미 달성 가능!")
            st.write(f"- {res.message}")
        else:
            st.error(f"오류: {res.message}")


def tab_simulation(all_semesters: list[str]) -> None:
    """과목별 성적 등급 변경 시뮬레이션 탭을 렌더링한다."""
    st.subheader("3. 성적 시뮬레이터")
    st.caption("이번 학기 수강 과목의 예상 등급을 실시간으로 바꾸어가며 누적 평점 변화를 확인하세요.")

    if not all_semesters:
        st.warning("먼저 1번 탭에서 과목을 등록해주세요.")
        return

    sim_sem = st.selectbox("시뮬레이션 대상 학기 선택", options=all_semesters, key="sim_sem")
    courses = get_courses(sim_sem)

    if not courses:
        st.info("해당 학기에 등록된 과목이 없습니다.")
        return

    # 기준 학기 제외한 기존 누적 성적 계산
    other_courses = [c for c in get_courses() if c.semester != sim_sem]
    prev_gpa, prev_credits = calculate_cumulative_gpa(other_courses)

    st.write(f"#### 📝 [{sim_sem}] 과목별 예상 등급 조정")
    overrides: dict[str, str] = {}

    cols = st.columns(min(len(courses), 4))
    for i, c in enumerate(courses):
        with cols[i % len(cols)]:
            cur_idx = GRADE_OPTIONS.index(c.grade) if c.grade in GRADE_OPTIONS else 0
            new_g = st.selectbox(
                f"{c.name} ({c.credits}학점)",
                options=GRADE_OPTIONS,
                index=cur_idx,
                key=f"sim_{c.id}_{c.name}",
            )
            overrides[c.name] = new_g

    # 원본 vs 시뮬레이션 계산
    orig_sem_gpa, orig_sem_credits = calculate_semester_gpa(courses)
    orig_cum_gpa, _ = calculate_combined_gpa(prev_gpa, prev_credits, orig_sem_gpa, orig_sem_credits)

    sim_sem_gpa, sim_sem_credits = simulate_semester(courses, overrides)
    sim_cum_gpa, _ = calculate_combined_gpa(prev_gpa, prev_credits, sim_sem_gpa, sim_sem_credits)

    st.write("---")
    st.write("#### 📊 시뮬레이션 결과 비교")
    m1, m2 = st.columns(2)
    with m1:
        st.metric(
            label="학기 평균 평점",
            value=f"{format_gpa(sim_sem_gpa)}",
            delta=f"{sim_sem_gpa - orig_sem_gpa:+.2f}",
        )
    with m2:
        st.metric(
            label="전체 누적 평점",
            value=f"{format_gpa(sim_cum_gpa)}",
            delta=f"{sim_cum_gpa - orig_cum_gpa:+.2f}",
        )

    # 시나리오 비교 프리셋
    with st.expander("🔍 주요 시나리오 자동 비교"):
        target_input = st.number_input("달성 목표 누적 평점 입력", min_value=0.0, max_value=4.5, value=4.00, step=0.05)
        scenarios = {
            "현재 등록 상태": {c.name: c.grade for c in courses},
            "전체 A+ 취득 시": {c.name: "A+" for c in courses},
            "전체 A 취득 시": {c.name: "A" for c in courses},
            "전체 B+ 취득 시": {c.name: "B+" for c in courses},
        }
        scenario_results = compare_scenarios(
            courses=courses,
            scenarios=scenarios,
            prev_gpa=prev_gpa,
            prev_credits=prev_credits,
            target=target_input,
        )

        res_data = []
        for name, r in scenario_results.items():
            res_data.append(
                {
                    "시나리오": name,
                    "학기 평점": format_gpa(r.semester_gpa),
                    "누적 평점": format_gpa(r.cumulative_gpa),
                    "목표 달성 여부": "✅ " + r.status if r.is_achieved else "❌ " + r.status,
                    "안내": r.message,
                }
            )
        st.dataframe(res_data, use_container_width=True)


def tab_graph_view() -> None:
    """학기별 성적 추이 그래프 탭을 렌더링한다."""
    st.subheader("4. 학기별 성적 추이 그래프")
    st.caption("등록된 학기별 성적 변화와 누적 평점의 추이를 그래프로 확인합니다.")

    fig = create_gpa_trend_chart()
    st.pyplot(fig)


def main() -> None:
    """GradePlan 웹 애플리케이션 메인 실행 함수."""
    setup_page_config()
    init_db()
    render_header()

    all_semesters = get_all_semesters()

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📚 과목 성적 관리",
            "🎯 목표 학점 역산",
            "🔮 성적 시뮬레이터",
            "📈 성적 추이 그래프",
        ]
    )

    with tab1:
        tab_course_management(all_semesters)
    with tab2:
        tab_goal_prediction()
    with tab3:
        tab_simulation(all_semesters)
    with tab4:
        tab_graph_view()


if __name__ == "__main__":
    main()
