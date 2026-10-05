# AI Usage Analyzer

AI systems are easier to operate when request usage is measurable. This dependency-free toolkit reads JSONL request logs and produces an explainable summary of request volume, token totals, estimated cost, latency, failures, and per-model performance.

## Features

- Validates and loads JSONL records with clear line-level errors.
- Aggregates input/output tokens, success and failure counts, estimated cost, average latency, and p95 latency.
- Breaks results down by model and flags high failure rates or an exceeded budget.
- Includes a Python API and human-readable or JSON CLI output.
- Uses illustrative pricing profiles only; it never calls a paid service or claims to be live billing data.

## Quick start

Requires Python 3.10 or newer. No third-party packages are needed.

```powershell
python -m unittest discover -s tests -v
python -m usage_analyzer examples/usage.jsonl
python -m usage_analyzer examples/usage.jsonl --budget 0.01 --json
```

Each input line must contain `timestamp`, `model`, `input_tokens`, `output_tokens`, and `latency_ms`. Optional fields include `status`, `request_id`, and arbitrary metadata. Statuses `success`, `ok`, and `completed` count as successful; other values count as failed.

## Python API

```python
from usage_analyzer import analyze
from usage_analyzer.loader import records_from_objects

records = records_from_objects([{
    "timestamp": "2026-10-05T13:00:00Z",
    "model": "gpt-4o-mini",
    "input_tokens": 800,
    "output_tokens": 220,
    "latency_ms": 410,
}])
report = analyze(records, budget=0.01)
print(report.to_dict())
```

Pricing is intentionally stored in `usage_analyzer/pricing.py` as illustrative USD rates. Update those profiles for an internal estimate, and label any resulting report appropriately before using it for billing decisions.
