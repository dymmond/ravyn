from __future__ import annotations

from inspect import isclass
from typing import Any, Generic, TypeVar, get_args

import msgspec
from lilya._internal._encoders import json_encoder as json_encoder  # noqa
from lilya._utils import is_class_and_subclass  # noqa
from lilya.encoders import (
    ENCODER_TYPES as LILYA_ENCODER_TYPES,  # noqa
    Encoder as LilyaEncoder,  # noqa
    EncoderProtocol,
    register_encoder as register_encoder,  # noqa
)
from msgspec import Struct
from pydantic import BaseModel
from pydantic_core import PydanticSerializationError

from ravyn.exceptions import ImproperlyConfigured
from ravyn.utils.helpers import is_union

T = TypeVar("T")

# it is a TransparentCage now
ENCODER_TYPES = LILYA_ENCODER_TYPES


class Encoder(EncoderProtocol, Generic[T]):
    """
    Base class for Ravyn encoders. All encoders must inherit from this class
    and implement the following methods:
    - is_type: Check if the value is an instance of a given type.
    - is_type_structure: Prevent Lilya from picking it up for apply_structure.
    - serialize: Transform a data structure into a serializable object.
    - encode: Transform the kwargs into a structure.
    """

    def is_type(self, value: Any) -> bool:
        """
        Check if the value is an instance of a given type.

        Args:
            value (Any): The value to check.

        Returns:
            bool: True if the value is an instance of the type, False otherwise.
        """
        raise NotImplementedError("All Ravyn encoders must implement is_type() method.")

    def is_type_structure(self, value: Any) -> bool:
        """
        Prevent Lilya from picking it up for apply_structure.

        Args:
            value (Any): The value to check.

        Returns:
            bool: False, indicating it should not be picked up for apply_structure.
        """
        return False

    def serialize(self, obj: Any) -> Any:
        """
        Transform a data structure into a serializable object.

        Args:
            obj (Any): The object to serialize.

        Returns:
            Any: The serialized object.
        """
        raise NotImplementedError("All Ravyn encoders must implement serialize() method.")

    def encode(self, annotation: Any, value: Any) -> Any:
        """
        Transform the kwargs into a structure.

        Args:
            annotation (Any): The annotation type.
            value (Any): The value to encode.

        Returns:
            Any: The encoded value.
        """
        raise NotImplementedError("All Ravyn encoders must implement encode() method.")


def register_ravyn_encoder(encoder: Encoder | type[Encoder]) -> None:
    """
    Register an Ravyn encoder into available Lilya encoders.

    Args:
        encoder (Encoder | type[Encoder]): The encoder to register.

    Raises:
        ImproperlyConfigured: If the encoder is not a subclass of Encoder.
    """
    encoder_type = encoder if isclass(encoder) else type(encoder)
    if not isinstance(encoder, Encoder) and not is_class_and_subclass(encoder, Encoder):
        raise ImproperlyConfigured(f"{encoder_type} must be a subclass of Encoder")

    encoder_types = {_encoder.__class__.__name__ for _encoder in LILYA_ENCODER_TYPES.get()}
    if encoder_type.__name__ not in encoder_types:
        register_encoder(encoder)


class MsgSpecEncoder(Encoder):
    """
    Encoder for msgspec.Struct objects.
    """

    def is_type(self, value: Any) -> bool:
        """
        Check if the value is an instance of msgspec.Struct.

        Args:
            value (Any): The value to check.

        Returns:
            bool: True if the value is an instance of msgspec.Struct, False otherwise.
        """
        return isinstance(value, Struct) or is_class_and_subclass(value, Struct)

    def serialize(self, obj: Any) -> Any:
        """
        Serialize a msgspec.Struct object.

        Args:
            obj (Any): The object to serialize.

        Returns:
            Any: The serialized object.
        """
        return msgspec.to_builtins(obj)

    def encode(self, annotation: Any, value: Any) -> Any:
        """
        Encode a value into a msgspec.Struct.

        Args:
            annotation (Any): The annotation type.
            value (Any): The value to encode.

        Returns:
            Any: The encoded value.
        """
        return msgspec.json.decode(msgspec.json.encode(value), type=annotation)


class PydanticEncoder(Encoder):
    """
    Encoder for Pydantic BaseModel objects.
    """

    def is_type(self, value: Any) -> bool:
        """
        Check if the value is an instance of Pydantic BaseModel.

        Args:
            value (Any): The value to check.

        Returns:
            bool: True if the value is an instance of Pydantic BaseModel, False otherwise.
        """
        return isinstance(value, BaseModel) or is_class_and_subclass(value, BaseModel)

    def serialize(self, obj: BaseModel) -> dict[str, Any]:
        """
        Serialize a Pydantic BaseModel object.

        Args:
            obj (BaseModel): The object to serialize.

        Returns:
            dict[str, Any]: The serialized object as a dictionary.
        """
        try:
            return obj.model_dump(mode="json")
        except PydanticSerializationError:
            return obj.model_dump()

    def encode(self, annotation: Any, value: Any) -> Any:
        """
        Encode a value into a Pydantic BaseModel.

        Args:
            annotation (Any): The annotation type.
            value (Any): The value to encode.

        Returns:
            Any: The encoded value.
        """
        if isinstance(value, BaseModel) or is_class_and_subclass(value, BaseModel):
            return value
        return annotation(**value)


def is_body_encoder(value: Any) -> bool:
    """
    Check if the value is a body encoder.

    Args:
        value (Any): The value to check.

    Returns:
        bool: True if the value is a body encoder, False otherwise.
    """
    encoder_types = LILYA_ENCODER_TYPES.get()
    if not is_union(value):
        return any(encoder.is_type(value) for encoder in encoder_types)

    union_arguments = get_args(value)
    if not union_arguments:
        return False
    return any(
        any(encoder.is_type(argument) for encoder in encoder_types) for argument in union_arguments
    )
