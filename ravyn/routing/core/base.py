from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from functools import partial
from inspect import Signature, isawaitable
from itertools import chain
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Set,
    Type,
    TypeVar,
    Union,
    cast,
)
from uuid import UUID

from lilya._internal._connection import Connection  # noqa
from lilya.datastructures import DataUpload
from lilya.permissions import DefinePermission
from lilya.responses import Response as LilyaResponse
from lilya.routing import compile_path
from lilya.transformers import TRANSFORMER_TYPES
from lilya.types import Receive, Scope, Send
from typing_extensions import TypedDict

from ravyn import status
from ravyn.core.datastructures import ResponseContainer, UploadFile
from ravyn.core.transformers.model import (
    TransformerModel,
    create_signature as transformer_create_signature,
    get_signature,
)
from ravyn.core.transformers.signature import SignatureFactory
from ravyn.exceptions import ImproperlyConfigured
from ravyn.injector import Inject
from ravyn.permissions import BasePermission
from ravyn.permissions.utils import continue_or_raise_permission_exception
from ravyn.requests import Request
from ravyn.responses.base import JSONResponse, Response
from ravyn.routing.controllers.base import BaseController
from ravyn.typing import AnyCallable, Void
from ravyn.utils.constants import DATA, PAYLOAD
from ravyn.utils.helpers import is_async_callable, is_class_and_subclass
from ravyn.utils.sync import AsyncCallable

if TYPE_CHECKING:  # pragma: no cover
    from ravyn.applications import Ravyn
    from ravyn.openapi.schemas.v3_1_0.security_scheme import SecurityScheme
    from ravyn.routing.router import HTTPHandler
    from ravyn.types import (
        APIGateHandler,
        Cookie,
        Dependencies,
        ResponseCookies,
        ResponseHeaders,
    )

param_type_map = {
    "str": str,
    "int": int,
    "float": float,
    "uuid": UUID,
    "decimal": Decimal,
    "date": date,
    "datetime": datetime,
    "time": time,
    "timedelta": timedelta,
    "path": Path,
}

CONV2TYPE = {conv: typ for typ, conv in TRANSFORMER_TYPES.items()}


T = TypeVar("T", bound="Dispatcher")
_empty: tuple[Any, ...] = ()


class PathParameterSchema(TypedDict):
    name: str
    full: str
    type: Type


class OpenAPIDefinitionMixin:  # pragma: no cover
    def parse_path(self, path: str) -> list[Union[str, PathParameterSchema]]:
        """
        Using the Lilya TRANSFORMERS and the application registered convertors,
        transforms the path into a PathParameterSchema used for the OpenAPI definition.
        """
        _, path, variables, _ = compile_path(path)

        parsed_components: list[Union[str, PathParameterSchema]] = []

        for name, convertor in variables.items():
            _type = CONV2TYPE[convertor]
            parsed_components.append(
                PathParameterSchema(name=name, type=param_type_map[_type], full=name)
            )
        return parsed_components


class BaseSignature:
    """
    In charge of handling the signartures of the handlers.
    """

    def create_signature_model(self, is_websocket: bool = False) -> None:
        """
        Creates a signature model for the given route.

        Websockets do not support methods.
        """
        if not self.signature_model:
            self.signature_model = SignatureFactory(
                fn=cast(AnyCallable, self.fn),
                dependency_names=self.dependency_names,
            ).create_signature()

        for dependency in list(self.get_dependencies().values()):
            if not dependency.signature_model:
                dependency.signature_model = SignatureFactory(
                    fn=dependency.dependency, dependency_names=self.dependency_names
                ).create_signature()

        transformer_model = self.create_handler_transformer_model()
        if not is_websocket:
            self.transformer = transformer_model
            for method in self.methods:
                self.route_map[method] = (self, transformer_model)
        else:
            self.websocket_parameter_model = transformer_model

    def create_handler_transformer_model(self) -> TransformerModel:
        """Method to create a TransformerModel for a given handler."""
        dependencies = self.get_dependencies()
        signature_model = get_signature(self)

        return transformer_create_signature(
            signature_model=signature_model,
            dependencies=dependencies,
            path_parameters=self.path_parameters,
        )


class BaseResponseHandler:
    """
    In charge of handling the responses of the handlers.
    """

    __original_status_code__: int | None = None
    __is_status_overridden__: bool = False

    @staticmethod
    async def _get_response_data(
        route: "HTTPHandler", parameter_model: "TransformerModel", request: Request
    ) -> Any:
        """
        Determine required kwargs for the given handler, assign to the object dictionary, and get the response data.

        The application contains the reserved kwargs for Ravyn but also allows to add custom kwargs.

        Args:
            route (HTTPHandler): The route handler for the request.
            parameter_model (TransformerModel): The parameter model for handling request parameters.
            request (Request): The incoming request.

        Returns:
            Any: The response data generated by processing the request.
        """
        signature_model = get_signature(route)

        if parameter_model.has_kwargs:
            kwargs: dict[str, Any] = await parameter_model.to_kwargs(
                connection=request, handler=route
            )

            is_data_or_payload = (
                DATA if DATA in kwargs else (PAYLOAD if PAYLOAD in kwargs else None)
            )

            request_data = kwargs.get(DATA) or kwargs.get(PAYLOAD)

            # Check if there is request data
            if request_data:
                # Get the request data
                data = await request_data

                # Check if the data is an UploadFile or DataUpload and matches the expected parameter type
                if isinstance(data, (UploadFile, DataUpload)) and is_data_or_payload is not None:
                    kwargs[is_data_or_payload] = data
                # Check if the data is None and matches the expected parameter type
                elif is_data_or_payload is not None and data is None:
                    kwargs[is_data_or_payload] = data
                # Check if the data is a dictionary and contains the expected parameter key
                elif is_data_or_payload is not None and is_data_or_payload not in data:
                    kwargs[is_data_or_payload] = data

                # Otherwise, assign the data to kwargs
                # This is important for cases where query parameters are passed as data
                # and the data is not an UploadFile or DataUpload and we don't want
                # to override the k
                else:
                    if data is not None:
                        kwargs.update(data)

            else:
                # Get the request data
                request_data = await parameter_model.get_request_data(request=request)

                # Check if there is request data
                if request_data is not None:
                    # Assign each key-value pair in the request data to kwargs
                    if isinstance(request_data, (UploadFile, DataUpload)) or (
                        isinstance(request_data, (list, tuple))
                        and any(
                            isinstance(value, (UploadFile, DataUpload)) for value in request_data
                        )
                    ):
                        for key, _ in kwargs.items():
                            kwargs[key] = request_data
                    else:
                        if request_data is not None:
                            kwargs.update(request_data)

            for dependency in parameter_model.dependencies:
                kwargs[dependency.key] = await parameter_model.get_dependencies(
                    dependency=dependency, connection=request, **kwargs
                )

            parsed_kwargs = await signature_model.parse_values_for_connection(
                connection=request, **kwargs
            )
        else:
            parsed_kwargs = {}

        if isinstance(route.parent, BaseController):
            fn = partial(route.fn, route.parent, **parsed_kwargs)
        else:
            fn = partial(route.fn, **parsed_kwargs)

        if is_async_callable(fn):
            return await fn()
        return fn()

    def _get_default_status_code(self, data: Response) -> int:
        """
        Get the default status code for the response.
        The Response has a default status code of 200, if the status code is different, it will be returned instead of the one from the handler.

        Args:
            data (Response): The response object.

        Returns:
            int: The default status code for the response.
        """
        default_response_status_code = status.HTTP_200_OK
        if data.status_code != default_response_status_code:
            return data.status_code
        return cast(int, self.status_code)

    def _get_response_container_handler(
        self,
        cookies: ResponseCookies,
        headers: dict[str, Any],
        media_type: str,
    ) -> Callable[
        [Union[ResponseContainer, LilyaResponse], Type[Ravyn], dict[str, Any]], LilyaResponse
    ]:
        """
        Creates a handler for ResponseContainer types.

        Args:
            cookies (ResponseCookies): The response cookies.
            headers (dict[str, Any]): The response headers.
            media_type (str): The media type.

        Returns:
            Callable[[ResponseContainer, Type["Ravyn"], dict[str, Any]], LilyaResponse]: The response container handler function.

        """

        async def response_content(
            data: Union[ResponseContainer, LilyaResponse],
            app: Type["Ravyn"],
            **kwargs: dict[str, Any],
        ) -> LilyaResponse:
            _headers = {**self.get_headers(headers), **data.headers}
            _cookies = self.get_cookies(data.cookies, cookies)
            if isinstance(data, LilyaResponse):
                response: LilyaResponse = data
            else:
                response = data.to_response(
                    app=app,
                    headers=_headers,
                    status_code=data.status_code or self.status_code,
                    media_type=media_type,
                )
            for cookie in _cookies:
                response.set_cookie(**cookie)
            return response

        return cast(
            Callable[
                [Union[ResponseContainer, LilyaResponse], Type["Ravyn"], dict[str, Any]],
                LilyaResponse,
            ],
            response_content,
        )

    def _get_json_response_handler(
        self, cookies: ResponseCookies, headers: dict[str, Any]
    ) -> Callable[[Response, dict[str, Any]], LilyaResponse]:
        """
        Creates a handler function for JSON responses.

        Args:
            cookies (ResponseCookies): The response cookies.
            headers (dict[str, Any]): The response headers.

        Returns:
            Callable[[Response, dict[str, Any]], LilyaResponse]: The JSON response handler function.
        """

        async def response_content(data: Response, **kwargs: dict[str, Any]) -> LilyaResponse:
            _cookies = self.get_cookies(cookies)
            _headers = {
                **self.get_headers(headers),
                **self.allow_header,
            }
            for cookie in _cookies:
                data.set_cookie(**cookie)  # pragma: no cover

            for header, value in _headers.items():
                data.headers[header] = value

            status_code = self._get_default_status_code(data)
            if status_code:
                data.status_code = status_code
            return data

        return cast(Callable[[Response, dict[str, Any]], LilyaResponse], response_content)

    def _get_response_handler(
        self, cookies: ResponseCookies, headers: dict[str, Any], media_type: str
    ) -> Callable[[Response, dict[str, Any]], LilyaResponse]:
        """
        Creates a handler function for Response types.

        Args:
            cookies (ResponseCookies): The response cookies.
            headers (dict[str, Any]): The response headers.
            media_type (str): The media type.

        Returns:
            Callable[[Response, dict[str, Any]], LilyaResponse]: The response handler function.
        """

        async def response_content(data: Response, **kwargs: dict[str, Any]) -> LilyaResponse:
            _cookies = self.get_cookies(data.cookies, cookies)
            _headers = {
                **self.get_headers(headers),
                **self.allow_header,
            }
            for cookie in _cookies:
                data.set_cookie(**cookie)

            status_code = self._get_default_status_code(data)
            if status_code:
                data.status_code = status_code

            if media_type:
                data.media_type = media_type

            for header, value in _headers.items():
                data.headers[header] = value
            return data

        return cast(Callable[[Response, dict[str, Any]], LilyaResponse], response_content)

    def _get_lilya_response_handler(
        self, cookies: ResponseCookies, headers: dict[str, Any]
    ) -> Callable[[LilyaResponse, dict[str, Any]], LilyaResponse]:
        """
        Creates a handler function for Lilya Responses.

        Args:
            cookies (ResponseCookies): The response cookies.
            headers (dict[str, Any]): The response headers.

        Returns:
            Callable[[LilyaResponse, dict[str, Any]], LilyaResponse]: The Lilya response handler function.
        """

        async def response_content(data: LilyaResponse, **kwargs: dict[str, Any]) -> LilyaResponse:
            _cookies = self.get_cookies(cookies)
            _headers = {
                **self.get_headers(headers),
                **self.allow_header,
            }
            for cookie in _cookies:
                data.set_cookie(**cookie)  # pragma: no cover

            for header, value in _headers.items():
                data.headers[header] = value

            return data

        return cast(Callable[[LilyaResponse, dict[str, Any]], LilyaResponse], response_content)

    def _get_default_handler(
        self,
        cookies: ResponseCookies,
        headers: dict[str, Any],
        media_type: str,
        response_class: Any,
    ) -> Callable[[Any, dict[str, Any]], LilyaResponse]:
        """
        Creates a default handler function.

        Args:
            cookies (ResponseCookies): The response cookies.
            headers (dict[str, Any]): The response headers.
            media_type (str): The media type.
            response_class (Any): The response class.

        Returns:
            Callable[[Any, dict[str, Any]], LilyaResponse]: The default handler function.
        """

        async def response_content(data: Any, **kwargs: dict[str, Any]) -> LilyaResponse:
            data = await self.get_response_data(data=data)
            _cookies = self.get_cookies(cookies)

            background = getattr(data, "background", None) or self.background

            status_code = (
                self.status_code
                if self.__is_status_overridden__
                else getattr(data, "status_code", None) or self.status_code
            )

            if isinstance(data, LilyaResponse):
                response = data
                response.status_code = status_code
                response.background = background
            else:
                response = response_class(
                    background=background,
                    content=data,
                    headers=headers,
                    media_type=media_type,
                    status_code=status_code,
                )

            for cookie in _cookies:
                response.set_cookie(**cookie)  # pragma: no cover
            return response

        return cast(Callable[[Response, dict[str, Any]], LilyaResponse], response_content)


class BaseDispatcher(BaseResponseHandler):
    """
    The base class for dispatching requests to route handlers.

    This class provides methods for getting a response for a request and calling the handler function.
    """

    def get_response_for_handler(self) -> Callable[[Any], Awaitable[LilyaResponse]]:
        """
        Checks and validates the type of return response and maps to the corresponding
        handler with the given parameters.

        Returns:
            Callable[[Any], Awaitable[LilyaResponse]]: The response handler function.
        """
        if self._response_handler is not Void:
            return cast("Callable[[Any], Awaitable[LilyaResponse]]", self._response_handler)

        media_type = (
            self.media_type.value if isinstance(self.media_type, Enum) else self.media_type
        )

        response_class = self.get_response_class()
        headers = self.get_response_headers()
        cookies = self.get_response_cookies()

        if is_class_and_subclass(self.handler_signature.return_annotation, ResponseContainer):
            handler = self._get_response_container_handler(cookies, headers, media_type)
        elif is_class_and_subclass(self.handler_signature.return_annotation, JSONResponse):
            handler = self._get_json_response_handler(cookies, headers)  # type: ignore[assignment]
        elif is_class_and_subclass(self.handler_signature.return_annotation, Response):
            handler = self._get_response_handler(cookies, headers, media_type)  # type: ignore[assignment]
        elif is_class_and_subclass(self.handler_signature.return_annotation, LilyaResponse):
            handler = self._get_lilya_response_handler(cookies, headers)  # type: ignore[assignment]
        else:
            handler = self._get_default_handler(cookies, headers, media_type, response_class)  # type: ignore[assignment]

        self._response_handler = handler

        return cast(
            Callable[[Any], Awaitable[LilyaResponse]],
            self._response_handler,
        )

    async def get_response_for_request(
        self,
        scope: "Scope",
        request: Request,
        route: "HTTPHandler",
        parameter_model: "TransformerModel",
    ) -> "LilyaResponse":
        """
        Get response for the given request using the specified route and parameter model.

        Args:
            scope (Scope): The scope of the request.
            request (Request): The incoming request.
            route (HTTPHandler): The route handler for the request.
            parameter_model (TransformerModel): The parameter model for handling request parameters.

        Returns:
            LilyaResponse: The response generated for the request.
        """
        response_data = await self._get_response_data(
            route=route,
            parameter_model=parameter_model,
            request=request,
        )

        response = await self.to_response(
            app=scope["app"],
            data=response_data,
        )
        return cast("LilyaResponse", response)


class Dispatcher(BaseSignature, BaseDispatcher, OpenAPIDefinitionMixin):
    """
    The Dispatcher class is responsible for handling interceptors and executing them before reaching any of the handlers.
    """

    @property
    def handler_signature(self) -> Signature:
        """
        Returns the Signature of the handler function.

        This property returns the Signature object representing the signature of the handler function.
        The Signature object provides information about the parameters, return type, and annotations of the handler function.

        Returns:
        - Signature: The Signature object representing the signature of the handler function.

        Example:
        >>> handler = Dispatcher()
        >>> signature = handler.handler_signature
        >>> print(signature)

        Note:
        - The Signature object is created using the `from_callable` method of the `Signature` class.
        - The `from_callable` method takes a callable object (in this case, the handler function) as input and returns a Signature object.
        - The Signature object can be used to inspect the parameters and return type of the handler function.
        """
        return Signature.from_callable(cast(AnyCallable, self.fn))

    @property
    def path_parameters(self) -> Set[str]:
        """
        Gets the path parameters in a set format.

        This property returns a set of path parameters used in the URL pattern of the handler.
        Each path parameter represents a dynamic value that is extracted from the URL during routing.

        Returns:
        - Set[str]: A set of path parameters.

        Example:
        >>> handler = Dispatcher()
        >>> parameters = handler.path_parameters
        >>> print(parameters)
        {'name', 'id'}

        Note:
        - The path parameters are extracted from the URL pattern defined in the handler's route.
        - The path parameters are represented as strings.
        - If no path parameters are defined in the URL pattern, an empty set will be returned.
        """
        parameters = set()
        for param_name, _ in self.param_convertors.items():
            parameters.add(param_name)
        return parameters

    @property
    def stringify_parameters(self) -> list[str]:  # pragma: no cover
        """
        Gets the param:type in string like list.
        Used for the directive `ravyn show_urls`.

        This property returns a list of strings representing the parameter name and type in the format "param:type".
        It is used specifically for the `ravyn show_urls` directive.

        The method first parses the path of the dispatcher object using the `parse_path` method.
        It then filters out any path components that are not dictionaries, leaving only the parameter components.

        Next, it iterates over each parameter component and creates a string in the format "param:type".
        The parameter name is obtained from the 'name' key of the component dictionary,
        and the parameter type is obtained from the 'type' key of the component dictionary.

        Finally, the method returns the list of stringified parameters.

        Returns:
        - list[str]: A list of strings representing the parameter name and type in the format "param:type".

        Example:
        >>> dispatcher = Dispatcher()
        >>> parameters = dispatcher.stringify_parameters()
        >>> print(parameters)
        ['param1:int', 'param2:str', 'param3:bool']

        Note:
        - The parameter type is obtained using the `__name__` attribute of the type object.
        - The parameter components are obtained by parsing the path of the dispatcher object.
        - If there are no parameter components in the path, an empty list will be returned.
        """
        path_components = self.parse_path(self.path)
        parameters = [component for component in path_components if isinstance(component, dict)]

        stringified_parameters = [
            f"{param['name']}:{param['type'].__name__}" for param in parameters
        ]
        return stringified_parameters

    @property
    def parent_levels(self) -> list[Any]:
        """
        Returns the handler from the app down to the route handler.

        This property returns a list of all the parent levels of the current handler.
        Each parent level represents a higher level in the routing hierarchy.

        Example:
        Consider the following routing hierarchy:
        app = Ravyn(routes=[
            Include(path='/api/v1', routes=[
                Gateway(path='/home', handler=home)
            ])
        ])

        In this example, the parent of the Gateway handler is the Include handler.
        The parent of the Include handler is the Ravyn router.
        The parent of the Ravyn router is the Ravyn app itself.

        The `parent_levels` property uses a while loop to traverse the parent hierarchy.
        It starts with the current handler and iteratively adds each parent level to a list.
        Finally, it reverses the list to maintain the correct order of parent levels.

        Returns:
        - list[Any]: A list of parent levels, starting from the current handler and going up to the app level.

        Note:
        - The parent levels are determined based on the `parent` attribute of each handler.
        - If there are no parent levels (i.e., the current handler is the top-level handler), an empty list will be returned.
        """
        levels = []
        current: Any = self
        while current:
            levels.append(current)
            current = current.parent
        return list(reversed(levels))

    def get_lookup_path(self, ignore_first: bool = True) -> list[str]:
        """
        Constructs and returns the lookup path for the current object by traversing
        its parent hierarchy.

        The method collects the 'name' attribute of the current object and its
        ancestors, if they exist, and returns them as a list in reverse order
        (from the root ancestor to the current object).

        Returns:
            list[str]: A list of names representing the lookup path from the root
            ancestor to the current object.
        """

        names = []
        current: Any = self
        counter: int = 0 if ignore_first else 1

        while current:
            if getattr(current, "name", None) is not None:
                if counter >= 1:
                    names.append(current.name)
            current = current.parent
            counter += 1
        return list(reversed(names))

    @property
    def dependency_names(self) -> Set[str]:
        """
        Returns a unique set of all dependency names provided in the handlers parent levels.

        This property retrieves the dependencies from each parent level of the handler and collects all the dependency names in a set.
        It ensures that the set only contains unique dependency names.

        Returns:
        - Set[str]: A set of unique dependency names.

        Example:
        >>> handler = Dispatcher()
        >>> dependency_names = handler.dependency_names
        >>> print(dependency_names)

        Note:
        - If no dependencies are defined in any of the parent levels, an empty set will be returned.
        - The dependencies are collected from all parent levels, ensuring that there are no duplicate dependency names in the final set.
        """
        level_dependencies = (level.dependencies or {} for level in self.parent_levels)
        return {name for level in level_dependencies for name in level.keys()}

    def get_dependencies(self) -> Dependencies:
        """
        Returns all dependencies of the handler function's starting from the parent levels.

        This method retrieves all the dependencies of the handler function by iterating over each parent level.
        It collects the dependencies defined in each level and stores them in a dictionary.

        Returns:
        - Dependencies: A dictionary containing all the dependencies of the handler function.

        Raises:
        - RuntimeError: If `get_dependencies` is called before a signature model has been generated.

        Example:
        >>> handler = Dispatcher()
        >>> dependencies = handler.get_dependencies()
        >>> print(dependencies)

        Note:
        - If no dependencies are defined in any of the parent levels, an empty dictionary will be returned.
        - Each dependency is represented by a key-value pair in the dictionary, where the key is the dependency name and the value is the dependency object.
        - The dependencies are collected from all parent levels, ensuring that there are no duplicate dependencies in the final dictionary.
        """
        if not self.signature_model:
            raise RuntimeError(
                "get_dependencies cannot be called before a signature model has been generated"
            )

        if not self._dependencies or self._dependencies is Void:
            self._dependencies: Dependencies = {}
            for level in self.parent_levels:
                for key, value in (level.dependencies or {}).items():
                    if not isinstance(value, Inject):
                        value = Inject(value)
                    self.is_unique_dependency(
                        dependencies=self._dependencies,
                        key=key,
                        injector=value,
                    )
                    self._dependencies[key] = value  # type: ignore[assignment]
        return self._dependencies

    @staticmethod
    def is_unique_dependency(dependencies: Dependencies, key: str, injector: Inject) -> None:
        """
        Validates that a given inject has not been already defined under a different key in any of the levels.

        This method takes in a dictionary of dependencies, a key, and an injector. It checks if the injector is already defined in the dependencies dictionary under a different key.

        Parameters:
        - dependencies (Dependencies): A dictionary of dependencies.
        - key (str): The key to check for uniqueness.
        - injector (Inject): The injector to check.

        Raises:
        - ImproperlyConfigured: If the injector is already defined under a different key in the dependencies dictionary.

        Example:
        >>> dependencies = {"db": injector1, "logger": injector2}
        >>> key = "db"
        >>> injector = injector3
        >>> is_unique_dependency(dependencies, key, injector)

        This method iterates over each key-value pair in the dependencies dictionary. If the value matches the given injector, it raises an ImproperlyConfigured exception with a detailed error message.

        Note:
        - The dependencies dictionary is expected to have string keys and values of type Inject.
        - The key parameter should be a string representing the key to check for uniqueness.
        - The injector parameter should be an instance of the Inject class.
        """
        for dependency_key, value in dependencies.items():
            if injector == value:
                raise ImproperlyConfigured(
                    f"Injector for key {key} is already defined under the different key {dependency_key}. "
                    f"If you wish to override a inject, it must have the same key."
                )

    def get_cookies(
        self,
        local_cookies: ResponseCookies | None,
        other_cookies: ResponseCookies | None = None,
    ) -> list[dict[str, Any]]:  # pragma: no cover
        """
        Returns a unique list of cookies.

        This method takes two sets of cookies, `local_cookies` and `other_cookies`,
        and returns a list of dictionaries representing the normalized cookies.

        Parameters:
        - local_cookies (ResponseCookies): The set of local cookies.
        - other_cookies (ResponseCookies): The set of other cookies.

        Returns:
        - list[dict[str, Any]]: A list of dictionaries representing the normalized cookies.

        The method first creates a filtered list of cookies by combining the `local_cookies`
        and `other_cookies` sets. It ensures that only unique cookies are included in the list.

        Then, it normalizes each cookie by converting it into a dictionary representation,
        excluding the 'description' attribute. The normalized cookies are stored in a list.

        Finally, the method returns the list of normalized cookies.

        Note:
        - The 'description' attribute is excluded from the normalized cookies.

        Example usage:
        ```
        local_cookies = [...]
        other_cookies = [...]
        normalized_cookies = get_cookies(local_cookies, other_cookies)
        print(normalized_cookies)
        ```

        This will output the list of normalized cookies.
        """
        filtered_cookies: dict[str, Cookie] = {}
        for cookie in chain(local_cookies or _empty, other_cookies or _empty):
            filtered_cookies.setdefault(cookie.key, cookie)
        return [
            cookie.model_dump(exclude_none=True, exclude={"description"})
            for cookie in filtered_cookies.values()
        ]

    def get_headers(self, headers: ResponseHeaders) -> dict[str, Any]:
        """
        Returns a dictionary of response headers.

        Parameters:
        - headers (ResponseHeaders): The response headers object.

        Returns:
        - dict[str, Any]: A dictionary containing the response headers.

        Example:
        >>> headers = {"Content-Type": "application/json", "Cache-Control": "no-cache"}
        >>> response_headers = get_headers(headers)
        >>> print(response_headers)
        {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}

        This method takes a `ResponseHeaders` object and converts it into a dictionary
        of response headers. Each key-value pair in the `ResponseHeaders` object is
        added to the dictionary.

        Note:
        - The `ResponseHeaders` object is expected to have string keys and values.
        - If the `ResponseHeaders` object is empty, an empty dictionary will be returned.
        """
        return {k: v.value for k, v in headers.items()}

    async def get_response_data(self, data: Any) -> Any:  # pragma: no cover
        """
        Retrieves the response data for synchronous and asynchronous operations.

        This method takes in a `data` parameter, which can be either a regular value or an awaitable object.
        If `data` is an awaitable object, it will be awaited to retrieve the actual response data.
        If `data` is a regular value, it will be returned as is.

        Parameters:
        - data (Any): The response data, which can be either a regular value or an awaitable object.

        Returns:
        - Any: The actual response data.

        Example usage:
        ```
        response_data = await get_response_data(some_data)
        ```
        """
        if isawaitable(data):
            data = await data
        return data

    async def allow_connection(
        self, connection: "Connection", permission: AsyncCallable
    ) -> None:  # pragma: no cover
        """
        Asynchronously allows a connection based on the provided permission.

        Args:
            permission (BasePermission): The permission object to check.
            connection (Connection): The connection object representing the request.
        Returns:
            None
        Raises:
            PermissionException: If the permission check fails.
        """
        awaitable: BasePermission = cast("BasePermission", await permission())
        request: Request = cast("Request", connection)
        handler = cast("APIGateHandler", self)
        await continue_or_raise_permission_exception(request, handler, awaitable)

    async def dispatch_allow_connection(
        self,
        permissions: dict[int, Union[AsyncCallable, DefinePermission]] | Any,
        connection: "Connection",
        scope: Scope,
        receive: Receive,
        send: Send,
        dispatch_call: Callable[..., Awaitable[None]],
    ) -> None:  # pragma: no cover
        """
        Dispatches a connection based on the provided permissions.

        Args:
            permissions (dict[int, Union[AsyncCallable, DefinePermission]]):
                A dictionary mapping permission levels to either an asynchronous
                callable or a DefinePermission instance.
            connection (Connection): The connection object to be dispatched.
            scope (Scope): The scope of the connection.
            receive (Receive): The receive channel for the connection.
            send (Send): The send channel for the connection.
        Returns:
            None
        """
        for _, permission in permissions.items():
            if isinstance(permission, AsyncCallable):
                await self.allow_connection(connection, permission)
            else:
                # Dispatches to lilya permissions
                await dispatch_call(scope, receive, send)

    def get_security_schemes(self) -> list[SecurityScheme]:
        """
        Returns a list of all security schemes associated with the handler.

        This method iterates over each parent level of the handler and collects the security schemes defined in each level.
        The collected security schemes are stored in a list and returned.

        Returns:
        - list[SecurityScheme]: A list of security schemes associated with the handler.

        Example:
        >>> handler = Dispatcher()
        >>> security_schemes = handler.get_security_schemes()
        >>> print(security_schemes)
        [SecurityScheme(name='BearerAuth', type='http', scheme='bearer', bearer_format='JWT'), SecurityScheme(name='ApiKeyAuth', type='apiKey', in_='header', name='X-API-Key')]

        Note:
        - If no security schemes are defined in any of the parent levels, an empty list will be returned.
        - Each security scheme is represented by an instance of the SecurityScheme class.
        - The SecurityScheme class has attributes such as name, type, scheme, bearer_format, in_, and name, which provide information about the security scheme.
        """
        security_schemes: list[SecurityScheme] = []
        for layer in self.parent_levels:
            security_schemes.extend(layer.security or [])
        return security_schemes

    def get_handler_tags(self) -> list[str]:
        """
        Returns all the tags associated with the handler by checking the parents as well.

        This method retrieves all the tags associated with the handler by iterating over each parent level.
        It collects the tags defined in each level and stores them in a list.

        Returns:
        - list[str]: A list of tags associated with the handler.

        Example:
        >>> handler = Dispatcher()
        >>> tags = handler.get_handler_tags()
        >>> print(tags)
        ['api', 'user']

        Note:
        - If no tags are defined in any of the parent levels, an empty list will be returned.
        - Each tag is represented as a string.
        - The tags are collected from all parent levels, ensuring that there are no duplicate tags in the final list.
        """
        tags: list[str] = []
        for layer in self.parent_levels:
            tags.extend(layer.tags or [])

        tags_clean: list[str] = []
        for tag in tags:
            if tag not in tags_clean:
                tags_clean.append(tag)

        return tags_clean if tags_clean else None
