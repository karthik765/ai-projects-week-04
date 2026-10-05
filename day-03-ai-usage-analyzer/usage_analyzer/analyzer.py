from collections import defaultdict
from statistics import mean

from .models import AnalysisReport, ModelSummary, UsageRecord
from .pricing import estimate_cost


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int((len(ordered) - 1) * fraction + 0.5)))
    return ordered[index]


def analyze(records: list[UsageRecord], budget: float | None = None) -> AnalysisReport:
    groups: dict[str, list[UsageRecord]] = defaultdict(list)
    for record in records:
        groups[record.model].append(record)
    summaries = tuple(_summarize(model, values) for model, values in sorted(groups.items()))
    latencies = [item.latency_ms for item in records]
    successful = sum(item.status in {"success", "ok", "completed"} for item in records)
    cost = sum(estimate_cost(item.model, item.input_tokens, item.output_tokens) for item in records)
    warnings: list[str] = []
    if records and successful / len(records) < 0.95:
        warnings.append("failure rate is above 5%; inspect failed requests")
    if budget is not None and cost > budget:
        warnings.append(f"estimated cost ${cost:.4f} exceeds budget ${budget:.4f}")
    return AnalysisReport(
        requests=len(records), successful=successful, failed=len(records) - successful,
        input_tokens=sum(item.input_tokens for item in records),
        output_tokens=sum(item.output_tokens for item in records),
        estimated_cost=cost, average_latency_ms=mean(latencies) if latencies else 0.0,
        p95_latency_ms=percentile(latencies, 0.95), by_model=summaries,
        warnings=tuple(warnings),
    )


def _summarize(model: str, records: list[UsageRecord]) -> ModelSummary:
    latencies = [item.latency_ms for item in records]
    successful = sum(item.status in {"success", "ok", "completed"} for item in records)
    return ModelSummary(
        model=model, requests=len(records), successful=successful, failed=len(records) - successful,
        input_tokens=sum(item.input_tokens for item in records),
        output_tokens=sum(item.output_tokens for item in records),
        estimated_cost=sum(estimate_cost(item.model, item.input_tokens, item.output_tokens) for item in records),
        average_latency_ms=mean(latencies), p95_latency_ms=percentile(latencies, 0.95),
    )
