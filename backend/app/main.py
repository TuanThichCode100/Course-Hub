from __future__ import annotations
import logging
from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .database import engine
from .schemas import EnrollmentCreate, SectionCapacityUpdate

logger = logging.getLogger(__name__)
app = FastAPI(
    title="CourseHub API",
    version="0.5.0",
    description="API thuc hanh Buoi 5 - tich hop Frontend React va Backend FastAPI",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "CourseHub API dang hoat dong"}

@app.get("/health")
def health_check() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.exception("Khong ket noi duoc co so du lieu")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Khong ket noi duoc co so du lieu",
        ) from exc
    return {"status": "ok", "database": "connected"}

# Bai 4 (Buoi 3). Tim kiem va phan trang cho danh sach hoc phan
@app.get("/courses")
def list_courses(
    q: str | None = Query(default=None, min_length=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
) -> list[dict[str, object]]:
    sql = """
    SELECT code, name, credits
    FROM courses
    """
    parameters: dict[str, object] = {
        "skip": skip,
        "limit": limit,
    }

    if q is not None:
        keyword = q.strip().lower()
        if not keyword:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tu khoa tim kiem khong duoc rong",
            )
        
        sql += """
        WHERE LOWER(code) LIKE :keyword
        OR LOWER(name) LIKE :keyword
        """

        parameters["keyword"] = f"%{keyword}%"
    
    sql += " ORDER BY code OFFSET :skip LIMIT :limit"

    with engine.connect() as connection:
        rows = connection.execute(text(sql), parameters).mappings().all()
        return [dict(row) for row in rows]

@app.get("/courses/{course_code}")
def get_course(course_code: str) -> dict[str, object]:
    sql = """
    SELECT code, name, credits
    FROM courses
    WHERE code = :course_code
    """
    with engine.connect() as connection:
        row = connection.execute(
            text(sql),
            {"course_code": course_code.upper()},
        ).mappings().first()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay hoc phan",
            )
        return dict(row)

# Bai 1. API danh sach giang vien
@app.get("/lecturers")
def list_lecturers() -> list[dict[str, object]]:
    sql = """
    SELECT id, name
    FROM lecturers
    ORDER BY id
    """
    with engine.connect() as connection:
        rows = connection.execute(text(sql)).mappings().all()
        return [dict(row) for row in rows]

# Bai 4 (Buoi 5). Tim kiem va phan trang CSDL cho lop hoc phan
@app.get("/sections")
def list_sections(
    available_only: bool = False,
    q: str | None = Query(default=None),
    course_code: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[dict[str, object]]:
    sql = """
    SELECT class_id, course_code, capacity, enrolled, remaining
    FROM v_section_summary
    WHERE 1=1
    """
    parameters: dict[str, object] = {
        "skip": skip,
        "limit": limit,
    }

    if available_only:
        sql += " AND remaining > 0"

    if course_code:
        sql += " AND course_code = :course_code"
        parameters["course_code"] = course_code.strip().upper()

    if q is not None:
        keyword = q.strip().lower()
        if keyword:
            sql += " AND (LOWER(class_id) LIKE :keyword OR LOWER(course_code) LIKE :keyword)"
            parameters["keyword"] = f"%{keyword}%"

    sql += " ORDER BY class_id OFFSET :skip LIMIT :limit"

    with engine.connect() as connection:
        rows = connection.execute(text(sql), parameters).mappings().all()
        return [dict(row) for row in rows]

# Bai 2. API chi tiet mot lop hoc phan
@app.get("/sections/{section_id}")
def get_section(section_id: str) -> dict[str, object]:
    sql = """
    SELECT cs.id AS class_id,
           cs.course_code,
           c.name AS course_name,
           s.name AS semester_name,
           l.id AS lecturer_id,
           l.name AS lecturer_name,
           v.capacity,
           v.enrolled,
           v.remaining
    FROM class_sections AS cs
    JOIN courses AS c ON c.code = cs.course_code
    JOIN semesters AS s ON s.code = cs.semester_code
    JOIN lecturers AS l ON l.id = cs.lecturer_id
    JOIN v_section_summary AS v ON v.class_id = cs.id
    WHERE cs.id = :section_id
    """
    with engine.connect() as connection:
        row = connection.execute(
            text(sql),
            {"section_id": section_id},
        ).mappings().first()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay lop hoc phan",
            )
        return dict(row)

# Bai 3. Cap nhat suc chua bang PATCH
@app.patch("/sections/{section_id}/capacity")
def update_section_capacity(
    section_id: str,
    payload: SectionCapacityUpdate,
) -> dict[str, object]:
    check_sql = """
    SELECT class_id, capacity, enrolled
    FROM v_section_summary
    WHERE class_id = :section_id
    """
    update_sql = """
    UPDATE class_sections
    SET capacity = :capacity
    WHERE id = :section_id
    """
    detail_sql = """
    SELECT class_id, course_code, capacity, enrolled, remaining
    FROM v_section_summary
    WHERE class_id = :section_id
    """
    with engine.begin() as connection:
        section = connection.execute(
            text(check_sql),
            {"section_id": section_id},
        ).mappings().first()
        if section is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay lop hoc phan",
            )
        if payload.capacity < section["enrolled"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Suc chua moi khong the nho hon so luong sinh vien da dang ky",
            )
        connection.execute(
            text(update_sql),
            {"section_id": section_id, "capacity": payload.capacity},
        )
        updated = connection.execute(
            text(detail_sql),
            {"section_id": section_id},
        ).mappings().first()
        return dict(updated)  

@app.get("/students/{student_id}/enrollments")
def list_student_enrollments(student_id: str) -> list[dict[str, object]]:
    student_sql = "SELECT id FROM students WHERE id = :student_id"
    enrollment_sql = """
    SELECT e.student_id,
    s.name AS student_name,
    cs.id AS class_section_id,
    c.code AS course_code,
    c.name AS course_name,
    e.registered_at
    FROM enrollments AS e
    JOIN students AS s ON s.id = e.student_id
    JOIN class_sections AS cs ON cs.id = e.class_section_id
    JOIN courses AS c ON c.code = cs.course_code
    WHERE e.student_id = :student_id
    ORDER BY cs.id
    """

    with engine.connect() as connection:
        student = connection.execute(
            text(student_sql),
            {"student_id": student_id},
        ).first()

        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay sinh vien",
            )

        rows = connection.execute(
            text(enrollment_sql),
            {"student_id": student_id},
        ).mappings().all()

        return [dict(row) for row in rows]

# Bai 3 & Bai 4 (Buoi 5). API lich su su kien dang ky voi tim kiem va phan trang phia server
@app.get("/enrollment-events")
def list_enrollment_events(
    student_id: str | None = Query(default=None),
    class_section_id: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    dataset: str = Query(default="demo"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=5, ge=1, le=100),
) -> list[dict[str, object]]:
    """
    Truy van nhat ky su kien dang ky voi tim kiem va phan trang phia CSDL.
    - dataset: mac dinh 'demo' de khong bao gio tai 100.000 su kien performance ve trinh duyet.
    - skip, limit: phan trang LIMIT ... OFFSET phia server.
    - Thu tu on dinh: ORDER BY occurred_at DESC, id DESC.
    """
    if dataset not in ("demo", "performance"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="dataset chi duoc phep la 'demo' hoac 'performance'",
        )
    if event_type is not None and event_type not in ("CREATED", "CANCELLED"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="event_type chi duoc phep la 'CREATED' hoac 'CANCELLED'",
        )

    sql = """
    SELECT e.id,
           e.student_id,
           e.class_section_id,
           cs.course_code,
           c.name AS course_name,
           e.event_type,
           e.source,
           e.dataset,
           e.occurred_at
    FROM enrollment_events AS e
    LEFT JOIN class_sections AS cs ON cs.id = e.class_section_id
    LEFT JOIN courses AS c ON c.code = cs.course_code
    WHERE e.dataset = :dataset
    """
    parameters: dict[str, object] = {
        "dataset": dataset,
        "skip": skip,
        "limit": limit,
    }

    if student_id is not None:
        sql += " AND e.student_id = :student_id"
        parameters["student_id"] = student_id.strip()

    if class_section_id is not None:
        sql += " AND e.class_section_id = :class_section_id"
        parameters["class_section_id"] = class_section_id.strip()

    if event_type is not None:
        sql += " AND e.event_type = :event_type"
        parameters["event_type"] = event_type

    sql += " ORDER BY e.occurred_at DESC, e.id DESC OFFSET :skip LIMIT :limit"

    with engine.connect() as connection:
        rows = connection.execute(text(sql), parameters).mappings().all()
        results: list[dict[str, object]] = []
        for row in rows:
            item = dict(row)
            if item.get("occurred_at") is not None:
                item["occurred_at"] = item["occurred_at"].isoformat()
            results.append(item)
        return results

@app.post(
    "/enrollments",
    status_code=status.HTTP_201_CREATED,
)
def create_enrollment(payload: EnrollmentCreate) -> dict[str, str]:
    student_sql = "SELECT id FROM students WHERE id = :student_id"
    lock_section_sql = """
    SELECT id, capacity
    FROM class_sections
    WHERE id = :class_section_id
    FOR UPDATE
    """
    duplicate_sql = """
    SELECT 1
    FROM enrollments
    WHERE student_id = :student_id
    AND class_section_id = :class_section_id
    """
    count_sql = """
    SELECT COUNT(*)
    FROM enrollments
    WHERE class_section_id = :class_section_id
    """
    insert_sql = """
    INSERT INTO enrollments (student_id, class_section_id)
    VALUES (:student_id, :class_section_id)
    """
    event_sql = """
    INSERT INTO enrollment_events
    (student_id, class_section_id, event_type, source, dataset)
    VALUES
    (:student_id, :class_section_id, 'CREATED', 'api', 'demo')
    """
    parameters = {
        "student_id": payload.student_id,
        "class_section_id": payload.class_section_id,
    }

    try:
        with engine.begin() as connection:
            student = connection.execute(
                text(student_sql),
                {"student_id": payload.student_id},
            ).first()
            if student is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Khong tim thay sinh vien",
                )
            section = connection.execute(
                text(lock_section_sql),
                {"class_section_id": payload.class_section_id},
            ).mappings().first()
            if section is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Khong tim thay lop hoc phan",
                )
            duplicated = connection.execute(
                text(duplicate_sql), parameters
            ).first()
            if duplicated is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Sinh vien da dang ky lop nay",
                )
            enrolled = connection.execute(
                text(count_sql),
                {"class_section_id": payload.class_section_id},
            ).scalar_one()
            if int(enrolled) >= int(section["capacity"]):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Lop hoc phan da het cho",
                )
            connection.execute(text(insert_sql), parameters)
            connection.execute(text(event_sql), parameters)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Dang ky xung dot voi du lieu hien tai",
        ) from exc
    return {
        "message": "Dang ky thanh cong",
        "student_id": payload.student_id,
        "class_section_id": payload.class_section_id,
    }

@app.delete(
    "/enrollments/{student_id}/{class_section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_enrollment(student_id: str, class_section_id: str) -> Response:
    lock_section_sql = """
    SELECT id
    FROM class_sections
    WHERE id = :class_section_id
    FOR UPDATE
    """
    delete_sql = """
    DELETE FROM enrollments
    WHERE student_id = :student_id
    AND class_section_id = :class_section_id
    RETURNING student_id
    """
    event_sql = """
    INSERT INTO enrollment_events
    (student_id, class_section_id, event_type, source, dataset)
    VALUES
    (:student_id, :class_section_id, 'CANCELLED', 'api', 'demo')
    """
    parameters = {
        "student_id": student_id,
        "class_section_id": class_section_id,
    }
    with engine.begin() as connection:
        section = connection.execute(
            text(lock_section_sql),
            {"class_section_id": class_section_id},
        ).first()
        if section is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay lop hoc phan",
            )
        deleted = connection.execute(
            text(delete_sql), parameters
        ).first()
        if deleted is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay dang ky can huy",
            )
        connection.execute(text(event_sql), parameters)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
