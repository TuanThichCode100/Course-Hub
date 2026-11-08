# CourseHub - Buoi 4

- Migration 001: enrollment_events.
- Demo class: RACE-01, capacity = 1.
- POST /enrollments: lock class_sections bang FOR UPDATE.
- Concurrency test: 1 request 201, 1 request 409.
- Performance data: 100000 rows, dataset=performance.
- Index: idx_enrollment_events_dataset_student_time.

## Do luong hieu nang truy van (EXPLAIN ANALYZE, BUFFERS)

### 1. Truoc khi tao chi muc (Sequential Scan)
- **Scan type:** `Seq Scan on enrollment_events`
- **Rows Removed by Filter:** 99180 rows
- **Buffers:** shared hit=1137
- **Planning Time:** 2.252 ms
- **Execution Time:** 13.862 ms

### 2. Sau khi tao chi muc composite (Index Scan)
- **Chi muc:** `idx_enrollment_events_dataset_student_time (dataset, student_id, occurred_at DESC)`
- **Scan type:** `Index Scan`
- **Buffers:** shared hit=50, read=3
- **Planning Time:** 2.209 ms
- **Execution Time:** 0.239 ms

### 3. Nhan xet
- Ke hoach thuc thi chuyen tu `Seq Scan` (quet toan bo 100.000 dong va loai bo 99.180 dong bang filter) sang `Index Scan` (dieu kien so sanh bang dataset, student_id tim thang vung du lieu va doc occurred_at theo thu tu DESC).
- So block I/O (Buffers) giam tu 1137 blocks xuong con 53 blocks.
- Thoi gian thuc thi (Execution Time) giam tu ~13.86 ms xuong ~0.24 ms (tang toc xap xi 58 lan).
