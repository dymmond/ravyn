from ravyn import RavynSettings
from ravyn.core.config.jwt import JWTConfig
from ravyn.contrib.auth.edgy.middleware import JWTAuthMiddleware, JWTAuthBackend
from monkay import load
from lilya.middleware import DefineMiddleware as LilyaMiddleware


class CustomSettings(RavynSettings):
    @property
    def jwt_config(self) -> JWTConfig:
        """
        A JWT object configuration to be passed to the application middleware
        """
        return JWTConfig(signing_key=self.secret_key, auth_header_types=["Bearer", "Token"])

    @property
    def middleware(self) -> list[LilyaMiddleware]:
        """
        Initial middlewares to be loaded on startup of the application.
        """
        return [
            LilyaMiddleware(
                JWTAuthMiddleware,
                backend=JWTAuthBackend(
                    config=self.jwt_config,
                    user_model=load("myapp.models.User"),
                ),
            )
        ]
