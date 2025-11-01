import http.client
import inspect
import json
import warnings
from typing import (
    Any,
    Sequence,
    Set,
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

from ravyn.core.protocols.middleware import MiddlewareProtocol
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

SecurityRequirement = dict[str, Sequence[str]]


ADDITIONAL_TYPES: list[str] = ["bool", "list", "dict"]
TRANSFORMER_TYPES_KEYS: list[str] = list(TRANSFORMER_TYPES.keys())
TRANSFORMER_TYPES_KEYS += ADDITIONAL_TYPES


def get_flat_params(route: router.HTTPHandler | Any, body_fields: list[str]) -> list[Any]:
    """
    Extracts and flattens all relevant parameters (Path, Query, Header, Cookie)
    from a route handler's signature.

    It filters out parameters that are dependencies, security requirements, or those
    expected to be in the request body.

    Args:
        route: The `HTTPHandler` instance containing the route and its transformer.
        body_fields: A list of field aliases expected to be in the request body (and should be excluded from parameters).

    Returns:
        A list of `FieldInfo` objects representing all OpenAPI parameters.
    """
    path_params: list[FieldInfo] = [
        param.field_info for param in route.transformer.get_path_params()
    ]
    cookie_params: list[FieldInfo] = [
        param.field_info for param in route.transformer.get_cookie_params()
    ]
    header_params: list[FieldInfo] = [
        param.field_info for param in route.transformer.get_header_params()
    ]

    handler_dependencies: set[str] = set(route.get_dependencies().keys())
    body_encoder_fields: dict[str, Any] = route.body_encoder_fields

    # Filter query parameters
    handler_query_params = [
        param
        for param in route.transformer.get_query_params()
        if param.field_alias not in body_encoder_fields
        and not param.is_security
        and param.field_alias not in handler_dependencies
    ]

    query_params: list[FieldInfo] = []
    for param in handler_query_params:
        is_union_or_optional: bool = is_union(param.field_info.annotation)

        if param.field_info.alias in body_fields:
            continue

        if param.is_security or param.is_requires_dependency:
            continue

        # Logic to include parameters based on type and whether they are explicit requirements
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


def get_openapi_security_schemes(schemes: Any) -> tuple[dict[str, Any], list[SecurityRequirement]]:
    """
    Builds the security schemes components and the operational security requirements
    for OpenAPI based on the configured security objects.

    Args:
        schemes: A sequence of security scheme instances or classes (subclasses of SecurityScheme/SecurityBase).

    Returns:
        A tuple containing:
        1. Security Definitions (for `components/securitySchemes`).
        2. Operation Security List (for the `security` field in an operation object).
    """
    security_definitions: dict[str, Any] = {}
    operation_security: list[SecurityRequirement | Any] = []

    for security_requirement in schemes:
        if inspect.isclass(security_requirement):
            security_requirement = security_requirement()

        if not isinstance(
            security_requirement,
            (SecurityScheme, SecurityBase),
        ):
            raise ValueError(
                "Security schemes must subclass from `ravyn.openapi.models.SecurityScheme` or `ravyn.security.oauth2.oauth.SecurityBase`"
            )

        security_definition: dict[str, Any] = security_requirement.model_dump(
            by_alias=True, exclude_none=True
        )
        security_name: str = security_requirement.scheme_name

        security_definitions[security_name] = security_definition
        # Note: Appending the requirement object itself, assuming it maps to scopes later if needed.
        operation_security.append({security_name: security_requirement})

    return security_definitions, operation_security


def get_fields_from_routes(
    routes: Sequence[BasePath], request_fields: list[FieldInfo] | None = None
) -> list[FieldInfo]:
    """Extracts all unique Pydantic fields (for request body, response models, and parameters)
    across a sequence of routes, handling recursive route includes.

    Args:
        routes: A sequence of `BasePath` objects (routes, includes, gateways).
        request_fields: Initial list of fields to extend (used for recursion).

    Returns:
        A list of `FieldInfo` objects.
    """
    body_fields: list[FieldInfo] = []
    response_from_routes: list[FieldInfo] = []

    if not request_fields:
        request_fields = []

    for route in routes:
        # Handle recursive includes
        if getattr(route, "include_in_schema", None) and isinstance(route, router.Include):
            request_fields.extend(get_fields_from_routes(route.routes, request_fields))
            continue

        # Handle Gateway routes
        if getattr(route, "include_in_schema", None) and isinstance(
            route, (gateways.Gateway, gateways.WebhookGateway)
        ):
            handler: router.HTTPHandler = cast(router.HTTPHandler, route.handler)

            # Extract request body field
            if handler.data_field:
                body_fields.append(handler.data_field)

            # Extract response model fields
            if handler.response_models:
                for _, response in handler.response_models.items():
                    response_from_routes.append(response)

            # Extract parameter fields
            body_fields_names: list[str] = [field.alias for field in body_fields]
            params: list[FieldInfo] = get_flat_params(handler, body_fields_names)
            if params:
                request_fields.extend(params)

    # Return unique combination of all gathered fields
    return list(body_fields + response_from_routes + request_fields)


def get_openapi_operation(
    *, route: gateways.Gateway, operation_ids: Set[str]
) -> dict[str, Any]:  # pragma: no cover
    """
    Builds the base OpenAPI Operation Object for a given route method.

    Handles setting tags, summary, description, and ensures the operation ID is unique.

    Args:
        route: The `Gateway` instance.
        operation_ids: A set of already used operation IDs (modified in place).

    Returns:
        The OpenAPI Operation Object dictionary structure.
    """
    operation: Operation = Operation()
    operation.tags = route.handler.get_handler_tags()

    # Handle the routing summary
    if route.handler.summary:
        operation.summary = route.handler.summary
    else:
        name: str = route.handler.name or route.name
        operation.summary = name.replace("_", " ").replace("-", " ").title()

    # Handle the handler description
    if route.handler.description:
        operation.description = route.handler.description
    else:
        operation.description = inspect.cleandoc(route.handler.fn.__doc__ or "")

    operation_id: str | None = getattr(route, "operation_id", None) or route.handler.operation_id

    # Check and warn on duplicate operation IDs
    if operation_id in operation_ids:
        message: str = (
            f"Duplicate Operation ID {operation_id} for function " + f"{route.handler.fn.__name__}"
        )
        file_name: str | None = getattr(route.handler, "__globals__", {}).get("__file__")
        if file_name:
            message += f" at {file_name}"
        warnings.warn(message, stacklevel=1)
    operation_ids.add(operation_id)

    operation.operationId = operation_id

    # Handle deprecation status
    if route.deprecated:
        operation.deprecated = route.deprecated
    elif route.handler.deprecated:
        operation.deprecated = route.handler.deprecated

    operation_schema: dict[str, Any] = operation.model_dump(exclude_none=True, by_alias=True)
    return operation_schema


def get_openapi_operation_parameters(
    *,
    all_route_params: Sequence[FieldInfo],
    field_mapping: dict[tuple[FieldInfo, Literal["validation", "serialization"]], JsonSchemaValue],
) -> list[dict[str, Any]]:  # pragma: no cover
    """
    Converts a sequence of `FieldInfo` objects into OpenAPI Parameter objects.

    Args:
        all_route_params: Sequence of `FieldInfo` objects derived from route parameters.
        field_mapping: Mapping of fields to their root JSON Schema.

    Returns:
        A list of OpenAPI Parameter Object dictionaries.
    """
    parameters: list[dict[str, Any]] = []
    for param in all_route_params:
        field_info: Param = cast(Param, param)
        if not field_info.include_in_schema:
            continue

        param_schema: dict[str, Any] = get_schema_from_model_field(
            field=param,
            field_mapping=field_mapping,
        )

        # Set default value if present and not Undefined
        if field_info.default is not None and field_info.default is not Undefined:
            param_schema["default"] = field_info.default

        parameter: Parameter = Parameter(  # type: ignore[call-arg]
            name=param.alias,
            param_in=field_info.in_.value,
            required=param.is_required(),
            schema=param_schema,  # type: ignore[arg-type]
        )

        # Add description, examples, and deprecation status
        if field_info.description:
            parameter.description = field_info.description
        if field_info.examples is not None:
            # Note: Examples are dumped to JSON string as per original logic
            parameter.example = json.dumps(field_info.examples)
        if field_info.deprecated:
            parameter.deprecated = bool(field_info.deprecated)

        parameters.append(parameter.model_dump(by_alias=True, exclude_none=True))

    return parameters


def get_openapi_operation_request_body(
    *,
    data_field: FieldInfo | None = None,
    field_mapping: dict[tuple[FieldInfo, Literal["validation", "serialization"]], JsonSchemaValue],
) -> dict[str, Any] | None:  # pragma: no cover
    """
    Builds the OpenAPI Request Body Object for a route method.

    Args:
        data_field: The `FieldInfo` object representing the request body payload.
        field_mapping: Mapping of fields to their root JSON Schema.

    Returns:
        The OpenAPI Request Body Object dictionary, or None if no body field is present.
    """
    if data_field is None:
        return None

    assert isinstance(data_field, FieldInfo), "The 'data' needs to be a FieldInfo"

    schema: dict[str, Any] = get_schema_from_model_field(
        field=data_field, field_mapping=field_mapping
    )

    field_info: FieldInfo = data_field
    extra: dict[str, Any] = cast("dict[str, Any]", data_field.json_schema_extra)

    # Determine the media type from the field's extra schema
    request_media_type: str = extra.get("media_type").value
    required: bool = field_info.is_required()

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
    route: gateways.Gateway | gateways.WebhookGateway,
    operation_ids: Set[str],
    field_mapping: dict[tuple[FieldInfo, Literal["validation", "serialization"]], JsonSchemaValue],
    is_deprecated: bool = False,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]] | None:  # pragma: no cover
    """
    Generates the OpenAPI Path Item Object for all HTTP methods supported by a single route.

    Args:
        route: The Gateway or WebhookGateway route object.
        operation_ids: Set of existing operation IDs (updated in place).
        field_mapping: Mapping of fields to their root JSON Schema.
        is_deprecated: Boolean indicating if the route inherited a deprecated status from an include.

    Returns:
        A tuple containing: (Path Item Dict, Security Schemes Dict, Component Definitions Dict), or None if the route is excluded.
    """
    path: dict[str, Any] = {}
    security_schemes: dict[str, Any] = {}
    definitions: dict[str, Any] = {}

    assert route.handler.methods is not None, "Methods must be a list"
    route_response_media_type: str | None = None
    handler: router.HTTPHandler = cast("router.HTTPHandler", route.handler)

    # Determine the primary response media type
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
        return None

    # For each method (GET, POST, etc.)
    for method in route.handler.methods:
        operation: dict[str, Any] = get_openapi_operation(route=route, operation_ids=operation_ids)  # type: ignore[arg-type]

        # Apply deprecation status
        if is_deprecated or route.deprecated:
            operation["deprecated"] = is_deprecated if is_deprecated else route.deprecated

        parameters: list[dict[str, Any]] = []
        security_definitions, operation_security = get_openapi_security_schemes(
            handler.get_security_schemes()
        )

        # Merge security requirements
        if operation_security:
            operation.setdefault("security", []).extend(operation_security)

        if security_definitions:
            security_schemes.update(security_definitions)

        # Get and process parameters
        body_fields: list[FieldInfo] = []
        if handler.data_field:
            body_fields.append(handler.data_field)

        body_fields_names: list[str] = [field.alias for field in body_fields]
        all_route_params: list[FieldInfo] = get_flat_params(handler, body_fields_names)

        operation_parameters: list[dict[str, Any]] = get_openapi_operation_parameters(
            all_route_params=all_route_params,
            field_mapping=field_mapping,
        )
        parameters.extend(operation_parameters)

        if parameters:
            # Deduplicate parameters by (in, name) and ensure required ones override
            all_parameters: dict[tuple[str, str], dict[str, Any]] = {
                (param["in"], param["name"]): param for param in parameters
            }
            required_parameters: dict[tuple[str, str], dict[str, Any]] = {
                (param["in"], param["name"]): param
                for param in parameters
                if param.get("required")
            }
            all_parameters.update(required_parameters)
            operation["parameters"] = list(all_parameters.values())

        # Process Request Body
        if method in METHODS_WITH_BODY:
            request_data_oai: dict[str, Any] | None = get_openapi_operation_request_body(
                data_field=handler.data_field,
                field_mapping=field_mapping,
            )
            if request_data_oai:
                operation["requestBody"] = request_data_oai

        # Process Responses
        status_code: str = str(handler.status_code)

        # Set description for primary response
        operation.setdefault("responses", {}).setdefault(status_code, {})["description"] = (
            handler.response_description
        )

        # Set schema for primary response media type
        if route_response_media_type and is_status_code_allowed(handler.status_code):
            response_schema: dict[str, Any] = (
                {"type": "string"} if handler.status_code not in handler.responses else {}
            )

            operation.setdefault("responses", {}).setdefault(status_code, {}).setdefault(
                "content", {}
            ).setdefault(route_response_media_type, {})["schema"] = response_schema

        # Process Additional Responses (handler.response_models)
        if handler.response_models:
            operation_responses: dict[str, Any] = operation.setdefault("responses", {})
            for additional_status_code, _ in handler.response_models.items():
                process_response: Any = handler.responses[additional_status_code].model_copy()
                status_code_key: str = str(additional_status_code).upper()

                if status_code_key == "DEFAULT":
                    status_code_key = "default"

                openapi_response: dict[str, Any] = operation_responses.setdefault(
                    status_code_key, {}
                )

                field: FieldInfo | None = handler.response_models.get(additional_status_code)
                additional_field_schema: dict[str, Any] | None = None
                model_schema: dict[str, Any] = process_response.model_json_schema()

                if field:
                    additional_field_schema = get_schema_from_model_field(
                        field=field, field_mapping=field_mapping
                    )
                    media_type: str = route_response_media_type or MediaType.JSON.value

                    # Update the schema within the content section
                    additional_schema: dict[str, Any] = (
                        model_schema.setdefault("content", {})
                        .setdefault(media_type, {})
                        .setdefault("schema", {})
                    )
                    dict_update(additional_schema, additional_field_schema)

                # Set description for the response
                status_text: str = (
                    process_response.status_text
                    or STATUS_CODE_RANGES.get(str(additional_status_code).upper())
                    or http.client.responses.get(int(additional_status_code), "")
                )
                description: str = (
                    process_response.description
                    or openapi_response.get("description")
                    or status_text
                    or "Additional Response"
                )
                dict_update(openapi_response, model_schema)
                openapi_response["description"] = description

        # Convert return annotation to response schema if not explicitly provided
        if handler.handler_signature.return_annotation:
            response_schema = convert_annotation_to_pydantic_model(
                handler.handler_signature.return_annotation
            )

            if (
                hasattr(response_schema, "model_json_schema")
                and status_code not in handler.responses
                and int(status_code) not in handler.responses
            ):
                # Update the primary response schema
                operation["responses"][status_code]["content"][route_response_media_type][
                    "schema"
                ] = response_schema.model_json_schema()

        # Add 422 Unprocessable Entity response if request body or parameters exist
        http422: str = str(HTTP_422_UNPROCESSABLE_ENTITY)
        if (all_route_params or handler.data_field) and not any(
            status in operation["responses"] for status in {http422, "4XX", "default"}
        ):
            operation["responses"][http422] = {
                "description": "Validation Error",
                "content": {
                    "application/json": {"schema": {"$ref": REF_PREFIX + "HTTPValidationError"}}
                },
            }
            # Ensure ValidationError definitions are present in components/schemas
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
    Checks if a specific included application or router should be included in the OpenAPI schema.

    Args:
        route: The `Include` router object.

    Returns:
        True if the route should be included, False otherwise (e.g., if explicitly disabled or it's a middleware app).
    """
    from ravyn import ChildRavyn, Ravyn

    if not route.include_in_schema:
        return False

    if not isinstance(route.app, (DefineMiddleware, MiddlewareProtocol)):
        return True

    # Logic to handle nested Ravyn/ChildRavyn apps that might disable OpenAPI generation
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
    Checks if the application object within the Include route is a middleware or a router.

    Args:
        route: The `Include` router object.

    Returns:
        True if the included app is a middleware definition, False if it's a standard router/application.
    """

    return bool(isinstance(route.app, (DefineMiddleware, MiddlewareProtocol)))


def get_openapi(
    *,
    app: Any,
    title: str,
    version: str,
    openapi_version: str = "3.1.0",
    summary: str | None = None,
    description: str | None = None,
    routes: Sequence[BasePath],
    tags: list[str] | None = None,
    servers: list[dict[str, str | Any]] | None = None,
    terms_of_service: str | AnyUrl | None = None,
    contact: Contact | None = None,
    license: License | None = None,
    webhooks: Sequence[BasePath] | None = None,
) -> dict[str, Any]:  # pragma: no cover
    """
    The main function responsible for building the complete OpenAPI specification object
    for the application.

    It performs recursive route traversal, schema generation, and final object assembly.

    Args:
        app: The root application instance.
        title: The title of the API.
        version: The version of the API.
        openapi_version: The version of the OpenAPI specification (default: "3.1.0").
        summary: A short summary of the API.
        description: A detailed description of the API.
        routes: The sequence of HTTP routes.
        tags: A list of global tags.
        servers: A list of server objects.
        terms_of_service: Link to the terms of service.
        contact: Contact information object.
        license: License information object.
        webhooks: A sequence of Webhook routes (optional, for OpenAPI 3.1).

    Returns:
        The final OpenAPI specification dictionary.
    """
    from ravyn import ChildRavyn, Ravyn

    # 1. Build Info Object
    info: Info = Info(title=title, version=version)
    if summary:
        info.summary = summary
    if description:
        info.description = description
    if terms_of_service:
        info.termsOfService = terms_of_service
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

    # 2. Extract All Fields for Schema Generation
    all_fields: list[FieldInfo] = get_fields_from_routes(list(routes or []) + list(webhooks or []))
    schema_generator: GenerateJsonSchema = GenerateJsonSchema(ref_template=REF_TEMPLATE)

    # Generate definitions once for all fields
    field_mapping: dict[tuple[FieldInfo, Literal["validation", "serialization"]], JsonSchemaValue]
    definitions: dict[str, dict[str, Any]]

    field_mapping, definitions = get_definitions(
        fields=all_fields,
        schema_generator=schema_generator,
    )

    # 3. Recursive Route Traversal and Path Generation
    def iterate_routes(
        app: Any,
        routes: Sequence[BasePath],
        definitions: dict[str, dict[str, Any]],
        components: dict[str, dict[str, Any]],
        prefix: str | None = "",
        is_webhook: bool = False,
        is_deprecated: bool = False,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Internal recursive function to traverse and process routes."""
        for route in routes:
            # Inherit deprecation status from parent app/router
            if app.router.deprecated:
                is_deprecated = True

            if isinstance(route, router.Include):
                if hasattr(route, "app"):
                    if not should_include_in_schema(route):
                        continue

                # Skip external middlewares without attached routes
                if getattr(route.app, "routes", None) is None and not isinstance(
                    route.app, (DefineMiddleware, MiddlewareProtocol)
                ):
                    continue

                # Recurse into nested Ravyn apps/routers
                if hasattr(route, "app") and isinstance(route.app, (Ravyn, ChildRavyn)):
                    route_path: str = clean_path(prefix + route.path)

                    definitions, components = iterate_routes(
                        route.app,
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

            # Process Gateway/WebhookGateway
            if isinstance(route, (gateways.Gateway, gateways.WebhookGateway)):
                result: tuple[dict[str, Any], dict[str, Any], dict[str, Any]] | None = (
                    get_openapi_path(
                        route=route,
                        operation_ids=operation_ids,
                        field_mapping=field_mapping,
                        is_deprecated=is_deprecated,
                    )
                )

                if result:
                    path_item, security_schemes, path_definitions = result

                    if path_item:
                        if is_webhook:
                            webhooks_paths.setdefault(route.path, {}).update(path_item)
                        else:
                            route_path = clean_path(prefix + route.path_format)
                            paths.setdefault(route_path, {}).update(path_item)

                    if security_schemes:
                        components.setdefault("securitySchemes", {}).update(security_schemes)

                    if path_definitions:
                        definitions.update(path_definitions)

        return definitions, components

    # Process HTTP Routes
    definitions, components = iterate_routes(
        app=app, routes=routes, definitions=definitions, components=components
    )

    # Process Webhooks (if provided)
    if webhooks:
        definitions, components = iterate_routes(
            app=app,
            routes=webhooks,
            definitions=definitions,
            components=components,
            is_webhook=True,
        )

    # 4. Final Assembly
    if definitions:
        # Sort schemas alphabetically
        components["schemas"] = {k: definitions[k] for k in sorted(definitions)}
    if components:
        output["components"] = components

    output["paths"] = paths

    if webhooks_paths:
        output["webhooks"] = webhooks_paths

    if tags:
        output["tags"] = tags

    # Final Pydantic model validation and serialization
    openapi: OpenAPI = OpenAPI(**output)
    model_dump: str = openapi.model_dump_json(by_alias=True, exclude_none=True)

    return cast(dict[str, Any], loads(model_dump))
