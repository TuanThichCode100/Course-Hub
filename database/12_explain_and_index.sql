-- 1. Do truy van truoc khi tao chi muc
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, student_id, class_section_id, event_type, occurred_at
FROM enrollment_events
WHERE dataset = 'performance'
AND student_id = '22000001'
AND occurred_at >= TIMESTAMP '2025-12-20 00:00:00'
ORDER BY occurred_at DESC
LIMIT 50;

-- 2. Tao composite index va cap nhat thong ke
CREATE INDEX idx_enrollment_events_dataset_student_time
ON enrollment_events (dataset, student_id, occurred_at DESC);

ANALYZE enrollment_events;

-- 3. Do lai cung truy van sau khi co index
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, student_id, class_section_id, event_type, occurred_at
FROM enrollment_events
WHERE dataset = 'performance'
AND student_id = '22000001'
AND occurred_at >= TIMESTAMP '2025-12-20 00:00:00'
ORDER BY occurred_at DESC
LIMIT 50;

-- 4. Don bo du lieu hieu nang khi can
-- DELETE FROM enrollment_events
-- WHERE dataset = 'performance';
-- ANALYZE enrollment_events;
