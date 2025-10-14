from typing import Sequence
from myapp.models import User
from myapp.security.jwt.token import Token
from edgy.exceptions import ObjectNotFound

from lilya._internal._connection import Connection
from lilya.authentication import AuthResult, AuthCredentials
from lilya.types import ASGIApp

from ravyn.exceptions import NotAuthorized
from ravyn.middleware.authentication import AuthenticationMiddleware, AuthenticationBackend


class JWTBackend(AuthenticationBackend):
    async def retrieve_user(self, user_id: int) -> User:
        try:
            return await User.get(pk=user_id)
        except ObjectNotFound:
            raise NotAuthorized()

    async def authenticate(
        self, request: Connection, api_key_header: str, signing_key: str, algorithm: str
    ) -> AuthResult:
        token = request.headers.get(api_key_header)

        if not token:
            raise NotAuthorized("JWT token not found.")

        token = Token.decode(token=token, key=signing_key, algorithm=algorithm)

        user = await self.retrieve_user(token.sub)
        return AuthCredentials(), user


class JWTAuthMiddleware(AuthenticationMiddleware):
    """
    An example how to integrate and design a JWT authentication
    middleware assuming a `myapp` in Ravyn.
    """

    def __init__(
        self,
        app: ASGIApp,
        signing_key: str,
        algorithm: str,
        api_key_header: str,
        backend: Sequence[AuthenticationBackend] | AuthenticationBackend | None = None,
    ):
        super().__init__(app, backend=backend)
        self.app = app
        self.signing_key = signing_key
        self.algorithm = algorithm
        self.api_key_header = api_key_header

    async def authenticate(self, conn: Connection) -> AuthResult | Exception:
        for backend in self.backend:
            # exceptions are passed through to __call__ and there handled
            auth_result = await backend.authenticate(
                conn,
                signing_key=self.signing_key,
                algorithm=self.algorithm,
                api_key_header=self.api_key_header,
            )
            if auth_result is not None:
                return auth_result
        return NotAuthorized()
