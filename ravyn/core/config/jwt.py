from datetime import datetime, timedelta
from typing import Union

from pydantic import BaseModel
from typing_extensions import Annotated, Doc


class JWTConfig(BaseModel):
    """
    An instance of [JWTConfig](https://ravyn.dev/configurations/jwt/).

    This is a configuration that should be used with a dependency and for
    that reason you must run first:

    ```shell
    $ pip install ravyn[jwt]
    ```

    This configuration is passed to the [CORSMiddleware](https://ravyn.dev/middleware/middleware/#corsmiddleware) and enables the middleware.

    **Example**

    !!! Note
        This following example will build an auth middleware
        and it will be using the Ravyn contrib version.

        You are free to ignore this and build your own.

    ```python
    from ravyn import Ravyn, settings
    from ravyn.config.jwt import JWTConfig
    from ravyn.contrib.auth.edgy.base_user import AbstractUser

    from edgy import Database, Registry

    database = Database("sqlite:///db.sqlite")
    registry = Registry(database=database)

    class User(AbstractUser):
        '''
        Inheriting from the the contrib user for Edgy.
        '''

        class Meta:
            registry = registry

    jwt_config = JWTConfig(
        signing_key=settings.secret_key,
    )

    auth_middleware = StarletteMiddleware(
        JWTAuthMiddleware, config=jwt_config, user_model=User
    )

    app = Ravyn(middleware=[auth_middleware])
    ```
    """

    signing_key: Annotated[
        str,
        Doc(
            """
            The secret used to encode and generate the JWT Token. Having a centralized `secret` like in the settings would be recommended as it would be the source of truth for any configuration needing a secret.
            """
        ),
    ]
    api_key_header: Annotated[
        str,
        Doc(
            """
            API Key header for the jwt.
            """
        ),
    ] = "X_API_TOKEN"
    authorization_header: Annotated[
        str,
        Doc(
            """
            Authorization header name.
            """
        ),
    ] = "Authorization"
    algorithm: Annotated[
        str,
        Doc(
            """
            Algorithm used for the jwt token encoding/decoding.
            """
        ),
    ] = "HS256"
    audience: Annotated[
        str | None,
        Doc("Expected JWT audience for authentication. When set, tokens must match it."),
    ] = None
    issuer: Annotated[
        str | None,
        Doc("Expected JWT issuer for authentication. When set, tokens must match it."),
    ] = None
    access_token_lifetime: Annotated[
        Union[datetime, timedelta, str, float],
        Doc(
            """
            Lifetime of the token after generation.
            """
        ),
    ] = timedelta(minutes=5)
    refresh_token_lifetime: Annotated[
        Union[datetime, timedelta, str, float],
        Doc(
            """
            Lifetime of the generated refresh token.
            """
        ),
    ] = timedelta(days=1)
    auth_header_types: Annotated[
        list[str],
        Doc(
            """
            Header to be sent with the token value.
            """
        ),
    ] = ["Bearer"]
    jti_claim: Annotated[
        str,
        Doc(
            """
            Used to prevent the JWT from being relayed and relay attacks.
            """
        ),
    ] = "jti"
    verifying_key: Annotated[
        str,
        Doc(
            """
            Verification key.
            """
        ),
    ] = ""
    leeway: Annotated[
        Union[str, int],
        Doc(
            """
            Used for when there is a clock skew times.
            """
        ),
    ] = 0
    sliding_token_lifetime: Annotated[
        Union[datetime, timedelta, str, float],
        Doc(
            """
            A `datetime.timedelta` object which specifies how long sliding tokens are valid to prove authentication. This timedelta value is added to the current UTC time during token generation to obtain the token's default `exp` claim value.
            """
        ),
    ] = timedelta(minutes=5)
    sliding_token_refresh_lifetime: Annotated[
        Union[datetime, timedelta, str, float],
        Doc(
            """
            A `datetime.timedelta` object which specifies how long sliding tokens are valid to be refreshed. This timedelta value is added to the current UTC time during token generation to obtain the token's default `exp` claim value.
            """
        ),
    ] = timedelta(days=1)
    user_id_field: Annotated[
        str,
        Doc(
            """
             The database field from the user model that will be included in generated tokens to identify users. It is recommended that the value of this setting specifies a field that does not normally change once its initial value is chosen. For example, specifying a `username` or `email` field would be a poor choice since an account's username or email might change depending on how account management in a given service is designed. This could allow a new account to be created with an old username while an existing token is still valid which uses that username as a user identifier.
            """
        ),
    ] = "id"
    user_id_claim: Annotated[
        str,
        Doc(
            """
            The claim in generated tokens which will be used to store user identifiers. For example, a setting value of 'user_id' would mean generated tokens include a `user_id` claim that contains the user's identifier.
            """
        ),
    ] = "user_id"
    access_token_name: Annotated[
        str,
        Doc(
            """
            Name of the key for the access token.
            """
        ),
    ] = "access_token"
    refresh_token_name: Annotated[
        str,
        Doc(
            """
            Name of the key for the refresh token.
            """
        ),
    ] = "refresh_token"
