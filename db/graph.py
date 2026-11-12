"""학기별 평균 평점 변화 시각화 모듈."""

import matplotlib
import matplotlib.pyplot as plt
from core.grade import calculate_cumulative_gpa, calculate_semester_gpa
from db.database import get_all_semesters, get_courses

# 백엔드 및 한글 폰트 설정
matplotlib.use("Agg")
plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "NanumGothic", "DejaVu Sans", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False


def create_gpa_trend_chart(db_path: str = "gradeplan.db") -> matplotlib.figure.Figure:
    """학기별 평균 평점 및 누적 평점 추이를 꺾은선 그래프로 생성한다."""
    semesters = get_all_semesters(db_path=db_path)
    fig, ax = plt.subplots(figsize=(8, 4.5))

    if not semesters:
        ax.text(
            0.5,
            0.5,
            "등록된 과목 및 성적 데이터가 없습니다.",
            horizontalalignment="center",
            verticalalignment="center",
            transform=ax.transAxes,
            fontsize=12,
            color="gray",
        )
        ax.set_axis_off()
        return fig

    sem_gpas: list[float] = []
    cum_gpas: list[float] = []
    accumulated_courses = []

    for sem in semesters:
        sem_courses = get_courses(semester=sem, db_path=db_path)
        sem_gpa, _ = calculate_semester_gpa(sem_courses)
        sem_gpas.append(sem_gpa)

        accumulated_courses.extend(sem_courses)
        cum_gpa, _ = calculate_cumulative_gpa(accumulated_courses)
        cum_gpas.append(cum_gpa)

    ax.plot(semesters, sem_gpas, marker="o", color="#1f77b4", linewidth=2, label="학기 평점")
    ax.plot(semesters, cum_gpas, marker="s", color="#ff7f0e", linewidth=2, linestyle="--", label="누적 평점")

    for i, (sg, cg) in enumerate(zip(sem_gpas, cum_gpas)):
        ax.text(i, sg + 0.05, f"{sg:.2f}", ha="center", color="#1f77b4", fontweight="bold")
        if abs(sg - cg) > 0.08:
            ax.text(i, cg - 0.12, f"{cg:.2f}", ha="center", color="#ff7f0e", fontweight="bold")

    ax.set_title("학기별 성적 추이 (평균 / 누적)", fontsize=14, pad=12)
    ax.set_xlabel("학기", fontsize=11)
    ax.set_ylabel("평점 (4.5 만점)", fontsize=11)
    ax.set_ylim(0.0, 4.8)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="lower right")
    fig.tight_layout()

    return fig
