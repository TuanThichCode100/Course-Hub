# -*- coding: utf-8 -*-
"""
Bai tap Tuan 1: Quan ly dang ky hoc phan (Course Hub)
- Hoan thien ham dang ky hoc phan: enroll_student(student_id, course_code)
- Kiem tra cac tinh huong dang ky
"""

students = [
    {"id": "22000001", "name": "Nguyen Minh Anh", "major": "KHDL"},
    {"id": "22000002", "name": "Tran Duc Long", "major": "KHDL"},
]

courses = [
    {
        "code": "INT2204",
        "name": "Co so du lieu Web va he thong thong tin",
        "capacity": 3,
        "enrolled": 2,
    },
    {
        "code": "INT2205",
        "name": "Khai pha du lieu",
        "capacity": 2,
        "enrolled": 2,
    },
]

enrollments = [
    {"student_id": "22000001", "course_code": "INT2204"}
]

# 1. Ham tim kiem hoc phan theo ma
def find_course(course_code):
    for course in courses:
        if course["code"] == course_code:
            return course
    return None

# 2. Ham tim kiem sinh vien theo ma sinh vien
def find_student(student_id):
    for student in students:
        if student["id"] == student_id:
            return student
    return None

# 3. Ham dang ky hoc phan (enroll_student)
def enroll_student(student_id, course_code):
    """
    Dang ky hoc phan cho sinh vien.
    Kiem tra:
      - Sinh vien ton tai
      - Hoc phan ton tai
      - Sinh vien chua dang ky trung
      - Lop con cho trong
    Neu thanh cong:
      - Them ban ghi moi vao enrollments
      - Cap nhat so luong enrolled cua hoc phan (+1)
    Tra ve: (bool, str) - Trang thai thanh cong va thong bao mo ta
    """
    # Buoc 1: Kiem tra sinh vien ton tai
    student = find_student(student_id)
    if student is None:
        return False, "Sinh vien khong ton tai"

    # Buoc 2: Kiem tra hoc phan ton tai
    course = find_course(course_code)
    if course is None:
        return False, "Hoc phan khong ton tai"

    # Buoc 3: Kiem tra sinh vien chua dang ky trung
    duplicate = any(
        item["student_id"] == student_id and item["course_code"] == course_code
        for item in enrollments
    )
    if duplicate:
        return False, "Sinh vien da dang ky hoc phan nay"

    # Buoc 4: Kiem tra lop con cho
    if course["enrolled"] >= course["capacity"]:
        return False, "Lop da du so luong"

    # Buoc 5: Dang ky thanh cong -> them vao enrollments va tang enrolled
    enrollments.append({"student_id": student_id, "course_code": course_code})
    course["enrolled"] += 1
    return True, "Dang ky thanh cong"

# Ham tim kiem hoc phan theo tu khoa
def search_courses(keyword):
    normalized = keyword.strip().lower()
    results = []
    for course in courses:
        code = course["code"].lower()
        name = course["name"].lower()
        if normalized in code or normalized in name:
            results.append(course)
    return results

if __name__ == "__main__":
    print("Course Hub - Buoi 1: Python Refresh & Enrollment System\n")

    # Kiem tra chuong trinh voi toi thieu 05 tinh huong chay thu
    print("=" * 60)
    print("KIEM TRA CHUONG TRINH DANG KY HOC PHAN (05 TINH HUONG)")
    print("=" * 60)

    test_cases = [
        {
            "name": "Tinh huong 1: Dang ky thanh cong (lop con cho, sv ton tai, chua dk)",
            "student_id": "22000002",
            "course_code": "INT2204",
        },
        {
            "name": "Tinh huong 2: Dang ky trung (sv da dang ky hoc phan nay)",
            "student_id": "22000001",
            "course_code": "INT2204",
        },
        {
            "name": "Tinh huong 3: Lop day (hoc phan da dat suc chua toi da)",
            "student_id": "22000001",
            "course_code": "INT2205",
        },
        {
            "name": "Tinh huong 4: Ma hoc phan khong ton tai",
            "student_id": "22000001",
            "course_code": "INT9999",
        },
        {
            "name": "Tinh huong 5: Ma sinh vien khong ton tai",
            "student_id": "99999999",
            "course_code": "INT2204",
        },
    ]

    for tc in test_cases:
        success, message = enroll_student(tc["student_id"], tc["course_code"])
        status_text = "THANH CONG" if success else "THAT BAI"
        print(f"[{status_text}] {tc['name']}")
        print(f"   -> Input: student_id='{tc['student_id']}', course_code='{tc['course_code']}'")
        print(f"   -> Output: success={success}, thong_bao='{message}'\n")

    print("=" * 60)
    print("TRANG THAI DU LIEU SAU KHI CHAY CAC TINH HUONG:")
    print("Danh sach enrollments:")
    for enr in enrollments:
        print(f"   - {enr}")
    print("\nDanh sach courses:")
    for c in courses:
        print(f"   - {c['code']}: {c['name']} (Enrolled: {c['enrolled']}/{c['capacity']})")
    print("=" * 60)