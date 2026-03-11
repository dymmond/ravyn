from __future__ import annotations

import hashlib
import inspect
import logging
import re
import threading
from functools import update_wrapper, wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    Sequence,
    TypedDict,
    TypeVar,
    Union,
)

import anyio
import orjson
from lilya._internal._encoders import json_encode
from lilya._internal._path import clean_path  # noqa
from lilya.compat import is_async_callable
from lilya.decorators import observable as observable  # noqa
from typing_extensions import Annotated, Doc, Unpack

from ravyn import Controller
from ravyn.conf import settings
from ravyn.core.protocols.cache import CacheBackend

if TYPE_CHECKING:  # pragma: no cover
    from ravyn.core.interceptors.types import Interceptor
    from ravyn.openapi.schemas.v3_1_0.security_scheme import SecurityScheme
    from ravyn.permissions.types import Permission
    from ravyn.types import (
        Dependencies,
        ExceptionHandlerMap,
        Middleware,
        ResponseCookies,
        ResponseHeaders,
        ResponseType,
    )


T = TypeVar("T", bound=Callable[..., Any])
logger = logging.getLogger(__name__)


class ControllerOptions(TypedDict, total=False):
    path: Annotated[
        str,
        Doc(
            """
            Relative path of the `Gateway`.
            The path can contain parameters in a dictionary like format.
            """
        ),
    ]
    dependencies: Annotated[
        Optional[Dependencies],
        Doc(
            """
            A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
            """
        ),
    ]
    exception_handlers: Annotated[
        Optional[ExceptionHandlerMap],
        Doc(
            """
        A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
        """
        ),
    ]
    permissions: Annotated[
        Optional[list[Permission]],
        Doc(
            """
            A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
            """
        ),
    ]
    interceptors: Annotated[
        Optional[Sequence[Interceptor]],
        Doc(
            """
            A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
            """
        ),
    ]
    middleware: Annotated[
        Optional[list[Middleware]],
        Doc(
            """
        A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
        """
        ),
    ]
    response_class: Annotated[
        Optional[ResponseType],
        Doc(
            """
            Default response class to be used within the
            Ravyn application.

            Read more about the [Responses](https://ravyn.dev/responses/) and how
            to use them.

            **Example**

            ```python
            from ravyn import Controller, JSONResponse


            class MyView(Controller):
                response_class = JSONResponse
            ```
            """
        ),
    ]
    response_cookies: Annotated[
        Optional[ResponseCookies],
        Doc(
            """
            A sequence of `ravyn.datastructures.Cookie` objects.

            Read more about the [Cookies](https://ravyn.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

            **Example**

            ```python
            from ravyn import Controller
            from ravyn.datastructures import Cookie

            response_cookies=[
                Cookie(
                    key="csrf",
                    value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                    max_age=3000,
                    httponly=True,
                )
            ]

            class MyView(Controller):
                response_cookies = response_cookies
            ```
            """
        ),
    ]
    response_headers: Annotated[
        Optional[ResponseHeaders],
        Doc(
            """
        A mapping of `ravyn.datastructures.ResponseHeader` objects.

        Read more about the [ResponseHeader](https://ravyn.dev/extras/header-fields/#response-headers).

        **Example**

        ```python
        from ravyn import Controller
        from ravyn.datastructures import ResponseHeader

        response_headers={
            "authorize": ResponseHeader(value="granted")
        }

        class MyView(Controller):
            response_headers = response_headers
        ```
        """
        ),
    ]
    before_request: Annotated[
        Union[Sequence[Callable[[], Any]], None],
        Doc(
            """
            A `list` of events that are trigger after the application
            processes the request.

            Read more about the [events](https://lilya.dev/lifespan/).

            **Example**

            ```python
            from edgy import Database, Registry

            from ravyn import Ravyn, Request, Gateway, get

            database = Database("postgresql+asyncpg://user:password@host:port/database")
            registry = Registry(database=database)

            async def create_user(request: Request):
                # Logic to create the user
                data = await request.json()
                ...


            app = Ravyn(
                routes=[Gateway("/create", handler=create_user)],
                after_request=[database.disconnect],
            )
            ```
            """
        ),
    ]
    after_request: Annotated[
        Union[Sequence[Callable[[], Any]], None],
        Doc(
            """
            A `list` of events that are trigger after the application
            processes the request.

            Read more about the [events](https://lilya.dev/lifespan/).

            **Example**

            ```python
            from edgy import Database, Registry

            from ravyn import Ravyn, Request, Gateway, get

            database = Database("postgresql+asyncpg://user:password@host:port/database")
            registry = Registry(database=database)


            async def create_user(request: Request):
                # Logic to create the user
                data = await request.json()
                ...


            app = Ravyn(
                routes=[Gateway("/create", handler=create_user)],
                after_request=[database.disconnect],
            )
            ```
            """
        ),
    ]
    tags: Annotated[
        Optional[list[str]],
        Doc(
            """
        A list of strings tags to be applied to the *path operation*.

        It will be added to the generated OpenAPI documentation.

        **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means
        these tags on a Ravyn instance, means it will be added to every route even
        if those routes also contain tags.
        """
        ),
    ]
    include_in_schema: Annotated[
        Optional[bool],
        Doc(
            """
        Boolean flag indicating if it should be added to the OpenAPI docs.
        """
        ),
    ]
    security: Annotated[
        Optional[list[SecurityScheme]],
        Doc(
            """
        Used by OpenAPI definition, the security must be compliant with the norms.
        Ravyn offers some out of the box solutions where this is implemented.

        The [Ravyn security](https://ravyn.dev/openapi/) is available to automatically used.

        The security can be applied also on a [level basis](https://ravyn.dev/application/levels/).

        For custom security objects, you **must** subclass
        `ravyn.openapi.security.base.HTTPBase` object.
        """
        ),
    ]
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
        Boolean flag for indicating the deprecation of the Include and all of its routes and to display it in the OpenAPI documentation..
        """
        ),
    ]


def controller(**kwargs: Unpack[ControllerOptions]) -> Callable[[type], type]:
    """Decorator to transform a class into an Ravyn Controller."""

    def wrapper(cls: Any) -> type:
        # Dynamically create a new class that extends Controller and the original class
        base_path = kwargs.get("path", "/")

        kwargs["path"] = clean_path(base_path)
        new_class = type(
            cls.__name__,  # Keep the original class name
            (Controller, cls),  # Ensure it inherits from Controller
            {**cls.__dict__, **kwargs},  # Merge original attributes with kwargs
        )

        # Preserve the original class metadata
        update_wrapper(new_class, cls, updated=())
        return new_class

    return wrapper


def generate_cache_key(func: Callable, args: Any, kwargs: Any) -> str:
    """
    Generates a stable cache key ensuring it does not include `<locals>`.
    """
    # Get module and function name
    key_base = f"{func.__module__}.{func.__qualname__}"

    # Ensure that nested function names do not include <locals>
    key_base = re.sub(r"\.<locals>\.", ".", key_base)

    # Convert args & kwargs into a deterministic format
    def convert(value: Any) -> Any:
        if isinstance(value, tuple):
            return list(value)  # Convert tuples to lists
        if isinstance(value, set):
            return sorted(value)  # Convert sets to sorted lists for consistency
        return value

    try:
        bound_method = inspect.ismethod(func) or (
            len(args) > 0 and hasattr(args[0], func.__name__)
        )
    except (AttributeError, IndexError):  # Catch attribute access and empty args errors
        bound_method = False

    args_to_encode = args[1:] if bound_method else args

    serialized_data = orjson.dumps(
        {
            "args": [convert(json_encode(arg)) for arg in args_to_encode],
            "kwargs": {k: convert(json_encode(v)) for k, v in kwargs.items()},
        },
        option=orjson.OPT_SORT_KEYS,
    )

    # Use a stable hash to ensure key format remains consistent
    key_hash = hashlib.md5(serialized_data).hexdigest()

    return f"{key_base}:{key_hash}"


# Lock for thread safety
cache_lock = threading.Lock()


class cache:  # noqa
    """
    A function-based caching decorator with TTL support, cache invalidation, and flexible backends.

    This decorator works with both **synchronous** and **asynchronous** functions, supporting AnyIO-based
    thread safety for cache operations. It prevents repeated expensive computations by caching the result
    of function calls and returning cached values when available.

    If the cache backend fails, the function executes normally, and errors are logged without
    affecting the function's behavior.

    Args:
        ttl (Optional[int]): Time-to-live (TTL) in seconds for cached entries.
            - If `None`, the cache entry never expires.
        backend (Optional[CacheBackend]): Custom cache backend to store the data.
            - Defaults to `settings.cache_backend` if not provided.

    Example:
        >>> @cache(ttl=10)
        >>> async def get_data():
        >>>     return "expensive_computation"
    """

    def __init__(self, ttl: Optional[int] = None, backend: Optional[CacheBackend] = None) -> None:
        """
        Initializes the caching decorator with optional TTL and a cache backend.

        Args:
            ttl (Optional[int]): Time in seconds before a cache entry expires.
            backend (Optional[CacheBackend]): The cache backend implementation.
        """
        self.ttl = ttl or settings.cache_default_ttl
        self.backend = backend or settings.cache_backend

    def __call__(self, func: Callable) -> Any:
        """
        Wraps a function with caching logic to store and retrieve results from cache.

        This method determines whether the function is **synchronous** or **asynchronous**
        and applies the appropriate caching mechanism.

        - **For async functions**, it awaits the result and caches it.
        - **For sync functions**, it uses `anyio.run()` to interact with the async cache backend.

        If a cache backend failure occurs, the function runs as usual, and the error is logged.

        Args:
            func (Callable): The function to be decorated.

        Returns:
            Callable: A wrapped function that integrates caching.
        """
        if is_async_callable(func):  # Handle async functions

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                """
                Asynchronous cache wrapper.

                Attempts to retrieve the cached value before calling the actual function.
                If the cache fails, it logs the error and continues execution.

                Args:
                    *args: Positional arguments for the decorated function.
                    **kwargs: Keyword arguments for the decorated function.

                Returns:
                    Any: The cached value if available, otherwise the function result.
                """
                backend = self.backend
                if backend is None:
                    return await func(*args, **kwargs)

                key = generate_cache_key(func, args, kwargs)

                async with anyio.Lock():  # Ensure async thread safety
                    try:
                        cached_value = await backend.get(key)
                        if cached_value is not None:
                            return cached_value
                    except (ConnectionError, TimeoutError, OSError, TypeError, ValueError) as e:
                        # Catch network, timeout, serialization, and value errors from cache backend
                        logger.error(f"Cache backend failure in get(): {e}", exc_info=True)

                    # Proceed with function execution if cache fails
                    result = await func(*args, **kwargs)

                    try:
                        await backend.set(key, result, self.ttl)
                    except (ConnectionError, TimeoutError, OSError, TypeError, ValueError) as e:
                        # Catch network, timeout, serialization, and value errors from cache backend
                        logger.error(f"Cache backend failure in set(): {e}", exc_info=True)

                    return result

            return async_wrapper

        else:  # Handle sync functions with AnyIO for thread safety

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                """
                Synchronous cache wrapper.

                Uses `anyio.run()` to interact with the async cache backend safely.

                Args:
                    *args: Positional arguments for the decorated function.
                    **kwargs: Keyword arguments for the decorated function.

                Returns:
                    Any: The cached value if available, otherwise the function result.
                """
                backend = self.backend
                if backend is None:
                    return func(*args, **kwargs)

                key = generate_cache_key(func, args, kwargs)

                with cache_lock:  # Ensure sync thread safety
                    try:
                        cached_value = anyio.run(backend.get, key)

                        if cached_value is not None:
                            return cached_value
                    except (
                        ConnectionError,
                        TimeoutError,
                        OSError,
                        TypeError,
                        ValueError,
                        RuntimeError,
                    ) as e:
                        # Catch async runtime, network, timeout, and serialization errors
                        logger.error(f"Cache backend failure in get(): {e}", exc_info=True)

                    # Proceed with function execution if cache fails
                    result = func(*args, **kwargs)

                    try:
                        anyio.run(backend.set, key, result, self.ttl)
                    except (
                        ConnectionError,
                        TimeoutError,
                        OSError,
                        TypeError,
                        ValueError,
                        RuntimeError,
                    ) as e:
                        # Catch async runtime, network, timeout, and serialization errors
                        logger.error(f"Cache backend failure in set(): {e}", exc_info=True)

                    return result

            return sync_wrapper

    def invalidate(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        """
        Invalidates the cache entry for a specific function call with given arguments.

        This removes the cached value for a particular function signature, ensuring
        fresh execution the next time it is called.

        Args:
            func (Callable): The decorated function whose cache entry should be invalidated.
            *args: Positional arguments used to generate the cache key.
            **kwargs: Keyword arguments used to generate the cache key.

        Example:
            >>> @cache(ttl=30)
            >>> async def get_user_data(user_id: int):
            >>>     return fetch_from_db(user_id)

            >>> cache.invalidate(get_user_data, user_id=42)  # Removes cache for user 42
        """
        backend = self.backend
        if backend is None:
            return None

        key = generate_cache_key(func, args, kwargs)

        with cache_lock:  # Prevent multiple threads from invalidating at the same time
            try:
                anyio.run(backend.delete, key)
            except (
                ConnectionError,
                TimeoutError,
                OSError,
                TypeError,
                ValueError,
                RuntimeError,
            ) as e:
                # Catch async runtime, network, timeout, and serialization errors
                logger.error(f"Cache backend failure in delete(): {e}", exc_info=True)
