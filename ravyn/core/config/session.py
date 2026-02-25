from typing import Union

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator
from typing_extensions import Annotated, Doc, Literal

from ravyn.core.datastructures import Secret

SECONDS_IN_A_DAY: Annotated[
    int,
    Doc(
        """
        Total seconds in a day.
        """
    ),
] = 60 * 60 * 24


class SessionConfig(BaseModel):
    """
    An instance of [SessionConfig](https://ravyn.dev/configurations/session/).

    This configuration is passed to the [SessionMiddleware](https://ravyn.dev/middleware/middleware/#sessionmiddleware) and enables the middleware.

    **Example**

    ```python
    from ravyn import Ravyn
    from ravyn.config import SessionConfig

    session_config = SessionConfig(
        secret_key=settings.secret_key,
        session_cookie="session",
    )

    app = Ravyn(session_config=session_config)
    ```
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    secret_key: Annotated[
        Union[str, bytes, Secret],
        Doc(
            """
            The string used for the encryption/decryption and used to create an HMAC to sign.

            !!! Tip
                It is advised to use the same secret as the one in the settings to make it consistent.
            """
        ),
    ]
    path: Annotated[
        str,
        Doc(
            """
            The path of the cookie.
            """
        ),
    ] = "/"
    session_cookie: Annotated[  # type: ignore
        str,
        StringConstraints(min_length=1, max_length=256),
        Doc(
            """
            The name for the session cookie.
            """
        ),
    ] = "session"
    max_age: Annotated[
        int,
        Doc(
            """
            The number in seconds until the cookie expires.
            """
        ),
    ] = SECONDS_IN_A_DAY * 180
    https_only: Annotated[
        bool,
        Doc(
            """
            Boolean if set enforces the session cookie to be httpsOnly.
            """
        ),
    ] = False
    same_site: Annotated[
        Literal["lax", "strict", "none"],
        Doc(
            """
            Level of restriction for the session cookie.

            Learn more about the [same site](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite).
            """
        ),
    ] = "lax"

    @field_validator("secret_key")
    def validate_secret(
        cls,
        value: Annotated[
            Secret,
            Doc(
                """
                The string secret that will be evaluated.
                """
            ),
        ],
    ) -> Secret:
        if not value:
            raise ValueError("secret_key is empty")
        return value
