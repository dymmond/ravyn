import traceback
from contextlib import AsyncExitStack
from typing import Optional

from lilya.types import ASGIApp, Receive, Scope, Send

from ravyn.core.config import AsyncExitConfig
from ravyn.core.protocols.middleware import MiddlewareProtocol


class _LazyAsyncExitStack:
    __slots__ = ("_stack",)

    def __init__(self) -> None:
        self._stack: AsyncExitStack | None = None

    def _ensure(self) -> AsyncExitStack:
        if self._stack is None:
            self._stack = AsyncExitStack()
        return self._stack

    async def aclose(self) -> None:
        if self._stack is not None:
            await self._stack.aclose()

    def __getattr__(self, item: str) -> object:
        return getattr(self._ensure(), item)


class AsyncExitStackMiddleware(MiddlewareProtocol):
    def __init__(
        self,
        app: "ASGIApp",
        config: "AsyncExitConfig",
        debug: bool = False,
    ):
        """AsyncExitStack Middleware class.

        Args:
            app: The 'next' ASGI app to call.
            config: The AsyncExitConfig instance.
            debug: If the application should print the stack trace on any error.
        """
        super().__init__(app)
        self.app = app
        self.config = config
        self.debug = debug

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        if not AsyncExitStack:
            await self.app(scope, receive, send)  # pragma: no cover

        exception: Optional[Exception] = None
        lazy_stack = _LazyAsyncExitStack()
        scope[self.config.context_name] = lazy_stack
        scope["_ravyn_route_boundary"] = True
        try:
            await self.app(scope, receive, send)
        except Exception as e:
            exception = e
        finally:
            await lazy_stack.aclose()

        if exception and self.debug:
            traceback.print_exception(exception, exception, exception.__traceback__)  # type: ignore

        if exception:
            raise exception
