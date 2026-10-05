from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class UsageRecord:
    """One normalized request observation."""

    timestamp: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    status: str = "success"
    request_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True)
class ModelSummary:
    model: str
    requests: int
    successful: int
    failed: int
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    average_latency_ms: float
    p95_latency_ms: float


@dataclass(frozen=True)
class AnalysisReport:
    requests: int
    successful: int
    failed: int
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    average_latency_ms: float
    p95_latency_ms: float
    by_model: tuple[ModelSummary, ...]
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "requests": self.requests,
            "successful": self.successful,
            "failed": self.failed,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "estimated_cost": round(self.estimated_cost, 6),
            "average_latency_ms": round(self.average_latency_ms, 2),
            "p95_latency_ms": round(self.p95_latency_ms, 2),
            "by_model": [
                {
                    "model": item.model,
                    "requests": item.requests,
                    "successful": item.successful,
                    "failed": item.failed,
                    "input_tokens": item.input_tokens,
                    "output_tokens": item.output_tokens,
                    "estimated_cost": round(item.estimated_cost, 6),
                    "average_latency_ms": round(item.average_latency_ms, 2),
                    "p95_latency_ms": round(item.p95_latency_ms, 2),
                }
                for item in self.by_model
            ],
            "warnings": list(self.warnings),
        }
