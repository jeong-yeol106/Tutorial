"""데이터베이스 CRUD 및 중복 방지 로직 단위 테스트."""

from pathlib import Path
from core.models import Course
from db.database import (
    add_course,
    delete_course,
    get_all_semesters,
    get_courses,
    init_db,
    update_course,
)


def test_db_add_and_get_courses(tmp_path: Path) -> None:
    """과목 등록 및 학기별 조회가 정상 동작해야 한다."""
    db_file = str(tmp_path / "test.db")
    init_db(db_file)

    course1 = Course(name="심화프로그래밍", credits=3, grade="A+")
    success, msg = add_course("2026-2", course1, db_path=db_file)
    assert success is True
    assert "등록되었습니다" in msg

    courses = get_courses("2026-2", db_path=db_file)
    assert len(courses) == 1
    assert courses[0].name == "심화프로그래밍"
    assert courses[0].credits == 3
    assert courses[0].grade == "A+"


def test_db_duplicate_course_rejection(tmp_path: Path) -> None:
    """동일 학기에 동일한 과목명을 중복 등록하려 하면 거부되어야 한다."""
    db_file = str(tmp_path / "test.db")
    init_db(db_file)

    course = Course(name="미분적분학", credits=3, grade="A")
    success1, _ = add_course("2026-2", course, db_path=db_file)
    assert success1 is True

    # 동일 학기 동일 과목 재등록 시도
    success2, msg2 = add_course("2026-2", course, db_path=db_file)
    assert success2 is False
    assert "이미 등록된 과목명" in msg2

    # 다른 학기에 동일 과목 등록은 허용되어야 함
    success3, _ = add_course("2026-1", course, db_path=db_file)
    assert success3 is True


def test_db_invalid_credits_rejection(tmp_path: Path) -> None:
    """이수 학점이 1~4 범위를 벗어날 경우 등록이 거부되어야 한다."""
    db_file = str(tmp_path / "test.db")
    init_db(db_file)

    course = Course(name="특강", credits=5, grade="A+")
    success, msg = add_course("2026-2", course, db_path=db_file)
    assert success is False
    assert "1~4학점" in msg


def test_db_update_and_delete_course(tmp_path: Path) -> None:
    """과목 수정 및 삭제 기능 검증."""
    db_file = str(tmp_path / "test.db")
    init_db(db_file)

    c = Course(name="대학영어 1", credits=3, grade="B+")
    add_course("2026-2", c, db_path=db_file)
    courses = get_courses("2026-2", db_path=db_file)
    course_id = courses[0].id
    assert course_id is not None

    # 수정
    updated_course = Course(name="대학영어 1", credits=3, grade="A+")
    up_success, _ = update_course(course_id, "2026-2", updated_course, db_path=db_file)
    assert up_success is True

    courses_after_up = get_courses("2026-2", db_path=db_file)
    assert courses_after_up[0].grade == "A+"

    # 삭제
    del_success = delete_course(course_id, db_path=db_file)
    assert del_success is True
    assert len(get_courses("2026-2", db_path=db_file)) == 0


def test_db_get_all_semesters(tmp_path: Path) -> None:
    """등록된 학기 목록이 중복 없이 반환되어야 한다."""
    db_file = str(tmp_path / "test.db")
    init_db(db_file)

    add_course("2026-1", Course(name="과목A", credits=3, grade="A"), db_path=db_file)
    add_course("2026-2", Course(name="과목B", credits=3, grade="B"), db_path=db_file)

    semesters = get_all_semesters(db_path=db_file)
    assert semesters == ["2026-1", "2026-2"]
