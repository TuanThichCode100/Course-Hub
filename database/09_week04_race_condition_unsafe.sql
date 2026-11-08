-- Tab A - giu trang thai cu trong 8 giay
-- BEGIN;
-- SELECT cs.id, cs.capacity, COUNT(e.student_id) AS enrolled
-- FROM class_sections AS cs
-- LEFT JOIN enrollments AS e ON e.class_section_id = cs.id
-- WHERE cs.id = 'RACE-01'
-- GROUP BY cs.id, cs.capacity;
-- SELECT pg_sleep(8);
-- INSERT INTO enrollments (student_id, class_section_id)
-- VALUES ('22000002', 'RACE-01');
-- COMMIT;

-- Tab B - chay khi Tab A dang pg_sleep
-- BEGIN;
-- SELECT cs.id, cs.capacity, COUNT(e.student_id) AS enrolled
-- FROM class_sections AS cs
-- LEFT JOIN enrollments AS e ON e.class_section_id = cs.id
-- WHERE cs.id = 'RACE-01'
-- GROUP BY cs.id, cs.capacity;
-- INSERT INTO enrollments (student_id, class_section_id)
-- VALUES ('22000004', 'RACE-01');
-- COMMIT;

-- Kiem tra ket qua sau khi ca hai tab hoan tat
SELECT cs.id, cs.capacity,
COUNT(e.student_id) AS enrolled,
cs.capacity - COUNT(e.student_id) AS remaining
FROM class_sections AS cs
LEFT JOIN enrollments AS e ON e.class_section_id = cs.id
WHERE cs.id = 'RACE-01'
GROUP BY cs.id, cs.capacity;

SELECT student_id, class_section_id
FROM enrollments
WHERE class_section_id = 'RACE-01'
ORDER BY student_id;
