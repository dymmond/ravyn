from lilya.middleware import DefineMiddleware as LilyaMiddleware
from monkay import load

from ravyn import Ravyn
from ravyn.conf import settings
from ravyn.core.config.jwt import JWTConfig
from ravyn.contrib.auth.mongoz.middleware import JWTAuthMiddleware, JWTAuthBackend

jwt_config = JWTConfig(signing_key=settings.secret_key, auth_header_types=["Bearer", "Token"])

jwt_auth_middleware = LilyaMiddleware(
    JWTAuthMiddleware,
    backend=JWTAuthBackend(
        config=jwt_config,
        user_model=load("myapp.models.User"),
    ),
)

app = Ravyn(middleware=[jwt_auth_middleware])
