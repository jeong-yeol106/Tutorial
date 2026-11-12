"""SQLite 기반 과목 성적 데이터 저장 및 조회 모듈."""

import sqlite3
from typing import Optional

from core.models import Course

DEFAULT_DB_PATH: str = "gradeplan.db"


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """SQLite 데이터베이스 연결을 생성하여 반환한다."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """데이터베이스 테이블을 생성하고 초기화한다."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                semester TEXT NOT NULL,
                name TEXT NOT NULL,
                credits INTEGER NOT NULL,
                grade TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(semester, name)
            )
            """
        )
        conn.commit()


def add_course(
    semester: str,
    course: Course,
    db_path: str = DEFAULT_DB_PATH,
) -> tuple[bool, str]:
    """과목을 등록하며 동일 학기 중복 과목일 경우 등록을 거부한다."""
    init_db(db_path)
    clean_sem = semester.strip()
    clean_name = course.name.strip()

    if not clean_sem:
        return False, "학기를 입력해주세요."
    if not clean_name:
        return False, "과목명을 입력해주세요."
    if course.credits not in {1, 2, 3, 4}:
        return False, "이수 학점은 1~4학점 사이의 정수만 허용됩니다."

    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO courses (semester, name, credits, grade)
                VALUES (?, ?, ?, ?)
                """,
                (clean_sem, clean_name, course.credits, course.grade.upper()),
            )
            conn.commit()
            return True, f"과목 '{clean_name}'이(가) 등록되었습니다."
    except sqlite3.IntegrityError:
        return False, f"동일 학기({clean_sem})에 이미 등록된 과목명입니다: {clean_name}"


def update_course(
    course_id: int,
    semester: str,
    course: Course,
    db_path: str = DEFAULT_DB_PATH,
) -> tuple[bool, str]:
    """과목 정보를 수정하며 중복 이름 충돌을 방지한다."""
    init_db(db_path)
    clean_sem = semester.strip()
    clean_name = course.name.strip()

    if not clean_name:
        return False, "과목명을 입력해주세요."
    if course.credits not in {1, 2, 3, 4}:
        return False, "이수 학점은 1~4학점 사이의 정수만 허용됩니다."

    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE courses
                SET semester = ?, name = ?, credits = ?, grade = ?
                WHERE id = ?
                """,
                (clean_sem, clean_name, course.credits, course.grade.upper(), course_id),
            )
            conn.commit()
            return True, f"과목 '{clean_name}' 정보가 수정되었습니다."
    except sqlite3.IntegrityError:
        return False, f"해당 학기에 동일한 이름의 다른 과목이 이미 존재합니다: {clean_name}"


def delete_course(course_id: int, db_path: str = DEFAULT_DB_PATH) -> bool:
    """과목 ID를 기준으로 과목 레코드를 삭제한다."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        conn.commit()
        return cursor.rowcount > 0


def get_courses(
    semester: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH,
) -> list[Course]:
    """지정된 학기(또는 전체)의 과목 목록을 조회하여 반환한다."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if semester:
            cursor.execute(
                "SELECT id, semester, name, credits, grade FROM courses WHERE semester = ? ORDER BY id ASC",
                (semester.strip(),),
            )
        else:
            cursor.execute(
                "SELECT id, semester, name, credits, grade FROM courses ORDER BY semester ASC, id ASC"
            )
        rows = cursor.fetchall()
        return [
            Course(
                id=row["id"],
                semester=row["semester"],
                name=row["name"],
                credits=row["credits"],
                grade=row["grade"],
            )
            for row in rows
        ]


def get_all_semesters(db_path: str = DEFAULT_DB_PATH) -> list[str]:
    """등록된 모든 고유 학기 목록을 정렬하여 반환한다."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT semester FROM courses ORDER BY semester ASC")
        rows = cursor.fetchall()
        return [row["semester"] for row in rows]
