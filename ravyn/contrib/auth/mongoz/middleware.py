from typing import Any, TypeVar

import bson
from mongoz import DocumentNotFound

from ravyn.contrib.auth.common.middleware import CommonJWTAuthBackend, CommonJWTAuthMiddleware
from ravyn.core.config.jwt import JWTConfig
from ravyn.exceptions import AuthenticationError, NotAuthorized

T = TypeVar("T")

IDS = ["id", "pk", "_id"]


class JWTAuthBackend(CommonJWTAuthBackend):  # pragma: no cover
    def __init__(
        self,
        config: "JWTConfig",
        user_model: T,
    ):
        super().__init__(config, user_model)
        """
        The user is simply the class type to be queried from the MongoZ ODM.

        Example how to use:

            1. User table

                from ravyn.contrib.auth.mongoz.base_user import User as BaseUser

                class User(BaseUser):
                    ...

            2. Middleware

                from lilya.middleware import DefinedMiddleware

                from ravyn.contrib.auth.mongoz.middleware import JWTAuthMiddleware, JWTAuthBackend
                from ravyn.config import JWTConfig

                jwt_config = JWTConfig(...)

                class CustomJWTMiddleware(JWTAuthMiddleware): ...

            3. The application
                from ravyn import Ravyn
                from myapp.middleware import CustomJWTMiddleware

                app = Ravyn(routes=[...], middleware=[DefinedMiddleware(
                    CustomJWTMiddleware, backend=[JWTAuthBackend(config=jwt_config, user_model=User]
                ))])

        """

    async def retrieve_user(self, token_sub: Any) -> T:
        """
        Retrieves a user from the database using the given token id.
        """
        try:
            sub = int(token_sub)
            token_sub = sub
        except (TypeError, ValueError):
            ...  # noqa

        if isinstance(token_sub, str) and self.config.user_id_field in IDS:
            token_sub = bson.ObjectId(token_sub)

        user_field = {self.config.user_id_field: token_sub}
        try:
            return await self.user_model.objects.get(**user_field)  # type: ignore
        except DocumentNotFound:
            raise NotAuthorized() from None
        except Exception as e:
            raise AuthenticationError(detail=str(e)) from e


class JWTAuthMiddleware(CommonJWTAuthMiddleware):
    """
    The simple JWT authentication Middleware.
    """

    ...
