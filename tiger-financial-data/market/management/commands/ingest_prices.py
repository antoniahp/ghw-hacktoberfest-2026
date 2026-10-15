"""Ingest real-time crypto prices into the Tiger Cloud "ticks" hypertable.

Live mode (default) uses Coinbase's public WebSocket feed: no account or API key needed.
Demo mode (--demo) simulates prices offline, handy if the network blocks WebSockets.
"""
import json
import random
import time
from datetime import datetime, timezone

from django.core.management.base import BaseCommand
from django.db import connection

COINBASE_WS = "wss://ws-feed.exchange.coinbase.com"
DEMO_START_PRICES = {"BTC-USD": 65000.0, "ETH-USD": 3200.0, "SOL-USD": 150.0}

INSERT_SQL = "INSERT INTO ticks (time, symbol, price, volume) VALUES (%s, %s, %s, %s)"


def parse_ticker(message):
    """Return (time, symbol, price, volume) from a Coinbase ticker message, or None."""
    data = json.loads(message)
    if data.get("type") != "ticker" or "price" not in data:
        return None
    when = datetime.fromisoformat(data["time"].replace("Z", "+00:00")) if data.get("time") else datetime.now(timezone.utc)
    return when, data["product_id"], float(data["price"]), float(data.get("last_size") or 0)


class Command(BaseCommand):
    help = "Stream real-time prices into the ticks hypertable"

    def add_arguments(self, parser):
        parser.add_argument("--symbols", nargs="+", default=["BTC-USD", "ETH-USD", "SOL-USD"])
        parser.add_argument("--seconds", type=int, default=0, help="Stop after N seconds (0 = run until Ctrl+C)")
        parser.add_argument("--flush-every", type=float, default=2.0, help="Seconds between batch inserts")
        parser.add_argument("--demo", action="store_true", help="Simulate prices instead of using Coinbase")

    def handle(self, *args, **options):
        self.batch = []
        self.total = 0
        self.last_flush = time.monotonic()
        self.flush_every = options["flush_every"]
        deadline = time.monotonic() + options["seconds"] if options["seconds"] else None
        symbols = options["symbols"]

        source = "simulated prices" if options["demo"] else "Coinbase live feed"
        self.stdout.write(self.style.SUCCESS(f"Streaming {', '.join(symbols)} from {source}. Press Ctrl+C to stop."))
        try:
            if options["demo"]:
                self.run_demo(symbols, deadline)
            else:
                self.run_live(symbols, deadline)
        except KeyboardInterrupt:
            pass
        except (OSError, TimeoutError, ImportError) as error:
            self.stderr.write(self.style.ERROR(f"Could not reach the Coinbase feed: {error}"))
            self.stderr.write("Check your internet connection, or run with --demo to simulate prices.")
        except Exception as error:  # websockets raises its own exception types
            if type(error).__module__.startswith("websockets"):
                self.stderr.write(self.style.ERROR(f"Coinbase WebSocket error: {error}"))
                self.stderr.write("Run with --demo to simulate prices instead.")
            else:
                raise
        finally:
            self.flush(force=True)
            self.stdout.write(self.style.SUCCESS(f"Done. {self.total} ticks saved to Tiger Cloud."))

    def run_live(self, symbols, deadline):
        from websockets.sync.client import connect

        with connect(COINBASE_WS, open_timeout=15) as ws:
            ws.send(json.dumps({"type": "subscribe", "product_ids": symbols, "channels": ["ticker"]}))
            while deadline is None or time.monotonic() < deadline:
                try:
                    message = ws.recv(timeout=1)
                except TimeoutError:
                    self.flush()
                    continue
                tick = parse_ticker(message)
                if tick:
                    self.batch.append(tick)
                self.flush()

    def run_demo(self, symbols, deadline):
        prices = {s: DEMO_START_PRICES.get(s, 100.0) for s in symbols}
        while deadline is None or time.monotonic() < deadline:
            now = datetime.now(timezone.utc)
            for symbol in symbols:
                prices[symbol] *= 1 + random.gauss(0, 0.0005)
                self.batch.append((now, symbol, round(prices[symbol], 2), round(random.uniform(0.001, 0.5), 4)))
            self.flush()
            time.sleep(0.5)

    def flush(self, force=False):
        if not self.batch or (not force and time.monotonic() - self.last_flush < self.flush_every):
            return
        with connection.cursor() as cursor:
            cursor.executemany(INSERT_SQL, self.batch)
        self.total += len(self.batch)
        latest = {}
        for _, symbol, price, _ in self.batch:
            latest[symbol] = price
        summary = "  ".join(f"{s} {p:,.2f}" for s, p in sorted(latest.items()))
        self.stdout.write(f"+{len(self.batch):>3} ticks (total {self.total})  {summary}")
        self.batch = []
        self.last_flush = time.monotonic()
