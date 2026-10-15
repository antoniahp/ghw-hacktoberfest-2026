-- 1. Term average per student (ranking)
SELECT st.full_name, ROUND(AVG(g.score), 2) AS term_average
FROM grades g JOIN students st ON st.id = g.student_id
GROUP BY st.full_name
ORDER BY term_average DESC;

-- 2. Average per subject and month (uses time_bucket, a TimescaleDB function)
SELECT time_bucket('1 month', exam_date) AS month, subject, ROUND(AVG(score), 2) AS avg_score
FROM grades
GROUP BY month, subject
ORDER BY month, subject;

-- 3. Best score in each subject
SELECT DISTINCT ON (g.subject) g.subject, st.full_name, g.score, g.exam_date::date
FROM grades g JOIN students st ON st.id = g.student_id
ORDER BY g.subject, g.score DESC;

-- 4. Check that "grades" is a hypertable and see its chunks
SELECT hypertable_name, num_chunks FROM timescaledb_information.hypertables;
