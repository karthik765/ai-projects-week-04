from typing import Any

from .models import Issue


def validate(value: Any, schema: dict[str, Any], path: str = "$",) -> list[Issue]:
    issues: list[Issue] = []
    expected = schema.get("type")
    if expected and not _matches_type(value, expected):
        return [Issue(path, "type", f"expected {expected}, got {_type_name(value)}")]
    if "enum" in schema and value not in schema["enum"]:
        issues.append(Issue(path, "enum", f"value must be one of {schema['enum']}"))
    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                issues.append(Issue(f"{path}.{key}", "required", "required property is missing"))
        for key, child_schema in schema.get("properties", {}).items():
            if key in value:
                issues.extend(validate(value[key], child_schema, f"{path}.{key}"))
    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            issues.extend(validate(item, schema["items"], f"{path}[{index}]"))
    if isinstance(value, (str, list, dict)):
        size = len(value)
        if "minLength" in schema and size < schema["minLength"]:
            issues.append(Issue(path, "minLength", f"length must be at least {schema['minLength']}"))
        if "maxLength" in schema and size > schema["maxLength"]:
            issues.append(Issue(path, "maxLength", f"length must be at most {schema['maxLength']}"))
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            issues.append(Issue(path, "minimum", f"value must be at least {schema['minimum']}"))
        if "maximum" in schema and value > schema["maximum"]:
            issues.append(Issue(path, "maximum", f"value must be at most {schema['maximum']}"))
    return issues


def _matches_type(value: Any, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected, False)


def _type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    return type(value).__name__
