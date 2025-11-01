from typing import Any, Union

from pydantic import TypeAdapter
from pydantic.fields import FieldInfo
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue
from typing_extensions import Literal

from ravyn.openapi.validation import (
    validation_error_definition,
    validation_error_response_definition,
)

VALIDATION_ERROR_DEFINITION: dict[str, Any] = validation_error_definition.model_dump(
    exclude_none=True
)
"""Pre-generated JSON Schema definition for a Pydantic validation error detail."""

VALIDATION_ERROR_RESPONSE_DEFINITION: dict[str, Any] = (
    validation_error_response_definition.model_dump(exclude_none=True)
)
"""Pre-generated OpenAPI response object definition for a validation error."""

STATUS_CODE_RANGES: dict[str, str] = {
    "1XX": "Information",
    "2XX": "Success",
    "3XX": "Redirection",
    "4XX": "Client Error",
    "5XX": "Server Error",
    "DEFAULT": "Default Response",
}
"""Mapping of OpenAPI status code ranges (e.g., '2XX') to their descriptive names."""

ALLOWED_STATUS_CODE: set[str] = {
    "default",
    "1XX",
    "2XX",
    "3XX",
    "4XX",
    "5XX",
}
"""Set of valid symbolic status codes/ranges recognized by the OpenAPI specification."""

REF_TEMPLATE: str = "#/components/schemas/{name}"
"""The JSON Reference template used to point to schema definitions in the components section."""


def get_definitions(
    *,
    fields: list[FieldInfo],
    schema_generator: GenerateJsonSchema,
) -> tuple[
    dict[tuple[FieldInfo, Literal["validation", "serialization"]], JsonSchemaValue],
    dict[str, dict[str, Any]],
]:
    """
    Generates the necessary JSON Schema definitions and field mappings for a list of Pydantic fields.

    This function prepares the schemas of complex types and external models defined in the fields
    to be placed under the global `#/components/schemas` section.

    Args:
        fields: A list of Pydantic `FieldInfo` objects whose schemas are needed.
        schema_generator: The `GenerateJsonSchema` instance used for schema generation.

    Returns:
        A tuple containing:
        1. A mapping from `(FieldInfo, 'validation')` to the root JSON Schema for that field.
        2. A dictionary of generated definitions for complex types.
    """
    # Prepare inputs for the schema generator
    inputs = [(field, "validation", TypeAdapter(field.annotation).core_schema) for field in fields]

    # Generate definitions and field mappings
    field_mapping, definitions = schema_generator.generate_definitions(
        inputs=inputs  # type: ignore[arg-type]
    )

    return field_mapping, definitions  # type: ignore[return-value]


def get_schema_from_model_field(
    *,
    field: FieldInfo,
    field_mapping: dict[tuple[FieldInfo, Literal["validation", "serialization"]], JsonSchemaValue],
) -> dict[str, Any]:
    """
    Retrieves the JSON Schema for a specific field from the generated field mapping.

    If the schema is not a reference (meaning it's not a complex type placed in definitions),
    this function ensures the 'title' is correctly set based on the field's metadata.

    Args:
        field: The `FieldInfo` object for which to retrieve the schema.
        field_mapping: The dictionary mapping fields to their root JSON Schema.

    Returns:
        The final JSON Schema dictionary for the field.
    """
    json_schema: dict[str, Any] = field_mapping[(field, "validation")]

    # If the schema is not a reference, ensure it has a proper title
    if "$ref" not in json_schema:
        # Use field title or generate one from the alias
        json_schema["title"] = field.title or field.alias.title().replace("_", " ")

    return json_schema


def is_status_code_allowed(status_code: Union[int, str, None]) -> bool:
    """
    Checks if a given status code is valid and relevant for OpenAPI response documentation.

    It allows generic ranges ('2XX', 'default') and specific integer codes,
    but excludes non-informative successful responses (204, 304) and pre-success
    informative codes (less than 200).

    Args:
        status_code: The status code as an integer, string (e.g., '404'), or symbolic range.

    Returns:
        True if the status code is allowed for documentation, False otherwise.
    """
    if status_code is None:
        return True

    if status_code in ALLOWED_STATUS_CODE:
        return True

    # Check for integer codes (must be >= 200 and not 204/304)
    try:
        current_status_code: int = int(status_code)
    except ValueError:
        return False

    # True if status code is >= 200 AND not one of the excluded codes
    return not (current_status_code < 200 or current_status_code in {204, 304})


def dict_update(
    original_dict: dict[Any, Any], update_dict: dict[Any, Any]
) -> None:  # pragma: no cover
    """
    Performs a deep, in-place merge of `update_dict` into `original_dict`.

    - Merges nested dictionaries recursively.
    - Appends items for nested lists (concatenation).
    - Overwrites scalar values.

    Args:
        original_dict: The dictionary to be updated (modified in place).
        update_dict: The dictionary containing the updates.
    """
    for key, value in update_dict.items():
        if (
            key in original_dict
            and isinstance(original_dict[key], dict)
            and isinstance(value, dict)
        ):
            # Recursively merge nested dictionaries
            dict_update(original_dict[key], value)
        elif (
            key in original_dict
            and isinstance(original_dict[key], list)
            and isinstance(update_dict[key], list)
        ):
            # Concatenate lists
            original_dict[key] = original_dict[key] + update_dict[key]
        else:
            # Overwrite all other types (scalars, non-matching containers)
            original_dict[key] = value
