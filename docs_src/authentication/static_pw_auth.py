import base64
import binascii

from lilya.authentication import AuthCredentials, AuthenticationBackend, BasicUser
from lilya.middleware import DefineMiddleware

from ravyn import Ravyn, Gateway, Request, get
from ravyn.exceptions import AuthenticationError
from ravyn.middleware.authentication import AuthenticationMiddleware
from ravyn.responses import PlainText
import secrets


class HardCodedBasicAuthBackend(AuthenticationBackend):
    def __init__(self, *, username: str = "admin", password: str) -> None:
        self.basic_string = base64.b64encode(f"{username}:{password}".encode()).decode()

    async def authenticate(self, connection) -> tuple[AuthCredentials, BasicUser] | None:
        if "Authorization" not in connection.headers:
            return None

        auth = connection.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != "basic":
                return None
            if not secrets.compare_digest(credentials, self.basic_string):
                raise ValueError()
            username = base64.b64decode(credentials).decode("ascii").split(":", 1)[0]
        except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
            raise AuthenticationError("Invalid basic auth credentials")

        return AuthCredentials(["authenticated"]), BasicUser(username)


@get()
async def homepage(request: Request) -> PlainText:
    if request.user.is_authenticated:
        return PlainText("Hello, " + request.user.display_name)
    return PlainText("Hello, you")


app = Ravyn(
    routes=[Gateway("/", handler=homepage)],
    middleware=[
        DefineMiddleware(
            AuthenticationMiddleware, backend=[HardCodedBasicAuthBackend(password="password")]
        )
    ],
)
