"""Serialization helpers for JSON, dict, and YAML."""

from typing import Any, cast

import yaml
from pydantic import BaseModel


def to_dict(model: BaseModel) -> dict[str, Any]:
    """Serialize a Pydantic model to a dictionary."""
    return model.model_dump(mode="python")


def from_dict[T: BaseModel](cls: type[T], data: dict[str, Any]) -> T:
    """Deserialize a dictionary to a Pydantic model."""
    return cls.model_validate(data)


def to_json(model: BaseModel, **kwargs: Any) -> str:
    """Serialize a Pydantic model to a JSON string."""
    return model.model_dump_json(**kwargs)


def from_json[T: BaseModel](cls: type[T], data: str, **kwargs: Any) -> T:
    """Deserialize a JSON string to a Pydantic model."""
    return cls.model_validate_json(data, **kwargs)


def to_yaml(model: BaseModel, **kwargs: Any) -> str:
    """Serialize a Pydantic model to a YAML string (safe, JSON-compatible)."""
    return cast("str", yaml.safe_dump(model.model_dump(mode="json"), **kwargs))


def from_yaml[T: BaseModel](cls: type[T], data: str, **kwargs: Any) -> T:
    """Deserialize a YAML string to a Pydantic model."""
    parsed = yaml.safe_load(data)
    return cls.model_validate(parsed, **kwargs)
