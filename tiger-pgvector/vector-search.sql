-- AI-powered vector search with pgvector on a hypertable (Tiger Cloud)
-- Each study note has a simple 3-dimension embedding: [math, languages, science]

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE study_notes (created_at TIMESTAMPTZ NOT NULL, subject TEXT NOT NULL, title TEXT NOT NULL, embedding vector(3) NOT NULL);

SELECT create_hypertable('study_notes', by_range('created_at'));

INSERT INTO study_notes (created_at, subject, title, embedding) VALUES ('2026-09-15','Math','Fractions and decimals','[0.95,0.05,0.10]'), ('2026-09-22','Math','Linear equations','[0.90,0.05,0.20]'), ('2026-10-06','Math','Probability basics','[0.85,0.10,0.30]'), ('2026-09-16','English','Past simple vs present perfect','[0.05,0.95,0.05]'), ('2026-10-01','English','Writing a formal email','[0.05,0.90,0.10]'), ('2026-09-18','Science','The water cycle','[0.10,0.10,0.95]'), ('2026-10-08','Science','Newton''s laws of motion','[0.45,0.05,0.90]'), ('2026-10-13','Science','Measuring speed and acceleration','[0.60,0.05,0.80]'), ('2026-09-25','History','The Industrial Revolution','[0.05,0.50,0.40]');

-- Similarity search: notes closest to a "physics with math" question, only from October (cosine distance)
SELECT title, subject, created_at::date AS date, ROUND((1 - (embedding <=> '[0.6,0.05,0.85]'))::numeric, 3) AS similarity FROM study_notes WHERE created_at >= '2026-10-01' ORDER BY embedding <=> '[0.6,0.05,0.85]' LIMIT 5;
