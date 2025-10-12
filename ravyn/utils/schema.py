from decimal import Decimal
from typing import Any, Type, TypeVar, Union, cast, get_args

try:
    from typing import _GenericAlias  # noqa
except ImportError:
    from types import GenericAlias as _GenericAlias

from pydantic.fields import FieldInfo
from pydantic.json_schema import SkipJsonSchema

T = TypeVar("T", int, float, Decimal)


def is_field_optional(field: "FieldInfo") -> bool:
    """
    Returns bool True or False for the optional model field.
    """
    allow_none = getattr(field, "allow_none", True)
    return not field.is_required() and not is_any_type(field=field) and allow_none


def is_any_type(field: "FieldInfo") -> bool:
    """
    Checks if the field is of type Any.
    """
    name = cast("Any", getattr(field.annotation, "_name", None))
    return (name is not None and "Any" in name) or field.annotation is Any


def should_skip_json_schema(field_info: Union[FieldInfo, Any]) -> FieldInfo:
    """
    Checks if the schema generation for the parameters should be skipped.
    This is applied for complex fields in query params.

    Example:
        1. Union[dict[str, str], None]
        2. Optional[dict[str, str]]
        3. Union[list[str], None]
        4. Optional[list[str]]
    """
    union_args = get_args(field_info.annotation)

    if not any(
        isinstance(annotation, _GenericAlias) for annotation in union_args
    ) or not isinstance(field_info.annotation, _GenericAlias):
        return field_info

    arguments: list[Type[Any]] = []

    for argument in union_args:
        if argument is not type(None):
            arguments.append(argument)
        else:
            arguments.append(SkipJsonSchema[None])

    arguments = tuple(arguments)  # type: ignore
    field_info.annotation = Union[arguments]
    return field_info


def extract_arguments(
    param: Union[Any, None] = None, argument_list: Union[list[Any], None] = None
) -> list[Type[type]]:
    """
    Recursively extracts unique types from a parameter's type annotation.

    Args:
        param (Union[Parameter, None], optional): The parameter with type annotation to extract from.
        argument_list (Union[list[Any], None], optional): The list of arguments extracted so far.

    Returns:
        list[Type[type]]: A list of unique types extracted from the parameter's type annotation.
    """
    arguments: list[Any] = list(argument_list) if argument_list is not None else []
    args = get_args(param)

    for arg in args:
        if isinstance(arg, _GenericAlias):
            arguments.extend(extract_arguments(param=arg, argument_list=arguments))
        else:
            if arg not in arguments:
                arguments.append(arg)
    return arguments
