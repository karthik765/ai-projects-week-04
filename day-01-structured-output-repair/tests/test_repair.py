import json
import unittest

from structured_output_repair import inspect_output


SCHEMA = {
    "type": "object",
    "required": ["answer", "confidence"],
    "properties": {
        "answer": {"type": "string", "minLength": 1},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
}


class StructuredOutputRepairTests(unittest.TestCase):
    def test_fence_and_trailing_comma_are_repaired(self):
        report = inspect_output('```json{"answer":"ready","confidence":0.8,}```', SCHEMA)
        self.assertTrue(report.ok)
        self.assertEqual(report.cleaned_value["answer"], "ready")
        self.assertEqual(len(report.repairs), 2)

    def test_missing_required_field_is_explained(self):
        report = inspect_output('{"answer":"ready"}', SCHEMA)
        self.assertFalse(report.ok)
        self.assertEqual(report.issues[0].path, "$.confidence")
        self.assertEqual(report.issues[0].code, "required")

    def test_wrong_nested_type_is_explained(self):
        report = inspect_output('{"answer":3,"confidence":0.8}', SCHEMA)
        self.assertFalse(report.ok)
        self.assertEqual(report.issues[0].path, "$.answer")
        self.assertEqual(report.issues[0].code, "type")

    def test_out_of_range_number_is_rejected(self):
        report = inspect_output('{"answer":"ready","confidence":1.4}', SCHEMA)
        self.assertFalse(report.ok)
        self.assertEqual(report.issues[0].code, "maximum")

    def test_invalid_json_is_not_guessed(self):
        report = inspect_output('{"answer":}', SCHEMA)
        self.assertFalse(report.ok)
        self.assertEqual(report.issues[0].code, "invalid_json")

    def test_comma_inside_string_is_preserved(self):
        report = inspect_output('{"answer":"comma,}","confidence":0.8,}', SCHEMA)
        self.assertTrue(report.ok)
        self.assertEqual(report.cleaned_value["answer"], "comma,}")

    def test_report_is_json_serializable(self):
        report = inspect_output('{"answer":"ready","confidence":0.8}', SCHEMA)
        json.dumps(report.to_dict())


if __name__ == "__main__":
    unittest.main()
