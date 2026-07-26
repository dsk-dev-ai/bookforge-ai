from __future__ import annotations

from typing import Any

from pydantic import ValidationError


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""

    def __init__(self, message: str, errors: list[dict[str, Any]] | None = None) -> None:
        self.errors = errors or []
        super().__init__(message)


def validate_settings(settings: Any) -> list[dict[str, Any]]:
    """Validate a settings instance and return a list of error details.

    Args:
        settings: A Pydantic BaseSettings instance to validate.

    Returns:
        A list of error dicts, each containing ``loc``, ``msg``, and ``type``.
        Returns an empty list if validation succeeds.
    """
    try:
        settings.model_validate(settings.model_dump())
        return []
    except ValidationError as e:
        return [
            {
                "loc": list(err.get("loc", [])),
                "msg": err.get("msg", str(err)),
                "type": err.get("type", "validation_error"),
            }
            for err in e.errors()
        ]


def assert_valid_config(settings: Any) -> None:
    """Validate settings and raise ``ConfigValidationError`` on failure."""
    errors = validate_settings(settings)
    if errors:
        detail = "; ".join(f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in errors)
        raise ConfigValidationError(f"Configuration validation failed: {detail}", errors=errors)
