-- Simulated IoT sensor dataset
CREATE TABLE sensors (id SERIAL PRIMARY KEY, type VARCHAR(50), location VARCHAR(50));

CREATE TABLE sensor_data (time TIMESTAMPTZ NOT NULL, sensor_id INTEGER REFERENCES sensors(id), temperature DOUBLE PRECISION, cpu DOUBLE PRECISION);

SELECT create_hypertable('sensor_data', by_range('time'));

INSERT INTO sensors (type, location) VALUES ('a', 'floor'), ('a', 'ceiling'), ('b', 'floor'), ('b', 'ceiling');

INSERT INTO sensor_data (time, sensor_id, temperature, cpu) SELECT t, s.id, 18 + random() * 10, random() FROM generate_series(now() - INTERVAL '24 hours', now(), INTERVAL '5 minutes') AS t CROSS JOIN sensors s;

-- Average temperature and CPU every 30 minutes, per sensor location
SELECT time_bucket('30 minutes', d.time) AS period, s.location, ROUND(AVG(d.temperature)::numeric, 2) AS avg_temp, ROUND(AVG(d.cpu)::numeric, 2) AS avg_cpu FROM sensor_data d JOIN sensors s ON s.id = d.sensor_id GROUP BY period, s.location ORDER BY period DESC, s.location LIMIT 20;
