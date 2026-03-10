from __future__ import annotations

import inspect
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar, Union

from ravyn.routing.router import HTTPHandler, WebhookHandler
from ravyn.utils.constants import AVAILABLE_METHODS
from ravyn.utils.enums import HttpMethod

if TYPE_CHECKING:
    pass

from . import handlers as _handlers, webhooks as _webhooks

status = _handlers.status
ImproperlyConfigured = _handlers.ImproperlyConfigured

SUCCESSFUL_RESPONSE = "Successful response"

F = TypeVar("F", bound=Callable[..., Any])

__all__ = ["_create_handler_decorator", "_create_route_decorator"]

_HANDLER_TEMPLATES = {
    "GET": _handlers.get,
    "HEAD": _handlers.head,
    "POST": _handlers.post,
    "PUT": _handlers.put,
    "PATCH": _handlers.patch,
    "DELETE": _handlers.delete,
    "OPTIONS": _handlers.options,
    "TRACE": _handlers.trace,
}

_WEBHOOK_TEMPLATES = {
    "GET": _webhooks.whget,
    "HEAD": _webhooks.whhead,
    "POST": _webhooks.whpost,
    "PUT": _webhooks.whput,
    "PATCH": _webhooks.whpatch,
    "DELETE": _webhooks.whdelete,
    "OPTIONS": _webhooks.whoptions,
    "TRACE": _webhooks.whtrace,
}


def _signature_from_template(
    template: Callable[..., Any], *, status_default: Optional[int] = None
) -> inspect.Signature:
    signature = inspect.signature(template)
    if status_default is None or "status_code" not in signature.parameters:
        return signature

    params = []
    for parameter in signature.parameters.values():
        if parameter.name == "status_code":
            params.append(parameter.replace(default=status_default))
        else:
            params.append(parameter)
    return signature.replace(parameters=params)


def _set_metadata(
    fn: Callable[..., Any],
    *,
    name: str,
    template: Callable[..., Any],
    status_default: Optional[int] = None,
) -> Callable[..., Any]:
    fn.__name__ = name
    fn.__qualname__ = name
    fn.__doc__ = template.__doc__
    fn.__annotations__ = dict(template.__annotations__)
    fn.__signature__ = _signature_from_template(template, status_default=status_default)  # type: ignore[attr-defined]
    return fn


def _create_handler_decorator(
    method: str,
    default_status_code: int,
    is_webhook: bool = False,
) -> Callable[..., Any]:
    method_upper = method.upper()
    method_enum = HttpMethod[method_upper]

    templates = _WEBHOOK_TEMPLATES if is_webhook else _HANDLER_TEMPLATES
    template = templates[method_upper]
    method_lower = method.lower()
    decorator_name = f"wh{method_lower}" if is_webhook else method_lower

    def generated_decorator(
        *args: Any, **kwargs: Any
    ) -> Callable[[F], Union[HTTPHandler, WebhookHandler]]:
        signature = _signature_from_template(template, status_default=default_status_code)
        bound = signature.bind_partial(*args, **kwargs)
        bound.apply_defaults()
        values = bound.arguments

        path = values["path"]
        summary = values["summary"]
        description = values["description"]
        status_code = values["status_code"]
        content_encoding = values["content_encoding"]
        content_media_type = values["content_media_type"]
        include_in_schema = values["include_in_schema"]
        background = values["background"]
        dependencies = values["dependencies"]
        exception_handlers = values["exception_handlers"]
        middleware = values["middleware"]
        permissions = values["permissions"]
        media_type = values["media_type"]
        response_class = values["response_class"]
        response_cookies = values["response_cookies"]
        response_headers = values["response_headers"]
        tags = values["tags"]
        deprecated = values["deprecated"]
        security = values["security"]
        operation_id = values["operation_id"]
        response_description = values["response_description"]
        responses = values["responses"]

        name = values.get("name")
        before_request = values.get("before_request")
        after_request = values.get("after_request")

        def wrapper(func: Callable[..., Any]) -> Union[HTTPHandler, WebhookHandler]:
            @wraps(func)
            def wrapped(*wrapper_args: Any, **wrapper_kwargs: Any) -> Any:
                return func(*wrapper_args, **wrapper_kwargs)

            if is_webhook:
                handler = WebhookHandler(
                    path=path,
                    methods=[method_enum],
                    summary=summary,
                    description=description,
                    status_code=status_code,
                    content_encoding=content_encoding,
                    content_media_type=content_media_type,
                    include_in_schema=include_in_schema,
                    background=background,
                    dependencies=dependencies,
                    exception_handlers=exception_handlers,
                    permissions=permissions,
                    middleware=middleware,
                    media_type=media_type,
                    response_class=response_class,
                    response_cookies=response_cookies,
                    response_headers=response_headers,
                    tags=tags,
                    deprecated=deprecated,
                    security=security,
                    operation_id=operation_id,
                    response_description=response_description,
                    responses=responses,
                )
                handler.fn = func
                handler.handler = wrapped
                handler.__type__ = method_enum.value
                handler.validate_handler()
                return handler

            handler = HTTPHandler(
                path=path,
                name=name,
                methods=[method_enum],
                summary=summary,
                description=description,
                status_code=status_code,
                content_encoding=content_encoding,
                content_media_type=content_media_type,
                include_in_schema=include_in_schema,
                background=background,
                dependencies=dependencies,
                exception_handlers=exception_handlers,
                permissions=permissions,
                middleware=middleware,
                media_type=media_type,
                response_class=response_class,
                response_cookies=response_cookies,
                response_headers=response_headers,
                tags=tags,
                deprecated=deprecated,
                security=security,
                operation_id=operation_id,
                response_description=response_description,
                responses=responses,
                before_request=before_request,
                after_request=after_request,
            )
            handler.fn = func
            handler.handler = wrapped
            handler.__type__ = method_enum.value
            handler.__original_status_code__ = default_status_code

            if method_upper in {"GET", "HEAD", "PUT", "PATCH", "OPTIONS", "TRACE"}:
                if status_code != handler.__original_status_code__:
                    handler.__is_status_overridden__ = True

            handler.validate_handler()
            return handler

        return wrapper

    return _set_metadata(
        generated_decorator,
        name=decorator_name,
        template=template,
        status_default=default_status_code,
    )


def _create_route_decorator(is_webhook: bool = False) -> Callable[..., Any]:
    template = _webhooks.whroute if is_webhook else _handlers.route
    decorator_name = "whroute" if is_webhook else "route"

    def generated_decorator(
        *args: Any, **kwargs: Any
    ) -> Callable[[F], Union[HTTPHandler, WebhookHandler]]:
        signature = inspect.signature(template)
        bound = signature.bind_partial(*args, **kwargs)
        bound.apply_defaults()
        values = bound.arguments

        path = values["path"]
        methods = values["methods"]
        summary = values["summary"]
        description = values["description"]
        status_code = values["status_code"]
        content_encoding = values["content_encoding"]
        content_media_type = values["content_media_type"]
        include_in_schema = values["include_in_schema"]
        background = values["background"]
        dependencies = values["dependencies"]
        exception_handlers = values["exception_handlers"]
        middleware = values["middleware"]
        permissions = values["permissions"]
        media_type = values["media_type"]
        response_class = values["response_class"]
        response_cookies = values["response_cookies"]
        response_headers = values["response_headers"]
        tags = values["tags"]
        deprecated = values["deprecated"]
        security = values["security"]
        operation_id = values["operation_id"]
        response_description = values["response_description"]
        responses = values["responses"]

        name = values.get("name")
        before_request = values.get("before_request")
        after_request = values.get("after_request")

        if not methods or not isinstance(methods, list):
            raise ImproperlyConfigured(
                "http handler demands `methods` to be declared. An example would be: @route(methods=['GET', 'PUT'])."
            )

        for method_name in methods:
            if method_name.upper() not in AVAILABLE_METHODS:
                raise ImproperlyConfigured(
                    f"Invalid method {method_name}. An example would be: @route(methods=['GET', 'PUT'])."
                )

        methods = [method_name.upper() for method_name in methods]
        if not status_code:
            status_code = status.HTTP_200_OK

        def wrapper(func: Callable[..., Any]) -> Union[HTTPHandler, WebhookHandler]:
            @wraps(func)
            def wrapped(*wrapper_args: Any, **wrapper_kwargs: Any) -> Any:
                return func(*wrapper_args, **wrapper_kwargs)

            if is_webhook:
                handler = WebhookHandler(
                    path=path,
                    methods=methods,
                    summary=summary,
                    description=description,
                    status_code=status_code,
                    content_encoding=content_encoding,
                    content_media_type=content_media_type,
                    include_in_schema=include_in_schema,
                    background=background,
                    dependencies=dependencies,
                    exception_handlers=exception_handlers,
                    permissions=permissions,
                    middleware=middleware,
                    media_type=media_type,
                    response_class=response_class,
                    response_cookies=response_cookies,
                    response_headers=response_headers,
                    tags=tags,
                    deprecated=deprecated,
                    security=security,
                    operation_id=operation_id,
                    response_description=response_description,
                    responses=responses,
                )
                handler.fn = func
                handler.handler = wrapped
                handler.__type__ = HttpMethod.OPTIONS.value
                handler.validate_handler()
                return handler

            handler = HTTPHandler(
                path=path,
                name=name,
                methods=methods,
                summary=summary,
                description=description,
                status_code=status_code,
                content_encoding=content_encoding,
                content_media_type=content_media_type,
                include_in_schema=include_in_schema,
                background=background,
                dependencies=dependencies,
                exception_handlers=exception_handlers,
                permissions=permissions,
                middleware=middleware,
                media_type=media_type,
                response_class=response_class,
                response_cookies=response_cookies,
                response_headers=response_headers,
                tags=tags,
                deprecated=deprecated,
                security=security,
                operation_id=operation_id,
                response_description=response_description,
                responses=responses,
                before_request=before_request,
                after_request=after_request,
            )

            handler.fn = func
            handler.handler = wrapped
            handler.__type__ = HttpMethod.GET.value
            handler.__original_status_code__ = status.HTTP_200_OK

            if status_code != handler.__original_status_code__:
                handler.__is_status_overridden__ = True

            handler.validate_handler()
            return handler

        return wrapper

    return _set_metadata(generated_decorator, name=decorator_name, template=template)
