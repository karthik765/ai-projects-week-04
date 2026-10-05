import json
from pathlib import Path
from typing import Iterable

from .models import UsageRecord

REQUIRED = {"timestamp", "model", "input_tokens", "output_tokens", "latency_ms"}


def load_records(path: str | Path) -> list[UsageRecord]:
    records: list[UsageRecord] = []
    for line_number, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
            records.append(_record_from(value, line_number))
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise ValueError(f"line {line_number}: {exc}") from exc
    return records


def records_from_objects(values: Iterable[dict]) -> list[UsageRecord]:
    return [_record_from(value, index) for index, value in enumerate(values, 1)]


def _record_from(value: object, line_number: int) -> UsageRecord:
    if not isinstance(value, dict):
        raise ValueError("expected a JSON object")
    missing = REQUIRED - value.keys()
    if missing:
        raise ValueError(f"missing fields: {', '.join(sorted(missing))}")
    try:
        input_tokens = int(value["input_tokens"])
        output_tokens = int(value["output_tokens"])
        latency_ms = float(value["latency_ms"])
    except (TypeError, ValueError) as exc:
        raise ValueError("token counts and latency must be numeric") from exc
    if input_tokens < 0 or output_tokens < 0 or latency_ms < 0:
        raise ValueError("token counts and latency cannot be negative")
    return UsageRecord(
        timestamp=str(value["timestamp"]), model=str(value["model"]),
        input_tokens=input_tokens, output_tokens=output_tokens,
        latency_ms=latency_ms, status=str(value.get("status", "success")).lower(),
        request_id=str(value.get("request_id", "")),
        metadata={k: v for k, v in value.items() if k not in REQUIRED},
    )
