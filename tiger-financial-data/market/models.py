from django.db import models


class Tick(models.Model):
    """One trade price received in real time. Stored in the "ticks" hypertable (created in migration 0001)."""

    time = models.DateTimeField(primary_key=True)  # Django needs a pk; the real table has no single-column key
    symbol = models.TextField()
    price = models.FloatField()
    volume = models.FloatField()

    class Meta:
        managed = False
        db_table = "ticks"


class Candle(models.Model):
    """1-minute OHLCV candle, read from the "ticks_1m" continuous aggregate."""

    bucket = models.DateTimeField(primary_key=True)
    symbol = models.TextField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()
    trades = models.IntegerField()

    class Meta:
        managed = False
        db_table = "ticks_1m"
