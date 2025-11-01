import inspect
import sys
from functools import cached_property
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast, get_args, get_origin

from lilya.datastructures import DataUpload
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

try:
    from typing import _GenericAlias  # noqa
except ImportError:
    from types import GenericAlias as _GenericAlias

from ravyn.core.datastructures import UploadFile
from ravyn.encoders import LILYA_ENCODER_TYPES, is_body_encoder
from ravyn.openapi.params import ResponseParam
from ravyn.params import Body
from ravyn.utils.constants import DATA, PAYLOAD
from ravyn.utils.enums import EncodingType
from ravyn.utils.helpers import is_class_and_subclass, is_union

if TYPE_CHECKING:
    from ravyn.routing.router import HTTPHandler, WebhookHandler

T = TypeVar("T")

DEFAULT_CONTAINERS = (list, set, tuple, dict, frozenset)


def create_field_model(*, field: FieldInfo, name: str, model_name: str) -> type[BaseModel]:
    """
    Creates a pydantic model for a specific field
    """
    params = {name.lower(): (field.annotation, field)}
    data_field_model: type[BaseModel] = create_model(  # type: ignore[call-overload]
        model_name, __config__={"arbitrary_types_allowed": True}, **params
    )
    return data_field_model


def get_base_annotations(base_annotation: Any, is_class: bool = False) -> dict[str, Any]:
    """
    Returns the annotations of the base class.

    Args:
        base_annotation (Any): The base class.
        is_class (bool): Whether the base class is a class or not.
    Returns:
        dict[str, Any]: The annotations of the base class.
    """
    base_annotations: dict[str, Any] = {}
    if not is_class:
        bases = base_annotation.__bases__
    else:
        bases = base_annotation.__class__.__bases__

    for base in bases:
        base_annotations.update(**get_base_annotations(base))
        if hasattr(base, "__annotations__"):
            for name, annotation in base.__annotations__.items():
                base_annotations[name] = annotation
    return base_annotations


def default_typed_container(type_: type[T]) -> type[Any]:
    """
    Adapts non-generic built-in container types (like list, dict, tuple)
    into their generic, subscripted forms (like list[Any], dict[str, Any]).

    This adaptation is often necessary for compatibility when frameworks (e.g., Pydantic)
    introspect type hints in Python versions (like <= 3.8) that do not automatically
    recognize bare containers as generic types.

    The function provides a minimal generic structure, defaulting list/set/tuple contents
    to `Any`, and uses `dict[str, Any]` to reflect the common pattern of string keys
    in JSON/OpenAPI schemas.

    Args:
        tp: The bare built-in type object (e.g., `list`, `dict`, `set`).

    Returns:
        The subscripted (generic) version of the type (e.g., `list[Any]`), or the
        original type if it is not a recognized container.
    """
    # minimal: only list is needed by your failing tests
    if type_ is list:
        return list[Any]
    if type_ is set:
        return set[Any]
    if type_ is tuple:
        # Note: Ellipsis is used to denote a tuple of indefinite length and homogeneous type (Any)
        return tuple[Any, ...]
    if type_ is dict:
        # OpenAPI keys are typically strings (JSON object); this keeps pydantic happy when needed
        return dict[str, Any]
    if type_ is frozenset:
        return frozenset[Any]
    return type_


def convert_annotation_to_pydantic_model(field_annotation: Any) -> Any:
    """
    Converts a Python type annotation (particularly custom types and Encoders)
    into a Pydantic BaseModel representation for OpenAPI documentation purposes.

    The function ensures that complex annotations, unions, and custom framework types
    are correctly represented as schema objects that OpenAPI can understand, without
    altering the core validation logic used elsewhere in the framework.

    Args:
        field_annotation: The type hint to be converted (e.g., `list[str]`, `UserEncoder`, `Union[str, int]`).

    Returns:
        The Pydantic BaseModel or generic type representing the annotation for
        OpenAPI schema generation.
    """
    origin: Any = get_origin(field_annotation)
    args: tuple[Any, ...] = get_args(field_annotation)

    # Handle Union Types (including Optional[T])
    if is_union(origin):
        # Recursively convert all members of the union
        new_args: tuple[Any, ...] = tuple(convert_annotation_to_pydantic_model(a) for a in args)
        return Union[new_args]

    # Handle Generic Containers (List[T], Dict[K, V], etc.)
    if origin is not None:
        # Recursively convert type arguments (e.g., convert T in List[T])
        new_args = tuple(convert_annotation_to_pydantic_model(a) for a in args)
        try:
            # Reconstruct the generic type (e.g., list[str] -> list[converted_str_type])
            return origin[new_args]
        except TypeError:
            # If the origin is not subscriptable at runtime (e.g., custom generic types), leave it.
            return field_annotation

    # Handle Bare Built-in Containers (list, dict, set, etc.)
    if field_annotation in DEFAULT_CONTAINERS:
        # Convert bare types (like 'list') to generic types (like 'list[Any]')
        return default_typed_container(field_annotation)

    # Handle Existing Pydantic Models
    if isinstance(field_annotation, type) and issubclass(field_annotation, BaseModel):
        return field_annotation

    # Handle Framework Encoder Types (The main conversion logic)
    # Iterate through registered encoder types to find a match
    for enc in LILYA_ENCODER_TYPES.get():
        if sys.version_info <= (3, 12):
            # For backwards compatibility
            if not hasattr(field_annotation, "__annotations__"):
                return field_annotation

        is_structure: bool = hasattr(enc, "is_type_structure") and enc.is_type_structure(
            field_annotation
        )
        is_instance: bool = hasattr(enc, "is_type") and enc.is_type(field_annotation)

        if is_structure or is_instance:
            # If the encoder is a generic alias (e.g., a parameterized encoder class)
            if isinstance(field_annotation, _GenericAlias):
                # Recursively convert the generic arguments
                annotations: tuple[Any, ...] = tuple(
                    convert_annotation_to_pydantic_model(arg) for arg in args
                )
                field_annotation.__args__ = annotations
                return cast(BaseModel, field_annotation)

            field_definitions: dict[str, Any] = {}

            # Get annotations from the base classes and the class itself
            base_annotations: dict[str, Any] = {
                **get_base_annotations(field_annotation, is_class=True)
            }
            field_annotations: dict[str, Any] = {
                **base_annotations,
                **field_annotation.__annotations__,
            }

            # Map collected annotations to Pydantic field definitions
            for name, annotation in field_annotations.items():
                field_definitions[name] = (annotation, ...)

            # Determine the name for the new dynamic model
            if inspect.isclass(field_annotation):
                name = field_annotation.__name__
            else:
                name = field_annotation.__class__.__name__

            # Dynamically create a Pydantic model for OpenAPI representation
            return cast(
                BaseModel,
                create_model(  # noqa
                    name,
                    __config__={"arbitrary_types_allowed": True},
                    **field_definitions,
                ),
            )

    # Fallback: Return original annotation
    return field_annotation


def handle_upload_files(data: Any, body: Body) -> Body:
    """
    Handles the creation of the body field for the upload files.
    """
    # For Uploads and Multi Part
    args = get_args(body.annotation)
    name = "File" if not args else "Files"

    model = create_field_model(field=body, name=name, model_name=body.title)
    data_field = Body(annotation=model, title=body.title)

    for key, _ in data._attributes_set.items():
        if key != "annotation":
            setattr(data_field, key, getattr(body, key, None))
    return data_field


def get_upload_body(handler: Union["HTTPHandler"]) -> Any:
    """
    This function repeats some of the steps but covers all the
    cases for simple use cases.
    """
    for name, _ in handler.signature_model.model_fields.items():
        data = handler.signature_model.model_fields[name]

        if not isinstance(data, Body):
            body = Body(alias="body")
            for key, _ in data._attributes_set.items():
                setattr(body, key, getattr(data, key, None))
        else:
            body = data

        # Check the annotation type
        body.annotation = convert_annotation_to_pydantic_model(body.annotation)

        if not body.title:
            body.title = f"Body_{handler.operation_id}"

        # For everything else that is not MULTI_PART
        extra = cast("dict[str, Any]", body.json_schema_extra) or {}
        if extra.get(
            "media_type", EncodingType.JSON
        ) != EncodingType.MULTI_PART and not is_class_and_subclass(
            body.annotation, (UploadFile, DataUpload)
        ):
            continue

        # For Uploads and Multi Part
        data_field = handle_upload_files(data, body)
        return data_field


def get_original_data_field(
    handler: Union["HTTPHandler", "WebhookHandler", Any],
) -> Any:  # pragma: no cover
    """
    The field used for the payload body.

    This builds a model for the required data field. Validates the type of encoding
    being passed and builds a model if a datastructure is evaluated.
    """
    model_fields = handler.signature_model.model_fields
    if DATA in model_fields or PAYLOAD in model_fields:
        data_or_payload = DATA if DATA in model_fields else PAYLOAD
        data = model_fields[data_or_payload]

        if not isinstance(data, Body):
            body = Body(alias="body")
            for key, _ in data._attributes_set.items():
                setattr(body, key, getattr(data, key, None))
        else:
            body = data

        # Check the annotation type
        body.annotation = convert_annotation_to_pydantic_model(body.annotation)

        if not body.title:
            body.title = f"Body_{handler.operation_id}"

        # For everything else that is not MULTI_PART
        extra = cast("dict[str, Any]", body.json_schema_extra) or {}
        if extra.get("media_type", EncodingType.JSON) != EncodingType.MULTI_PART:
            return body

        # For Uploads and Multi Part
        data_field = handle_upload_files(data, body)
        return data_field


def get_complex_data_field(
    handler: Union["HTTPHandler", "WebhookHandler", Any], fields: dict[str, FieldInfo]
) -> Any:  # pragma: no cover
    """
    The field used for the payload body.

    This builds a model for the required data field. Validates the type of encoding
    being passed and builds a model if a datastructure is evaluated.
    """
    body_fields_set = set()
    body_fields: dict[str, FieldInfo] = {}

    for name, field in fields.items():
        if name in body_fields_set:
            continue

        body_fields_set.add(name)
        body_fields[name] = field

    # Set the field definitions
    field_definitions = {}
    for name, param in body_fields.items():
        param.annotation = convert_annotation_to_pydantic_model(param.annotation)
        field_definitions[name] = param.annotation, ...

    # Create the model from the field definitions
    model = create_model(  # type: ignore
        "DataField", __config__={"arbitrary_types_allowed": True}, **field_definitions
    )
    # Create the body field
    body = Body(annotation=model, title=f"Body_{handler.operation_id}")

    # Check the annotation type
    if not body.title:
        body.title = f"Body_{handler.operation_id}"
    return body


def get_data_field(handler: Union["HTTPHandler", "WebhookHandler", Any]) -> Any:
    """
    Retrieves the data field from the given handler.

    Args:
        handler (Union[HTTPHandler, WebhookHandler, Any]): The handler object.

    Returns:
        Any: The data field.

    Raises:
        None

    This function checks if the handler has any body encoder fields. If there are less than 2 body encoder fields,
    it calls the get_original_data_field function. Otherwise, it calls the get_complex_data_field function.

    One the steps is to make sure backwards compatibility and this means to make sure previous
    versions of Ravyn are supported the way they are supposed to.

    The other thing is to make sure we extract any value from the signature of the handler and
    match against any encoder, custom or default, and isolate them as body fields and then extract
    the values that are not in the dependencies since those are not considered part of the body
    but as dependency itself.

    If the body fields are less than 1 and using the reserved `data` or `payload` then it will
    default to the normal Ravyn processing, otherwise it will use the complex approach of
    designing the OpenAPI body.
    """
    # If there are no body fields, we simply return the original
    # default Ravyn body parsing
    is_data_or_payload = not {DATA, PAYLOAD}.isdisjoint(
        handler.signature_model.model_fields.keys()
    )
    if not handler.body_encoder_fields and is_data_or_payload:
        return get_original_data_field(handler)

    if not handler.body_encoder_fields:
        return get_upload_body(handler)

    if len(handler.body_encoder_fields) < 2 and is_data_or_payload:
        return get_original_data_field(handler)
    return get_complex_data_field(handler, fields=handler.body_encoder_fields)


class OpenAPIFieldInfoMixin:
    """
    Used for validating model fields necessary for the
    OpenAPI parsing only.

    Don't use this anywhere else.
    """

    @cached_property
    def body_encoder_fields(self) -> dict[str, FieldInfo]:
        """
        The fields that are body encoders.

        This is used for OpenAPI representation purposes only.
        """
        # Making sure the dependencies are not met as body fields for OpenAPI representation
        handler_dependencies = set(self.get_dependencies().keys())
        security_dependencies = set(self.transformer.get_security_params().keys())

        # Getting everything else that is not considered a dependency
        body_encoder_fields = {
            name: field
            for name, field in self.signature_model.model_fields.items()
            if is_body_encoder(field.annotation)
            and name not in handler_dependencies
            and name not in security_dependencies
        }
        return body_encoder_fields

    @cached_property
    def response_models(self) -> dict[int, Any]:
        """
        The models converted into pydantic fields with the model used for OpenAPI.

        The response models can be a list representation or a single object representation.
        If another type of object is passed through the `model`, an Assertation error is raised.
        """
        responses: dict[int, ResponseParam] = {}
        if self.responses:
            for status_code, response in self.responses.items():
                model = response.model[0] if isinstance(response.model, list) else response.model

                annotation = (
                    list[model] if isinstance(response.model, list) else model  # type: ignore
                )

                responses[status_code] = ResponseParam(
                    annotation=convert_annotation_to_pydantic_model(annotation),
                    description=response.description,
                    alias=model.__name__,
                )
        return responses

    @cached_property
    def data_field(self) -> Any:  # pragma: no cover
        """
        The field used for the payload body.

        This builds a model for the required data field. Validates the type of encoding
        being passed and builds a model if a datastructure is evaluated.
        """
        data_field = get_data_field(self)
        return data_field
