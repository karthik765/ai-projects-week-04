import json
import tempfile
import unittest
from pathlib import Path

from usage_analyzer import analyze
from usage_analyzer.loader import load_records, records_from_objects


class UsageAnalyzerTests(unittest.TestCase):
    def test_aggregates_totals_and_models(self):
        records = records_from_objects([
            {"timestamp": "a", "model": "gpt-4o-mini", "input_tokens": 100, "output_tokens": 50, "latency_ms": 100},
            {"timestamp": "b", "model": "gpt-4o-mini", "input_tokens": 200, "output_tokens": 50, "latency_ms": 300, "status": "error"},
        ])
        report = analyze(records)
        self.assertEqual((report.requests, report.successful, report.failed), (2, 1, 1))
        self.assertEqual((report.input_tokens, report.output_tokens), (300, 100))
        self.assertEqual(report.by_model[0].p95_latency_ms, 300)
        self.assertTrue(report.warnings)

    def test_budget_warning_is_explainable(self):
        record = records_from_objects([{"timestamp": "a", "model": "gpt-4o", "input_tokens": 1_000_000, "output_tokens": 1_000_000, "latency_ms": 10}])[0]
        report = analyze([record], budget=1.0)
        self.assertIn("exceeds budget", report.warnings[0])

    def test_loader_rejects_missing_and_negative_values(self):
        with self.assertRaises(ValueError):
            records_from_objects([{"timestamp": "a", "model": "x", "input_tokens": -1, "output_tokens": 2, "latency_ms": 3}])
        with self.assertRaises(ValueError):
            records_from_objects([{"timestamp": "a", "model": "x"}])

    def test_jsonl_loader_and_serialization(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "usage.jsonl"
            path.write_text('{"timestamp":"a","model":"x","input_tokens":1,"output_tokens":2,"latency_ms":3}\n', encoding="utf-8")
            report = analyze(load_records(path))
        payload = report.to_dict()
        self.assertEqual(payload["requests"], 1)
        self.assertEqual(json.loads(json.dumps(payload))["by_model"][0]["model"], "x")


if __name__ == "__main__":
    unittest.main()
