from lilya.types import ASGIApp
from lilya.middleware import DefineMiddleware

from ravyn import Ravyn
from ravyn.conf import settings
from ravyn.core.config.jwt import JWTConfig
from ravyn.contrib.auth.mongoz.middleware import JWTAuthMiddleware, JWTAuthBackend
from monkay import load


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


app = Ravyn(
    middleware=[
        DefineMiddleware(
            AppAuthMiddleware,
        )
    ]
)
