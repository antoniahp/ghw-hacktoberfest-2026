import json
from datetime import timezone

from django.test import SimpleTestCase

from market.management.commands.ingest_prices import parse_ticker


class ParseTickerTests(SimpleTestCase):
    def test_parses_coinbase_ticker(self):
        message = json.dumps({
            "type": "ticker", "product_id": "BTC-USD", "price": "65432.10",
            "last_size": "0.0125", "time": "2026-10-15T12:00:01.123456Z",
        })
        when, symbol, price, volume = parse_ticker(message)
        self.assertEqual(symbol, "BTC-USD")
        self.assertEqual(price, 65432.10)
        self.assertEqual(volume, 0.0125)
        self.assertEqual(when.tzinfo, timezone.utc)

    def test_ignores_other_messages(self):
        self.assertIsNone(parse_ticker(json.dumps({"type": "subscriptions", "channels": []})))
