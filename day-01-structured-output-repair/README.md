# Structured Output Repair

Language models often return JSON wrapped in Markdown fences or with a trailing comma. Those small formatting defects can break an otherwise useful automation. This dependency-free toolkit cleans the safest common defects, validates the resulting value against a compact JSON-schema subset, and explains what still needs human or model attention.

## Features

- Extracts JSON from plain text or a Markdown `json` fence.
- Removes trailing commas without guessing at missing content.
- Validates `type`, `required`, `properties`, `items`, `enum`, length, and numeric bounds.
- Reports repair steps, precise issue paths, and a pass/fail summary.
- Provides both a Python API and a CLI with human-readable or JSON output.

## Quick start

Requires Python 3.10 or newer. No third-party packages are needed.

```powershell
python -m unittest discover -s tests -v
python -m structured_output_repair --text '```json{"answer":"42","confidence":0.9,}```' --schema examples/answer_schema.json
python -m structured_output_repair --input examples/model_output.txt --schema examples/answer_schema.json --json
```

The CLI exits with status `0` when the cleaned output satisfies the schema and `1` when parsing or validation still fails.

## Python API

```python
from structured_output_repair import inspect_output

schema = {"type": "object", "required": ["answer"], "properties": {"answer": {"type": "string"}}}
report = inspect_output('```json{"answer":"ready",}```', schema)
print(report.cleaned_value)  # {'answer': 'ready'}
print(report.ok)             # True
```

Repair is deliberately conservative: it only removes Markdown wrappers and trailing commas. It does not invent keys, infer values, or silently coerce types.
