from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, cast
from uuid import UUID

import msgspec  # type: ignore[import-not-found]
import pytest  # type: ignore[import-not-found]
from pydantic import BaseModel

from ravyn.encoders import (
    ENCODER_TYPES,
    Encoder,
    MsgSpecEncoder,
    PydanticEncoder,
    is_body_encoder,
    register_ravyn_encoder,
)
from ravyn.exceptions import ImproperlyConfigured


class Address(msgspec.Struct):
    city: str


class Payload(msgspec.Struct):
    identifier: UUID
    created_at: datetime
    amount: Decimal
    address: Address
    optional_note: str | None = None


class PydanticPayload(BaseModel):
    identifier: UUID
    created_at: datetime
    amount: Decimal
    nested: dict[str, Any]
    optional_note: str | None = None


class PydanticFallbackModel(BaseModel):
    value: object


def test_msgspec_encoder_serializes_struct_with_special_types() -> None:
    encoder = MsgSpecEncoder()
    payload = Payload(
        identifier=UUID("12345678-1234-5678-1234-567812345678"),
        created_at=datetime(2026, 3, 11, 10, 30, tzinfo=timezone.utc),
        amount=Decimal("19.99"),
        address=Address(city="Lisbon"),
    )

    serialized = encoder.serialize(payload)

    assert serialized["identifier"] == "12345678-1234-5678-1234-567812345678"
    assert serialized["created_at"] == "2026-03-11T10:30:00Z"
    assert serialized["amount"] == "19.99"
    assert serialized["address"] == {"city": "Lisbon"}
    assert serialized["optional_note"] is None


def test_msgspec_encoder_serializes_none_as_none() -> None:
    assert MsgSpecEncoder().serialize(None) is None


def test_pydantic_encoder_serializes_json_compatible_primitives() -> None:
    encoder = PydanticEncoder()
    payload = PydanticPayload(
        identifier=UUID("12345678-1234-5678-1234-567812345678"),
        created_at=datetime(2026, 3, 11, 10, 30, tzinfo=timezone.utc),
        amount=Decimal("19.99"),
        nested={"level": {"active": True}},
    )

    serialized = encoder.serialize(payload)

    assert serialized["identifier"] == "12345678-1234-5678-1234-567812345678"
    assert serialized["created_at"] == "2026-03-11T10:30:00Z"
    assert serialized["amount"] == "19.99"
    assert serialized["nested"] == {"level": {"active": True}}
    assert serialized["optional_note"] is None


def test_pydantic_encoder_falls_back_to_python_mode_on_serialization_error() -> None:
    model = PydanticFallbackModel(value=object())

    serialized = PydanticEncoder().serialize(model)

    assert isinstance(serialized["value"], object)
    assert serialized["value"] is model.value


def test_register_ravyn_encoder_registers_only_once() -> None:
    class DummyEncoder(Encoder[Any]):
        def is_type(self, value: Any) -> bool:
            return False

        def serialize(self, obj: Any) -> Any:
            return obj

        def encode(self, annotation: Any, value: Any) -> Any:
            return value

    original = ENCODER_TYPES.get()
    assert original is not None
    ENCODER_TYPES.set(deque(original))
    try:
        register_ravyn_encoder(DummyEncoder)
        first_registry = ENCODER_TYPES.get()
        assert first_registry is not None
        first_registration = list(first_registry)
        register_ravyn_encoder(DummyEncoder)
        second_registry = ENCODER_TYPES.get()
        assert second_registry is not None
        second_registration = list(second_registry)

        assert sum(type(enc).__name__ == "DummyEncoder" for enc in first_registration) == 1
        assert sum(type(enc).__name__ == "DummyEncoder" for enc in second_registration) == 1
    finally:
        ENCODER_TYPES.set(deque(original))


def test_register_ravyn_encoder_rejects_non_encoder_types() -> None:
    with pytest.raises(ImproperlyConfigured):
        register_ravyn_encoder(cast(Any, str))


def test_is_body_encoder_detects_registered_types_and_unions() -> None:
    original = ENCODER_TYPES.get()
    assert original is not None
    ENCODER_TYPES.set(deque([MsgSpecEncoder(), PydanticEncoder()]))
    try:
        assert is_body_encoder(Payload)
        assert is_body_encoder(PydanticPayload)
        assert is_body_encoder(Payload | int)
        assert is_body_encoder(PydanticPayload | None)
        assert not is_body_encoder(int | str)
    finally:
        ENCODER_TYPES.set(deque(original))
