import argparse
import json

from .analyzer import analyze
from .loader import load_records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize AI usage JSONL logs.")
    parser.add_argument("input", help="path to a JSONL usage log")
    parser.add_argument("--budget", type=float, help="optional estimated-cost budget in USD")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = analyze(load_records(args.input), budget=args.budget)
    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2))
        return
    print(f"Requests: {report.requests} ({report.successful} successful, {report.failed} failed)")
    print(f"Tokens: {report.input_tokens:,} input / {report.output_tokens:,} output")
    print(f"Estimated cost: ${report.estimated_cost:.4f}")
    print(f"Latency: {report.average_latency_ms:.1f} ms average / {report.p95_latency_ms:.1f} ms p95")
    for item in report.by_model:
        print(f"- {item.model}: {item.requests} requests, ${item.estimated_cost:.4f}, {item.average_latency_ms:.1f} ms avg")
    for warning in report.warnings:
        print(f"WARNING: {warning}")
