-- Class grades for one school term (Sept–Dec 2026)
-- Tiger Cloud / TimescaleDB: "grades" is a hypertable partitioned by exam date.

CREATE TABLE IF NOT EXISTS students (
    id         SERIAL PRIMARY KEY,
    full_name  TEXT NOT NULL,
    class_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS grades (
    student_id INTEGER NOT NULL REFERENCES students(id),
    subject    TEXT    NOT NULL,
    score      NUMERIC(4,2) NOT NULL CHECK (score BETWEEN 0 AND 10),
    exam_date  TIMESTAMPTZ NOT NULL
);

-- Turn "grades" into a hypertable, partitioned by exam_date in 1-month chunks
SELECT create_hypertable('grades', by_range('exam_date', INTERVAL '1 month'), if_not_exists => TRUE);

-- Sample students
INSERT INTO students (full_name, class_name) VALUES
    ('Lucia Martinez', '4A'),
    ('Pablo Garcia',   '4A'),
    ('Sofia Lopez',    '4A'),
    ('Hugo Sanchez',   '4A'),
    ('Martina Perez',  '4A'),
    ('Daniel Gomez',   '4A'),
    ('Valeria Ruiz',   '4A'),
    ('Alejandro Diaz', '4A');

-- Sample grades: one exam per subject every two weeks, from September to December
INSERT INTO grades (student_id, subject, score, exam_date)
SELECT s.id,
       subj,
       ROUND((4 + random() * 6)::numeric, 2),
       d + (random() * INTERVAL '3 days')
FROM students s
CROSS JOIN unnest(ARRAY['Math', 'English', 'Science', 'History']) AS subj
CROSS JOIN generate_series('2026-09-14'::timestamptz, '2026-12-14'::timestamptz, INTERVAL '14 days') AS d;
