from typing import Optional, Set

from pydantic import BaseModel
from typing_extensions import Annotated, Doc, Literal


class CSRFConfig(BaseModel):
    """
    An instance of [CRSFConfig](https://ravyn.dev/configurations/csrf/).

    This configuration is passed to the [CSRFMiddleware](https://ravyn.dev/middleware/middleware/#csrfmiddleware) and enables the middleware.

    !!! Tip
        You can creatye your own `CRSFMiddleware` version and pass your own
        configurations. You don't need to use the built-in version although it
        is recommended to do it so.

    **Example**

    ```python
    from ravyn import Ravyn
    from ravyn.config import CSRFConfig

    csrf_config = CSRFConfig(secret="your-long-unique-secret")

    app = Ravyn(csrf_config=csrf_config)
    ```
    """

    secret: Annotated[
        str,
        Doc(
            """
            The string used for the encryption/decryption and used to create an HMAC to sign
            the CSRF token.

            !!! Tip
                It is advised to use the same secret as the one in the settings to make it consistent.
            """
        ),
    ]
    cookie_name: Annotated[
        str,
        Doc(
            """
            The name of the CSRF cookie.
            """
        ),
    ] = "csrftoken"
    cookie_path: Annotated[
        str,
        Doc(
            """
            Name path of the CSRF cookie.
            """
        ),
    ] = "/"
    header_name: Annotated[
        str,
        Doc(
            """
            The header expected that will be expected in each request.
            """
        ),
    ] = "X-CSRFToken"
    secure: Annotated[
        bool,
        Doc(
            """
            Boolean flag when enabled sets `Secure` on the cookie.
            """
        ),
    ] = False
    httponly: Annotated[
        bool,
        Doc(
            """
            Boolean flag when enabled sets the cookie to be `httpsOnly`.
            """
        ),
    ] = False
    samesite: Annotated[
        Literal["lax", "strict", "none"],
        Doc(
            """
            The value to set in the `SameSite` attribute of the cookie.
            """
        ),
    ] = "lax"
    domain: Annotated[
        Optional[str],
        Doc(
            """
            Specifies which hosts can receive the cookie.
            """
        ),
    ] = None
    safe_methods: Annotated[
        Set[str],
        Doc(
            """
            A set of allowed safe methods that can set the cookie.
            """
        ),
    ] = {"GET", "QUERY", "HEAD"}
