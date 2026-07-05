from ravyn.core.config.jwt import JWTConfig
from ravyn.contrib.auth.edgy.base_user import User
from ravyn.exceptions import NotAuthorized
from ravyn.middleware.authentication import AuthenticationMiddleware
from ravyn.security.jwt.token import Token
from lilya._internal._connection import Connection
from lilya.authentication import AuthCredentials, AuthResult
from lilya.types import ASGIApp
from edgy.exceptions import ObjectNotFound


class JWTAuthMiddleware(AuthenticationMiddleware):
    def __init__(self, app: "ASGIApp", config: "JWTConfig"):
        super().__init__(app)
        self.app = app
        self.config = config

    async def retrieve_user(self, user_id) -> User:
        try:
            return await User.get(pk=user_id)
        except ObjectNotFound:
            raise NotAuthorized()

    async def authenticate(self, request: Connection) -> AuthResult:
        token = request.headers.get(self.config.api_key_header)

        if not token:
            raise NotAuthorized("JWT token not found.")

        token = Token.decode(
            token=token, key=self.config.signing_key, algorithm=self.config.algorithm
        )

        user = await self.retrieve_user(token.sub)
        return AuthCredentials(), user
