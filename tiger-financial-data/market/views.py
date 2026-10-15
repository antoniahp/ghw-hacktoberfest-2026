from datetime import timedelta

from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

LATEST_SQL = """
SELECT DISTINCT ON (symbol) symbol, price, time
FROM ticks
WHERE time > now() - INTERVAL '1 day'
ORDER BY symbol, time DESC
"""

CANDLES_SQL = """
SELECT bucket, symbol, open, high, low, close, volume, trades
FROM ticks_1m
WHERE bucket > %s
ORDER BY bucket
"""

STATS_SQL = "SELECT count(*), min(time), max(time) FROM ticks"


def fetch(sql, params=None):
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        columns = [c.name for c in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_data(minutes=60):
    since = timezone.now() - timedelta(minutes=minutes)
    latest = fetch(LATEST_SQL)
    candles = fetch(CANDLES_SQL, [since])
    count, first, last = fetch(STATS_SQL)[0].values()
    return latest, candles, {"ticks": count, "first": first, "last": last}


def dashboard(request):
    latest, candles, stats = get_data()
    return render(request, "market/dashboard.html", {"latest": latest, "candles": candles[-15:][::-1], "stats": stats})


def prices_api(request):
    latest, candles, stats = get_data()
    return JsonResponse({
        "latest": [{**row, "time": row["time"].isoformat()} for row in latest],
        "candles": [{**row, "bucket": row["bucket"].isoformat()} for row in candles],
        "stats": {**stats, "first": stats["first"] and stats["first"].isoformat(), "last": stats["last"] and stats["last"].isoformat()},
    })
