"""Unit tests for Simplicity Filter."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.agents.simplicity import score_event, scan_and_rank


def _event(
    title,
    *,
    description="This market resolves to Yes if the stated outcome occurs per official sources. Resolution by end date.",
    markets_count=1,
    liquidity=150_000,
    end_days=25,
):
    return {
        "id": "test-1",
        "title": title,
        "description": description,
        "liquidity": liquidity,
        "volume": 500_000,
        "volume24hr": 25_000,
        "endDate": f"2026-07-{max(10, min(28, 10 + end_days)):02d}T00:00:00Z",
        "marketsCount": markets_count,
        "markets": [{"outcomePrices": "[\"0.45\", \"0.55\"]", "outcomes": "[\"Yes\", \"No\"]"}] * markets_count,
    }


class SimplicityFilterTests(unittest.TestCase):
    def test_rejects_fed_macro(self):
        result = score_event(_event("How many Fed rate cuts in 2026?", markets_count=13))
        self.assertEqual(result["decision"], "rejected")
        self.assertEqual(result["score"], 0)

    def test_rejects_midterms(self):
        result = score_event(_event("Which party will win the House in 2026?"))
        self.assertEqual(result["decision"], "rejected")

    def test_accepts_sports_championship(self):
        result = score_event(_event("Will Manchester City win the Champions League final?"))
        self.assertGreaterEqual(result["score"], 70)
        self.assertEqual(result["decision"], "accepted")
        self.assertEqual(result["simpleCategory"], "sports")

    def test_accepts_oscar(self):
        result = score_event(_event("Will Anora win Best Picture at the Oscars?"))
        self.assertGreaterEqual(result["score"], 70)
        self.assertEqual(result["decision"], "accepted")
        self.assertEqual(result["simpleCategory"], "entertainment")

    def test_rejects_multi_market(self):
        result = score_event(
            _event("World Cup Winner 2026", markets_count=5),
        )
        self.assertEqual(result["decision"], "rejected")

    def test_scan_prefers_simple_over_macro(self):
        pool = [
            _event("How many Fed rate cuts in 2026?", markets_count=13),
            _event("Which party will win the Senate in 2026?"),
            _event("Will Team X win the Super Bowl?"),
            _event("Will Movie Y win Best Picture?"),
        ]
        ranking = scan_and_rank(pool, top_n=2)
        titles = [row["event"]["title"] for row in ranking["top"]]
        self.assertTrue(any("Super Bowl" in t or "Best Picture" in t for t in titles))
        self.assertFalse(any("Fed rate" in t for t in titles))


if __name__ == "__main__":
    unittest.main()
