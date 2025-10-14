from ravyn import RavynSettings
from ravyn.conf import settings
from ravyn.core.config.jwt import JWTConfig
from ravyn.contrib.auth.edgy.middleware import JWTAuthMiddleware, JWTAuthBackend
from monkay import load
from lilya.middleware import DefineMiddleware
from lilya.types import ASGIApp


class AppAuthMiddleware(JWTAuthMiddleware):
    """
    Overriding the JWTAuthMiddleware
    """

    jwt_config = JWTConfig(signing_key=settings.secret_key, auth_header_types=["Bearer", "Token"])

    def __init__(self, app: "ASGIApp"):
        super().__init__(
            app,
            backend=JWTAuthBackend(
                config=self.jwt_config,
                user_model=load("myapp.models.User"),
            ),
        )


class AppSettings(RavynSettings):
    @property
    def middleware(self) -> list[DefineMiddleware]:
        """
        Initial middlewares to be loaded on startup of the application.
        """
        return [DefineMiddleware(AppAuthMiddleware)]
