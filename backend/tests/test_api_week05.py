import requests

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    # 1. Health check
    res = requests.get(f"{BASE_URL}/health", timeout=5)
    assert res.status_code == 200, f"Health check failed: {res.status_code}"

    # 2. GET /enrollment-events demo with pagination
    res = requests.get(f"{BASE_URL}/enrollment-events?dataset=demo&limit=2&skip=0", timeout=5)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    events = res.json()
    assert isinstance(events, list), "Expected list response"
    assert len(events) <= 2, f"Expected <= 2 events, got {len(events)}"
    print(f"PASS: GET /enrollment-events returned {len(events)} events (limit=2)")

    # 3. GET /enrollment-events validation error on dataset
    res = requests.get(f"{BASE_URL}/enrollment-events?dataset=invalid", timeout=5)
    assert res.status_code == 400, f"Expected 400, got {res.status_code}"
    print("PASS: GET /enrollment-events rejected invalid dataset with 400")

    # 4. GET /sections with server-side filter & pagination
    res = requests.get(f"{BASE_URL}/sections?course_code=INT2204&limit=10", timeout=5)
    assert res.status_code == 200
    sections = res.json()
    assert all(s["course_code"] == "INT2204" for s in sections), "Filter course_code failed"
    print(f"PASS: GET /sections filtered by INT2204 returned {len(sections)} sections")

    # 5. Full lifecycle: Create (201) -> Duplicate (409) -> Verify Event -> Delete (204) -> Delete not found (404)
    student_id = "22000004"
    section_id = "PY-01"

    # Reset before test
    requests.delete(f"{BASE_URL}/enrollments/{student_id}/{section_id}", timeout=5)

    # 5a. Create enrollment -> 201
    r_create = requests.post(
        f"{BASE_URL}/enrollments",
        json={"student_id": student_id, "class_section_id": section_id},
        timeout=5,
    )
    assert r_create.status_code == 201, f"Expected 201, got {r_create.status_code}"
    print("PASS: POST /enrollments returned 201 Created")

    # 5b. Duplicate enrollment -> 409
    r_dup = requests.post(
        f"{BASE_URL}/enrollments",
        json={"student_id": student_id, "class_section_id": section_id},
        timeout=5,
    )
    assert r_dup.status_code == 409, f"Expected 409, got {r_dup.status_code}"
    print("PASS: POST /enrollments duplicate returned 409 Conflict")

    # 5c. Check event created
    r_ev1 = requests.get(
        f"{BASE_URL}/enrollment-events?student_id={student_id}&dataset=demo&limit=5",
        timeout=5,
    )
    assert r_ev1.status_code == 200
    ev1_list = r_ev1.json()
    assert len(ev1_list) > 0 and ev1_list[0]["event_type"] == "CREATED"
    print(f"PASS: Enrollment event 'CREATED' found for {student_id}")

    # 5d. Delete enrollment -> 204
    r_del = requests.delete(
        f"{BASE_URL}/enrollments/{student_id}/{section_id}",
        timeout=5,
    )
    assert r_del.status_code == 204, f"Expected 204, got {r_del.status_code}"
    print("PASS: DELETE /enrollments returned 204 No Content")

    # 5e. Delete enrollment not found -> 404
    r_del404 = requests.delete(
        f"{BASE_URL}/enrollments/{student_id}/{section_id}",
        timeout=5,
    )
    assert r_del404.status_code == 404, f"Expected 404, got {r_del404.status_code}"
    print("PASS: DELETE /enrollments not found returned 404 Not Found")

    # 5f. Check event cancelled
    r_ev2 = requests.get(
        f"{BASE_URL}/enrollment-events?student_id={student_id}&dataset=demo&limit=5",
        timeout=5,
    )
    assert r_ev2.status_code == 200
    ev2_list = r_ev2.json()
    assert len(ev2_list) > 0 and ev2_list[0]["event_type"] == "CANCELLED"
    print(f"PASS: Enrollment event 'CANCELLED' found for {student_id}")

    print("\n=========================================")
    print("ALL BUOI 5 INTEGRATION TESTS PASSED 100%!")
    print("=========================================")

if __name__ == "__main__":
    test_api()
