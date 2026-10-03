from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Issue:
    path: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class RepairReport:
    ok: bool
    cleaned_text: str
    cleaned_value: Any = None
    repairs: list[str] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "cleaned_text": self.cleaned_text,
            "cleaned_value": self.cleaned_value,
            "repairs": self.repairs,
            "issues": [issue.to_dict() for issue in self.issues],
        }
