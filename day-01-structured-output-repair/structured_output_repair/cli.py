import argparse
import json
import sys
from pathlib import Path

from .analyzer import inspect_output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Clean and validate model-generated JSON.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", help="raw model output")
    source.add_argument("--input", type=Path, help="file containing raw model output")
    parser.add_argument("--schema", type=Path, required=True, help="compact JSON schema file")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit a JSON report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    raw = args.text if args.text is not None else args.input.read_text(encoding="utf-8")
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    report = inspect_output(raw, schema)
    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print("PASS" if report.ok else "FAIL")
        for repair in report.repairs:
            print(f"Repair: {repair}")
        if report.ok:
            print(json.dumps(report.cleaned_value, indent=2))
        else:
            for issue in report.issues:
                print(f"{issue.path} [{issue.code}] {issue.message}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
