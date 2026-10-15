-- Continuous aggregate on the "grades" hypertable: monthly stats per subject
CREATE MATERIALIZED VIEW monthly_subject_stats WITH (timescaledb.continuous) AS SELECT time_bucket('1 month', exam_date) AS month, subject, ROUND(AVG(score), 2) AS avg_score, MIN(score) AS min_score, MAX(score) AS max_score, COUNT(*) AS exams FROM grades GROUP BY month, subject;

-- Keep it refreshed automatically every hour
SELECT add_continuous_aggregate_policy('monthly_subject_stats', start_offset => INTERVAL '6 months', end_offset => NULL, schedule_interval => INTERVAL '1 hour');

-- Dashboard query: read pre-computed stats
SELECT * FROM monthly_subject_stats ORDER BY month, subject;
