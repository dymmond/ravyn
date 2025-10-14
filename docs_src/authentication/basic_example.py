import base64
import binascii

from lilya.authentication import AuthCredentials, AuthenticationBackend, BasicUser
from lilya.middleware import DefineMiddleware

from ravyn import Ravyn, Gateway, Request, get
from ravyn.exceptions import AuthenticationError
from ravyn.middleware.sessions import SessionMiddleware
from ravyn.middleware.authentication import AuthenticationMiddleware
from ravyn.responses import PlainText


class SessionBackend(AuthenticationBackend):
    async def authenticate(self, connection):
        if "session" not in connection.scope:
            return

        if connection.scope["session"].get("username", None):
            return
        return AuthCredentials(["authenticated"]), BasicUser(
            connection.scope["session"]["username"]
        )


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, connection):
        if "Authorization" not in connection.headers:
            return

        auth = connection.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != "basic":
                return
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
            raise AuthenticationError("Invalid basic auth credentials")

        username, _, password = decoded.partition(":")
        return AuthCredentials(["authenticated"]), BasicUser(username)


@get()
async def homepage(request: Request) -> PlainText:
    if request.user.is_authenticated:
        return PlainText("Hello, " + request.user.display_name)
    return PlainText("Hello, you")


app = Ravyn(
    routes=[Gateway("/", handler=homepage)],
    middleware=[
        # must be defined before AuthenticationMiddleware, because of the SessionBackend
        DefineMiddleware(SessionMiddleware, secret_key=...),
        DefineMiddleware(AuthenticationMiddleware, backend=[SessionBackend(), BasicAuthBackend()]),
    ],
)
