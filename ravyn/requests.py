from typing import TYPE_CHECKING, Any, cast

from lilya._internal._connection import Connection as Connection  # noqa: F401
from lilya.datastructures import URL  # noqa
from lilya.requests import (
    ClientDisconnect as ClientDisconnect,  # noqa
    Request as LilyaRequest,  # noqa: F401
    empty_receive,
    empty_send,
)
from lilya.types import Receive, Scope, Send
from orjson import loads

from ravyn.typing import Void

if TYPE_CHECKING:  # pragma: no cover
    from ravyn.applications import Ravyn
    from ravyn.conf.global_settings import RavynSettings
    from ravyn.types import HTTPMethod


class Request(LilyaRequest):
    def __init__(
        self,
        scope: "Scope",
        receive: "Receive" = empty_receive,
        send: "Send" = empty_send,
    ):
        super().__init__(scope, receive, send)
        self._json: Any = Void

    @property
    def app(self) -> "Ravyn":
        return cast("Ravyn", self.scope["app"])

    @property
    def method(self) -> "HTTPMethod":
        return cast("HTTPMethod", self.scope["method"])

    @property
    def global_settings(self) -> Any:
        """
        Access to the global settings via `request.global_settings`.
        """
        assert "global_settings" in self.scope, (
            "RequestSettingsMiddleware must be added to the middlewares"
        )
        return cast("RavynSettings", self.scope["global_settings"])

    @property
    def app_settings(self) -> Any:
        """
        Access to the app settings via `request.app_settings`.
        """
        assert "app_settings" in self.scope, (
            "RequestSettingsMiddleware must be added to the middlewares"
        )
        return cast("RavynSettings", self.scope["app_settings"])

    async def json(self) -> Any:
        if self._json is Void:
            if "_body" in self.scope:
                body = self.scope["_body"]
            else:
                body = self.scope["_body"] = await self.body() or b"null"
            self._json = loads(body)
        return self._json

    def path_for(self, __name: str, **path_params: Any) -> Any:
        url: URL = super().path_for(__name, **path_params)
        return str(url)

    def url_path_for(self, __name: str, **path_params: Any) -> Any:
        url: URL = super().url_path_for(__name, **path_params)
        return str(url)
