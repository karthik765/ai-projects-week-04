import json
from typing import Any

from .cleaner import clean_json_text
from .models import Issue, RepairReport
from .validator import validate


def inspect_output(raw_text: str, schema: dict[str, Any]) -> RepairReport:
    try:
        cleaned_text, repairs = clean_json_text(raw_text)
    except ValueError as exc:
        return RepairReport(False, "", issues=[Issue("$", "empty_input", str(exc))])
    try:
        value = json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        issue = Issue("$", "invalid_json", f"line {exc.lineno}, column {exc.colno}: {exc.msg}")
        return RepairReport(False, cleaned_text, repairs=repairs, issues=[issue])
    issues = validate(value, schema)
    return RepairReport(not issues, cleaned_text, value, repairs, issues)
