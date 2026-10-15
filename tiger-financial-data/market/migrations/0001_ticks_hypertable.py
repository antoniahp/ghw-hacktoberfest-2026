from django.db import migrations

CREATE_TICKS = """
CREATE TABLE IF NOT EXISTS ticks (
    time   TIMESTAMPTZ      NOT NULL,
    symbol TEXT             NOT NULL,
    price  DOUBLE PRECISION NOT NULL,
    volume DOUBLE PRECISION NOT NULL DEFAULT 0
);
SELECT create_hypertable('ticks', by_range('time', INTERVAL '1 day'), if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS ticks_symbol_time_idx ON ticks (symbol, time DESC);
"""

CREATE_CANDLES = """
CREATE MATERIALIZED VIEW IF NOT EXISTS ticks_1m
WITH (timescaledb.continuous, timescaledb.materialized_only = false) AS
SELECT time_bucket('1 minute', time) AS bucket,
       symbol,
       first(price, time) AS open,
       max(price)         AS high,
       min(price)         AS low,
       last(price, time)  AS close,
       sum(volume)        AS volume,
       count(*)           AS trades
FROM ticks
GROUP BY bucket, symbol
WITH NO DATA;
"""

ADD_POLICY = """
SELECT add_continuous_aggregate_policy('ticks_1m',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute',
    if_not_exists => TRUE);
"""


class Migration(migrations.Migration):
    # Continuous aggregates cannot be created inside a transaction
    atomic = False
    initial = True
    dependencies = []

    operations = [
        migrations.RunSQL(CREATE_TICKS, reverse_sql="DROP TABLE IF EXISTS ticks;"),
        migrations.RunSQL(CREATE_CANDLES, reverse_sql="DROP MATERIALIZED VIEW IF EXISTS ticks_1m;"),
        migrations.RunSQL(ADD_POLICY, reverse_sql=migrations.RunSQL.noop),
    ]
