import http.client
import inspect
import json
import warnings
from typing import (
    Any,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
    cast,
)

try:
    from typing import _GenericAlias  # noqa
except ImportError:
    from types import GenericAlias as _GenericAlias

from lilya._internal._path import clean_path
from lilya.contrib.security.base import (
    SecurityScheme as SecurityScheme,
)
from lilya.middleware import DefineMiddleware
from lilya.routing import BasePath
from lilya.status import HTTP_422_UNPROCESSABLE_ENTITY
from lilya.transformers import TRANSFORMER_TYPES
from orjson import loads
from pydantic import AnyUrl
from pydantic.fields import FieldInfo
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue
from typing_extensions import Literal

from ravyn.openapi.constants import METHODS_WITH_BODY, REF_PREFIX, REF_TEMPLATE
from ravyn.openapi.models import (
    Contact,
    Info,
    License,
    OpenAPI,
    Operation,
    Parameter,
)
from ravyn.openapi.responses import create_internal_response
from ravyn.openapi.utils import (
    STATUS_CODE_RANGES,
    VALIDATION_ERROR_DEFINITION,
    VALIDATION_ERROR_RESPONSE_DEFINITION,
    dict_update,
    get_definitions,
    get_schema_from_model_field,
    is_status_code_allowed,
)
from ravyn.params import Param
from ravyn.routing import gateways, router
from ravyn.routing.core._internal import (
    convert_annotation_to_pydantic_model,
)
from ravyn.security.oauth2.oauth import SecurityBase
from ravyn.typing import Undefined
from ravyn.utils.dependencies import is_base_requires
from ravyn.utils.enums import MediaType
from ravyn.utils.helpers import is_class_and_subclass, is_union

ADDITIONAL_TYPES = ["bool", "list", "dict"]
TRANSFORMER_TYPES_KEYS = list(TRANSFORMER_TYPES.keys())
TRANSFORMER_TYPES_KEYS += ADDITIONAL_TYPES


def get_flat_params(route: Union[router.HTTPHandler, Any], body_fields: list[str]) -> list[Any]:
    """
    Gets all the neded params of the request and route.
    """
    path_params = [param.field_info for param in route.transformer.get_path_params()]
    cookie_params = [param.field_info for param in route.transformer.get_cookie_params()]
    header_params = [param.field_info for param in route.transformer.get_header_params()]

    handler_dependencies = set(route.get_dependencies().keys())
    body_encoder_fields = route.body_encoder_fields
    handler_query_params = [
        param
        for param in route.transformer.get_query_params()
        if param.field_alias not in body_encoder_fields
        and not param.is_security
        and param.field_alias not in handler_dependencies
    ]

    query_params = []
    for param in handler_query_params:
        is_union_or_optional = is_union(param.field_info.annotation)

        if param.field_info.alias in body_fields:
            continue

        if param.is_security or param.is_requires_dependency:
            continue

        # Making sure all the optional and union types are included
        if is_union_or_optional:
            if not is_base_requires(param.field_info.default):
                query_params.append(param.field_info)

        else:
            if isinstance(param.field_info.annotation, _GenericAlias) and not is_base_requires(
                param.field_info.default
            ):
                query_params.append(param.field_info)
            elif (
                param.field_info.annotation.__class__.__name__ in TRANSFORMER_TYPES_KEYS
                or param.field_info.annotation.__name__ in TRANSFORMER_TYPES_KEYS
            ):
                if not is_base_requires(param.field_info.default):
                    query_params.append(param.field_info)

    return path_params + query_params + cookie_params + header_params


def get_openapi_security_schemes(schemes: Any) -> Tuple[dict, list]:
    """
    Builds the security schemas for OpenAPI.
    """
    security_definitions = {}
    operation_security = []

    for security_requirement in schemes:
        if inspect.isclass(security_requirement):
            security_requirement = security_requirement()

        if not isinstance(
            security_requirement,
            (SecurityScheme, SecurityBase),
        ):
            raise ValueError(
                "Security schemes must subclass from `ravyn.openapi.models.SecurityScheme`"
            )

        security_definition = security_requirement.model_dump(by_alias=True, exclude_none=True)
        security_name = security_requirement.scheme_name
        security_definitions[security_name] = security_definition
        operation_security.append({security_name: security_requirement})
    return security_definitions, operation_security


def get_fields_from_routes(
    routes: Sequence[BasePath], request_fields: Optional[list[FieldInfo]] = None
) -> list[FieldInfo]:
    """Extracts the fields from the given routes of Ravyn"""
    body_fields: list[FieldInfo] = []
    response_from_routes: list[FieldInfo] = []

    if not request_fields:
        request_fields = []

    for route in routes:
        if getattr(route, "include_in_schema", None) and isinstance(route, router.Include):
            request_fields.extend(get_fields_from_routes(route.routes, request_fields))
            continue

        if getattr(route, "include_in_schema", None) and isinstance(
            route, (gateways.Gateway, gateways.WebhookGateway)
        ):
            handler = cast(router.HTTPHandler, route.handler)

            if handler.data_field:
                body_fields.append(handler.data_field)

            if handler.response_models:
                for _, response in handler.response_models.items():
                    response_from_routes.append(response)

            # Get the params from the transformer
            body_fields_names = [field.alias for field in body_fields]
            params = get_flat_params(handler, body_fields_names)
            if params:
                request_fields.extend(params)

    return list(body_fields + response_from_routes + request_fields)


def get_openapi_operation(
    *, route: gateways.Gateway, operation_ids: Set[str]
) -> dict[str, Any]:  # pragma: no cover
    operation = Operation()
    operation.tags = route.handler.get_handler_tags()

    # Handle the routing summary
    if route.handler.summary:
        operation.summary = route.handler.summary
    else:
        name = route.handler.name or route.name
        operation.summary = name.replace("_", " ").replace("-", " ").title()

    # Handle the handler description
    if route.handler.description:
        operation.description = route.handler.description
    else:
        operation.description = inspect.cleandoc(route.handler.fn.__doc__ or "")

    operation_id = getattr(route, "operation_id", None) or route.handler.operation_id

    if operation_id in operation_ids:
        message = (
            f"Duplicate Operation ID {operation_id} for function " + f"{route.handler.fn.__name__}"
        )
        file_name = getattr(route.handler, "__globals__", {}).get("__file__")
        if file_name:
            message += f" at {file_name}"
        warnings.warn(message, stacklevel=1)
    operation_ids.add(operation_id)

    operation.operationId = operation_id
    if route.deprecated:
        operation.deprecated = route.deprecated
    elif route.handler.deprecated:
        operation.deprecated = route.handler.deprecated

    operation_schema = operation.model_dump(exclude_none=True, by_alias=True)
    return operation_schema


def get_openapi_operation_parameters(
    *,
    all_route_params: Sequence[FieldInfo],
    field_mapping: dict[Tuple[FieldInfo, Literal["validation", "serialization"]], JsonSchemaValue],
) -> list[dict[str, Any]]:  # pragma: no cover
    parameters = []
    for param in all_route_params:
        field_info = cast(Param, param)
        if not field_info.include_in_schema:
            continue

        param_schema = get_schema_from_model_field(
            field=param,
            field_mapping=field_mapping,
        )
        if field_info.default is not None and field_info.default is not Undefined:
            param_schema["default"] = field_info.default

        parameter = Parameter(  # type: ignore
            name=param.alias,
            param_in=field_info.in_.value,
            required=param.is_required(),
            schema=param_schema,  # type: ignore
        )
        if field_info.description:
            parameter.description = field_info.description
        if field_info.examples is not None:
            parameter.example = json.dumps(field_info.examples)
        if field_info.deprecated:
            parameter.deprecated = field_info.deprecated  # type: ignore
        parameters.append(parameter.model_dump(by_alias=True, exclude_none=True))
    return parameters


def get_openapi_operation_request_body(
    *,
    data_field: Optional[FieldInfo],
    field_mapping: dict[Tuple[FieldInfo, Literal["validation", "serialization"]], JsonSchemaValue],
) -> Optional[dict[str, Any]]:  # pragma: no cover
    if not data_field:
        return None  # type: ignore

    assert isinstance(data_field, FieldInfo), "The 'data' needs to be a FieldInfo"
    schema = get_schema_from_model_field(field=data_field, field_mapping=field_mapping)

    field_info = data_field
    extra = cast("dict[str, Any]", data_field.json_schema_extra)
    request_media_type = extra.get("media_type").value
    required = field_info.is_required()

    request_data_oai: dict[str, Any] = {}
    if required:
        request_data_oai["required"] = required

    request_media_content: dict[str, Any] = {"schema": schema}
    if field_info.examples is not None:
        request_media_content["example"] = json.dumps(field_info.examples)
    request_data_oai["content"] = {request_media_type: request_media_content}
    return request_data_oai


def get_openapi_path(
    *,
    route: Union[gateways.Gateway, gateways.WebhookGateway],
    operation_ids: Set[str],
    field_mapping: dict[Tuple[FieldInfo, Literal["validation", "serialization"]], JsonSchemaValue],
    is_deprecated: bool = False,
) -> Tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:  # pragma: no cover
    path: dict[str, Any] = {}
    security_schemes: dict[str, Any] = {}
    definitions: dict[str, Any] = {}

    assert route.handler.methods is not None, "Methods must be a list"
    route_response_media_type: str = None
    handler: router.HTTPHandler = cast("router.HTTPHandler", route.handler)

    if not handler.response_class:
        internal_response = create_internal_response(handler)
        route_response_media_type = internal_response.media_type
    else:
        assert handler.response_class.media_type is not None, (
            "`media_type` is required in the response class."
        )
        route_response_media_type = handler.response_class.media_type

    # If routes do not want to be included in the schema generation
    if not route.include_in_schema or not handler.include_in_schema:
        return path, security_schemes, definitions

    # For each method
    for method in route.handler.methods:
        operation = get_openapi_operation(route=route, operation_ids=operation_ids)  # type: ignore
        # If the parent if marked as deprecated, it takes precedence
        if is_deprecated or route.deprecated:
            operation["deprecated"] = is_deprecated if is_deprecated else route.deprecated

        parameters: list[dict[str, Any]] = []
        security_definitions, operation_security = get_openapi_security_schemes(
            handler.get_security_schemes()
        )

        if operation_security:
            operation.setdefault("security", []).extend(operation_security)

        if security_definitions:
            security_schemes.update(security_definitions)

        body_fields = []
        if handler.data_field:
            body_fields.append(handler.data_field)

        body_fields_names = [field.alias for field in body_fields]
        all_route_params = get_flat_params(handler, body_fields_names)
        operation_parameters = get_openapi_operation_parameters(
            all_route_params=all_route_params,
            field_mapping=field_mapping,
        )
        parameters.extend(operation_parameters)

        if parameters:
            all_parameters = {(param["in"], param["name"]): param for param in parameters}
            required_parameters = {
                (param["in"], param["name"]): param
                for param in parameters
                if param.get("required")
            }
            all_parameters.update(required_parameters)
            operation["parameters"] = list(all_parameters.values())

        if method in METHODS_WITH_BODY:
            request_data_oai = get_openapi_operation_request_body(
                data_field=handler.data_field,
                field_mapping=field_mapping,
            )
            if request_data_oai:
                operation["requestBody"] = request_data_oai

        status_code = str(handler.status_code)
        operation.setdefault("responses", {}).setdefault(status_code, {})["description"] = (
            handler.response_description
        )

        # Media type
        if route_response_media_type and is_status_code_allowed(handler.status_code):
            response_schema = (
                {"type": "string"} if handler.status_code not in handler.responses else {}
            )

            operation.setdefault("responses", {}).setdefault(status_code, {}).setdefault(
                "content", {}
            ).setdefault(route_response_media_type, {})["schema"] = response_schema

        # Additional responses
        if handler.response_models:
            operation_responses = operation.setdefault("responses", {})
            for additional_status_code, _ in handler.response_models.items():
                process_response = handler.responses[additional_status_code].model_copy()
                status_code_key = str(additional_status_code).upper()

                if status_code_key == "DEFAULT":
                    status_code_key = "default"

                openapi_response = operation_responses.setdefault(status_code_key, {})

                field = handler.response_models.get(additional_status_code)
                additional_field_schema: Optional[dict[str, Any]] = None
                model_schema = process_response.model_json_schema()

                if field:
                    additional_field_schema = get_schema_from_model_field(
                        field=field, field_mapping=field_mapping
                    )
                    media_type = route_response_media_type or MediaType.JSON.value
                    additional_schema = (
                        model_schema.setdefault("content", {})
                        .setdefault(media_type, {})
                        .setdefault("schema", {})
                    )
                    dict_update(additional_schema, additional_field_schema)

                # status
                status_text = (
                    process_response.status_text
                    or STATUS_CODE_RANGES.get(str(additional_status_code).upper())
                    or http.client.responses.get(int(additional_status_code))
                )
                description = (
                    process_response.description
                    or openapi_response.get("description")
                    or status_text
                    or "Additional Response"
                )
                dict_update(openapi_response, model_schema)
                openapi_response["description"] = description

        # Convert to automatic response detection if none is provided by the
        # responses of the handler.
        if handler.handler_signature.return_annotation:
            response_schema = convert_annotation_to_pydantic_model(
                handler.handler_signature.return_annotation
            )

            if (
                hasattr(response_schema, "model_json_schema")
                and status_code not in handler.responses
                and int(status_code) not in handler.responses
            ):
                operation["responses"][status_code]["content"][route_response_media_type][
                    "schema"
                ] = response_schema.model_json_schema()

        http422 = str(HTTP_422_UNPROCESSABLE_ENTITY)
        if (all_route_params or handler.data_field) and not any(
            status in operation["responses"] for status in {http422, "4XX", "default"}
        ):
            operation["responses"][http422] = {
                "description": "Validation Error",
                "content": {
                    "application/json": {"schema": {"$ref": REF_PREFIX + "HTTPValidationError"}}
                },
            }
            if "ValidationError" not in definitions:
                definitions.update(
                    {
                        "ValidationError": VALIDATION_ERROR_DEFINITION,
                        "HTTPValidationError": VALIDATION_ERROR_RESPONSE_DEFINITION,
                    }
                )
        path[method.lower()] = operation
    return path, security_schemes, definitions


def should_include_in_schema(route: router.Include) -> bool:
    """
    Checks if a specifc object should be included in the schema
    """
    from ravyn import ChildRavyn, Ravyn

    if not route.include_in_schema:
        return False

    if not is_middleware_app(route):
        return True

    if (
        isinstance(route.app, (Ravyn, ChildRavyn))
        or (
            is_class_and_subclass(route.app, Ravyn) or is_class_and_subclass(route.app, ChildRavyn)
        )
    ) and not getattr(route.app, "enable_openapi", False):
        return False
    if (
        isinstance(route.app, (Ravyn, ChildRavyn))
        or (
            is_class_and_subclass(route.app, Ravyn) or is_class_and_subclass(route.app, ChildRavyn)
        )
    ) and not getattr(route.app, "include_in_schema", False):
        return False

    return True


def is_middleware_app(route: router.Include) -> bool:
    """
    Checks if the app is a middleware or a router
    """
    from ravyn import MiddlewareProtocol

    return bool(isinstance(route.app, (DefineMiddleware, MiddlewareProtocol)))


def get_openapi(
    *,
    app: Any,
    title: str,
    version: str,
    openapi_version: str = "3.1.0",
    summary: Optional[str] = None,
    description: Optional[str] = None,
    routes: Sequence[BasePath],
    tags: Optional[list[str]] = None,
    servers: Optional[list[dict[str, Union[str, Any]]]] = None,
    terms_of_service: Optional[Union[str, AnyUrl]] = None,
    contact: Optional[Contact] = None,
    license: Optional[License] = None,
    webhooks: Optional[Sequence[BasePath]] = None,
) -> dict[str, Any]:  # pragma: no cover
    """
    Builds the whole OpenAPI route structure and object
    """
    from ravyn import ChildRavyn, Ravyn

    info = Info(title=title, version=version)
    if summary:
        info.summary = summary
    if description:
        info.description = description
    if terms_of_service:
        info.termsOfService = terms_of_service  # type: ignore
    if contact:
        info.contact = contact
    if license:
        info.license = license

    output: dict[str, Any] = {
        "openapi": openapi_version,
        "info": info.model_dump(exclude_none=True, by_alias=True),
    }

    if servers:
        output["servers"] = servers

    components: dict[str, dict[str, Any]] = {}
    paths: dict[str, dict[str, Any]] = {}
    webhooks_paths: dict[str, dict[str, Any]] = {}
    operation_ids: Set[str] = set()
    all_fields = get_fields_from_routes(list(routes or []) + list(webhooks or []))
    schema_generator = GenerateJsonSchema(ref_template=REF_TEMPLATE)
    field_mapping, definitions = get_definitions(
        fields=all_fields,
        schema_generator=schema_generator,
    )

    # Iterate through the routes
    def iterate_routes(
        app: Any,
        routes: Sequence[BasePath],
        definitions: Any = None,
        components: Any = None,
        prefix: Optional[str] = "",
        is_webhook: bool = False,
        is_deprecated: bool = False,
    ) -> Tuple[dict[str, Any], dict[str, Any]]:
        for route in routes:
            if app.router.deprecated:
                is_deprecated = True

            if isinstance(route, router.Include):
                if hasattr(route, "app"):
                    if not should_include_in_schema(route):
                        continue

                # For external middlewares
                if getattr(route.app, "routes", None) is None and not is_middleware_app(route):
                    continue

                if hasattr(route, "app") and isinstance(route.app, (Ravyn, ChildRavyn)):
                    route_path = clean_path(prefix + route.path)

                    definitions, components = iterate_routes(
                        app,
                        route.app.routes,
                        definitions,
                        components,
                        prefix=route_path,
                        is_deprecated=is_deprecated if is_deprecated else route.deprecated,
                    )
                else:
                    route_path = clean_path(prefix + route.path)
                    definitions, components = iterate_routes(
                        app,
                        route.routes,
                        definitions,
                        components,
                        prefix=route_path,
                        is_deprecated=is_deprecated if is_deprecated else route.deprecated,
                    )
                continue

            if isinstance(route, (gateways.Gateway, gateways.WebhookGateway)):
                result = get_openapi_path(
                    route=route,
                    operation_ids=operation_ids,
                    field_mapping=field_mapping,
                    is_deprecated=is_deprecated,
                )
                if result:
                    path, security_schemes, path_definitions = result
                    if path:
                        if is_webhook:
                            webhooks_paths.setdefault(route.path, {}).update(path)
                        else:
                            route_path = clean_path(prefix + route.path_format)
                            paths.setdefault(route_path, {}).update(path)
                    if security_schemes:
                        components.setdefault("securitySchemes", {}).update(security_schemes)
                    if path_definitions:
                        definitions.update(path_definitions)

        return definitions, components

    definitions, components = iterate_routes(
        app=app, routes=routes, definitions=definitions, components=components
    )

    if webhooks:
        definitions, components = iterate_routes(
            app=app,
            routes=webhooks,
            definitions=definitions,
            components=components,
            is_webhook=True,
        )

    if definitions:
        components["schemas"] = {k: definitions[k] for k in sorted(definitions)}
    if components:
        output["components"] = components
    output["paths"] = paths
    if webhooks_paths:
        output["webhooks"] = webhooks_paths
    if tags:
        output["tags"] = tags

    openapi = OpenAPI(**output)
    model_dump = openapi.model_dump_json(by_alias=True, exclude_none=True)
    return cast(dict[str, Any], loads(model_dump))
