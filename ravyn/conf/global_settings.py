from functools import cached_property
from typing import TYPE_CHECKING, Any, Callable, Optional, Sequence, Union, cast

from lilya.types import Lifespan
from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated, Doc

from ravyn import __version__  # noqa
from ravyn.conf.enums import EnvironmentType
from ravyn.core.caches.memory import InMemoryCache
from ravyn.core.config import (
    CORSConfig,
    CSRFConfig,
    LoggingConfig,
    OpenAPIConfig,
    SessionConfig,
    StaticFilesConfig,
)
from ravyn.core.config.asyncexit import AsyncExitConfig
from ravyn.core.datastructures import Secret
from ravyn.core.interceptors.types import Interceptor
from ravyn.core.protocols.cache import CacheBackend
from ravyn.encoders import Encoder
from ravyn.logging import StandardLoggingConfig
from ravyn.openapi.schemas.v3_1_0 import Contact, License, SecurityScheme
from ravyn.permissions.types import Permission
from ravyn.pluggables import Extension, Pluggable
from ravyn.routing import gateways
from ravyn.types import (
    APIGateHandler,
    Dependencies,
    ExceptionHandlerMap,
    LifeSpanHandler,
    Middleware,
    ResponseCookies,
    ResponseHeaders,
    ResponseType,
)

if TYPE_CHECKING:
    from ravyn.routing.router import Include  # pragma: no cover
    from ravyn.types import TemplateConfig  # pragma: no cover


class CacheBackendSettings(BaseSettings):
    """
    `CacheBackendSettings` settings object. The main entry-point for any settings
    used by **any** Ravyn application.

    Ravyn uses these settings to set the `@caches` decorator and use it across
    the application.
    """

    model_config = SettingsConfigDict(
        extra="allow",
        ignored_types=(cached_property,),
        arbitrary_types_allowed=True,
    )

    cache_backend: Annotated[
        Optional["CacheBackend"],
        Doc(
            """
            Defines the cache backend to be used for caching operations within the application.
            By default, an in-memory cache is used, but this can be replaced with other
            implementations such as Redis or Memcached.

            The cache backend should implement the necessary methods for storing, retrieving,
            and invalidating cached data.

            Read more about this in the official [Ravyn documentation](https://ravyn.dev/caching/).

            !!! Tip
                For distributed applications, consider using an external caching backend
                like Redis instead of the default in-memory cache.
            """
        ),
    ] = InMemoryCache()
    cache_default_ttl: Annotated[int, Doc("Default time-to-live (TTL) for cached items.")] = 300


class RavynSettings(CacheBackendSettings):
    """
    `RavynSettings` settings object. The main entry-point for any settings
    used by **any** Ravyn application.

    Usually, when creating an application you will need some sort of organisation
    and some sort of settings. Ravyn comes with a native settings system where
    you will only need to inherit, override and add your own extra settings and
    use them anywhere.

    When no values are provided upon an instantiation of an `Ravyn` object, these
    settings are used as the defaults.

    The settings can be done via `RAVYN_SETTINGS_MODULE` or `settings_module` parameter
    in the Ravyn instantiation.

    Learn more about [settings](https://ravyn.dev/application/settings/).

    !!! Tip
        The settings system is extremely powerful and must be leveraged accordingly.
        Read more about how to use the [settings](https://ravyn.dev/application/settings/)
        and how you can take advantage of the system.

    **Example**

    ```python
    from ravyn import RavynSettings
    from ravyn.conf.enums import EnvironmentType

    class AppSettings(RavynSettings):
        '''
        Create your own custom settings.
        '''
        debug: bool = False
        environment: Optional[str] = EnvironmentType.TESTING
    ```
    """

    debug: Annotated[
        bool,
        Doc(
            """
            Boolean indicating if the application should return the debug tracebacks on
            server errors, in other words, if you want to have debug errors being displayed.

            Read more about this in the official [Lilya documentation](https://www.lilya.dev/applications/#instantiating-the-application).

            !!! Tip
                Do not use this in production as `True`.
            """
        ),
    ] = False
    environment: Annotated[
        Optional[str],
        Doc(
            """
            Optional string indicating the environment where the settings are running.
            You won't probably need this but it is here in case you might want to use.
            """
        ),
    ] = EnvironmentType.PRODUCTION
    app_name: Annotated[
        str,
        Doc(
            """
            The name of the Ravyn application/API. This name is displayed when the
            [OpenAPI](https://ravyn.dev/openapi/) documentation is used.
            """
        ),
    ] = "Ravyn"
    title: Annotated[
        str,
        Doc(
            """
            The title of the Ravyn application/API. This title is displayed when the
            [OpenAPI](https://ravyn.dev/openapi/) documentation is used.
            """
        ),
    ] = "Ravyn"
    version: Annotated[
        str,
        Doc(
            """
            The version of the Ravyn application/API. This version is displayed when the
            [OpenAPI](https://ravyn.dev/openapi/) documentation is used.

            **Note**: This is the version of your application/API and not th version of the
            OpenAPI specification being used by Ravyn.
            """
        ),
    ] = __version__
    summary: Annotated[
        str,
        Doc(
            """
            The summary of the Ravyn application/API. This short summary is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.
            """
        ),
    ] = "Ravyn application"
    description: Annotated[
        str,
        Doc(
            """
            The description of the Ravyn application/API. This description is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.
            """
        ),
    ] = "Highly scalable, performant, easy to learn and for every application."
    contact: Annotated[
        Optional[Contact],
        Doc(
            """
            A dictionary or an object of type `ravyn.openapi.schemas.v3_1_0.Contact` containing the contact information of the application/API.

            Both dictionary and object contain several fields.

            * **name** - String name of the contact.
            * **url** - String URL of the contact. It **must** be in the format of a URL.
            * **email** - String email address of the contact. It **must** be in the format
            of an email address.
            """
        ),
    ] = Contact(name="admin", email="admin@myapp.com")
    terms_of_service: Annotated[
        Optional[AnyUrl],
        Doc(
            """
            A URL pointing to the Terms of Service of the application.
            This description is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.
            """
        ),
    ] = None
    license: Annotated[
        Optional[License],
        Doc(
            """
            A dictionary or an object of type `ravyn.openapi.schemas.v3_1_0.License` containing the license information of the application/API.

            Both dictionary and object contain several fields.

            * **name** - String name of the license.
            * **identifier** - An [SPDX](https://spdx.dev/) license expression.
            * **url** - String URL of the contact. It **must** be in the format of a URL.
            """
        ),
    ] = None
    security: Annotated[
        Optional[list[SecurityScheme]],
        Doc(
            """
            Used by OpenAPI definition, the security must be compliant with the norms.
            Ravyn offers some out of the box solutions where this is implemented.

            The [Ravyn security](https://ravyn.dev/openapi/) is available to automatically used.

            The security can be applied also on a [level basis](https://ravyn.dev/application/levels/).

            For custom security objects, you **must** subclass
            `ravyn.openapi.security.base.HTTPBase` object.
            """
        ),
    ] = None
    servers: Annotated[
        list[dict[str, Union[str, Any]]],
        Doc(
            """
            A `list` of python dictionaries with the information regarding the connectivity
            to the target.

            This can be useful, for example, if your application is served from different domains and you want a shared OpenAPI documentation to test it all.

            Ravyn automatically handles the OpenAPI documentation generation for you but
            sometimes you might want to add an extra custom domain to it.

            For example, when using `ChildRavyn` modules, since the object itself subclasses
            Ravyn, that also means you can have independent documentation directly in the
            ChildRavyn or access the [top level](https://ravyn.dev/application/levels/)
            documentation (the application itself) where you can select the server to test it.

            If the servers `list` is not provided or an is an empty `list`, the default value
            will be a `dict` with the `url` pointing to `/`.

            Each `dict` of the `list` follows the following format for the parameters:

            * **url** - A URL string to the target host/domain. The URL may support server
            variables and it may be also a relative server (for example, the domain/path of a `ChildRavyn`).
            * **description** - An optional string description of the host/domain.
            * **variables** - A dictionary between the variable and its value. The value
            is used for substitution in the servers URL template. E.g.: `/my-domain/{age: int}`.

            You can read more about how the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.
            """
        ),
    ] = [{"url": "/"}]
    secret_key: Annotated[
        Union[str, Secret],
        Doc(
            """
            A unique string value used for the cryptography. This value is also
            used internally by Ravyn with the JWT as well the
            [CSRFConfig](https://ravyn.dev/configurations/csrf/).

            !!! Tip
                Make sure you do not reuse the same secret key across environments as
                this can lead to security issues that you can easily avoid.
            """
        ),
    ] = "my secret"
    openapi_version: Annotated[
        str,
        Doc(
            """
            The string version of the OpenAPI.

            Ravyn will generate the OpenAPI 3.1.0 by default and will
            output that as the OpenAPI version.

            If you need to somehow trick some of the tools you are using
            by setting a different version of the OpenAPI, this is the
            field you can use to do it so.
            """
        ),
    ] = "3.1.0"
    allowed_hosts: Annotated[
        Optional[list[str]],
        Doc(
            """
            A `list` of allowed hosts for the application. The allowed hosts when not specified
            defaults to `["*"]` but when specified.

            The allowed hosts are also what controls the
            [TrustedHostMiddleware](https://ravyn.dev/middleware/middleware/#trustedhostmiddleware) and you can read more about how to use it.
            """
        ),
    ] = ["*"]
    allow_origins: Annotated[
        Optional[list[str]],
        Doc(
            """
            A `list` of allowed origins hosts for the application.

            The allowed origins is used by the [CORSConfig](https://ravyn.dev/configurations/cors/) and controls the [CORSMiddleware](https://ravyn.dev/middleware/middleware/#corsmiddleware).

            !!! Tip
                If you create your own [CORSConfig](https://ravyn.dev/configurations/cors/),
                this setting **is ignored** and your custom config takes priority.
            """
        ),
    ] = None
    response_class: Annotated[
        Optional[ResponseType],
        Doc(
            """
            Global default response class to be used within the
            Ravyn application.

            Read more about the [Responses](https://ravyn.dev/responses/) and how
            to use them.
            """
        ),
    ] = None
    response_cookies: Annotated[
        Optional[ResponseCookies],
        Doc(
            """
            A global sequence of `ravyn.datastructures.Cookie` objects.

            Read more about the [Cookies](https://ravyn.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).
            """
        ),
    ] = None
    response_headers: Annotated[
        Optional[ResponseHeaders],
        Doc(
            """
            A global mapping of `ravyn.datastructures.ResponseHeader` objects.

            Read more about the [ResponseHeader](https://ravyn.dev/extras/header-fields/#response-headers).
            """
        ),
    ] = None
    include_in_schema: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if all the routes of the application
            should be included in the OpenAPI documentation.

            **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means when the application
            level is set to `include_in_schema=False`, no schemas will be
            displayed in the OpenAPI documentation.

            !!! Tip
                This can be particularly useful if you have, for example, a `ChildRavyn` and
                you don't want to include in the schema the routes of the said `ChildRavyn`.
                This way there is no reason to do it route by route and instead you can
                simply do it directly in the application [level](https://ravyn.dev/application/levels/).
            """
        ),
    ] = True
    tags: Annotated[
        Optional[list[str]],
        Doc(
            """
            A list of strings tags to be applied to the *path operation*.

            It will be added to the generated OpenAPI documentation.

            **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means
            these tags on a Ravyn instance, means it will be added to every route even
            if those routes also contain tags.
            """
        ),
    ] = None
    timezone: Annotated[
        str,
        Doc(
            """
            Object of time `datetime.timezone` or string indicating the
            timezone for the application.

            **Note** - The timezone is internally used for the supported
            scheduler.
            """
        ),
    ] = "UTC"
    root_path: Annotated[
        Optional[str],
        Doc(
            """
            A path prefix that is handled by a proxy not seen in the
            application but seen by external libraries.

            This affects the tools like the OpenAPI documentation.
            """
        ),
    ] = ""
    enable_sync_handlers: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating the the sync handlers should be allowed in the
            application or not.

            When the `enable_sync_handlers` is set to `False` then only
            `async` handlers are allowed in the application.

            !!! Warning
                Be careful when disabling the `enable_sync_handlers`. When this happens,
                only `async` is allowed in the handlers.
            """
        ),
    ] = True
    enable_scheduler: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if the internal scheduler should be enabled
            or not.
            """
        ),
    ] = False
    enable_openapi: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if the OpenAPI documentation should
            be generated or not.

            When `False`, no OpenAPI documentation is accessible.

            !!! Tip
                Disable this option if you run in production and no one should access the
                documentation unless behind an authentication.
            """
        ),
    ] = True
    redirect_slashes: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if the redirect slashes are enabled for the
            routes or not.
            ```
            """
        ),
    ] = True
    x_frame_options: Annotated[
        Union[str, None],
        Doc(
            """
            Set the X-Frame-Options HTTP header in HTTP responses.

            To enable the response to be loaded on a frame within the same site, set
            x_frame_options to 'SAMEORIGIN'.

            This flag is to be used when `XFrameOptionsMiddleware` is added to the
            application.
            """
        ),
    ] = None
    before_request: Annotated[
        Union[Sequence[Callable[..., Any]], None],
        Doc(
            """
            A `list` of events that are trigger after the application
            processes the request.

            Read more about the [events](https://lilya.dev/lifespan/).

            **Example**

            ```python
            from edgy import Database, Registry

            from ravyn import Ravyn, Request, Gateway, get

            database = Database("postgresql+asyncpg://user:password@host:port/database")
            registry = Registry(database=database)

            async def create_user(request: Request):
                # Logic to create the user
                data = await request.json()
                ...


            app = Ravyn(
                routes=[Gateway("/create", handler=create_user)],
                after_request=[database.disconnect],
            )
            ```
            """
        ),
    ] = None
    after_request: Annotated[
        Union[Sequence[Callable[..., Any]], None],
        Doc(
            """
            A `list` of events that are trigger after the application
            processes the request.

            Read more about the [events](https://lilya.dev/lifespan/).

            **Example**

            ```python
            from edgy import Database, Registry

            from ravyn import Ravyn, Request, Gateway, get

            database = Database("postgresql+asyncpg://user:password@host:port/database")
            registry = Registry(database=database)


            async def create_user(request: Request):
                # Logic to create the user
                data = await request.json()
                ...


            app = Ravyn(
                routes=[Gateway("/create", handler=create_user)],
                after_request=[database.disconnect],
            )
            ```
            """
        ),
    ] = None
    root_path_in_servers: Annotated[
        bool,
        Doc(
            """
            Boolean flag use to disable the automatic URL generation in the `servers` field
            in the OpenAPI documentation.
            """
        ),
    ] = True
    webhooks: Annotated[
        Optional[Sequence[gateways.WebhookGateway]],
        Doc(
            """
            This is the same principle of the `routes` but for OpenAPI webhooks.

            Read more [about webhooks](https://ravyn.dev/routing/webhooks).

            When a webhook is added, it will automatically add them into the
            OpenAPI documentation.
            """
        ),
    ] = None
    openapi_url: Annotated[
        Optional[str],
        Doc(
            """
            The URL where the OpenAPI schema will be served from.
            The default is `/openapi.json`.

            **Example**

            ```python
            from ravyn import Ravyn

            app = Ravyn(openapi_url="/api/v1/openapi.json")
            ```
            """
        ),
    ] = "/openapi.json"
    docs_url: Annotated[
        Optional[str],
        Doc(
            """
            String default relative URL where the Swagger documentation
            shall be accessed in the application.

            This is used as the default if no [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "/docs/swagger"
    redoc_url: Annotated[
        Optional[str],
        Doc(
            """
            String default relative URL where the ReDoc documentation
            shall be accessed in the application.

            This is used as the default if no [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "/docs/redoc"
    swagger_ui_oauth2_redirect_url: Annotated[
        Optional[str],
        Doc(
            """
            String default relative URL where the Swagger UI OAuth Redirect URL
            shall be accessed in the application.

            This is used as the default if no [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "/docs/oauth2-redirect"
    redoc_js_url: Annotated[
        str,
        Doc(
            """
            String default URL where the ReDoc Javascript is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    redoc_favicon_url: Annotated[
        str,
        Doc(
            """
            String default URL where the ReDoc favicon is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "https://ravyn.dev/statics/images/favicon.ico"
    swagger_ui_init_oauth: Annotated[
        Optional[dict[str, Any]],
        Doc(
            """
            String default relative URL where the Swagger Init Auth documentation
            shall be accessed in the application.

            This is used as the default if no [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = None
    swagger_ui_parameters: Annotated[
        Optional[dict[str, Any]],
        Doc(
            """
            A mapping with parameters to be passed onto Swagger.

            This is used as the default if no [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = None
    swagger_js_url: Annotated[
        str,
        Doc(
            """
            String default URL where the Swagger Javascript is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.4/swagger-ui-bundle.min.js"
    swagger_css_url: Annotated[
        str,
        Doc(
            """
            String default URL where the Swagger CSS is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.4/swagger-ui.min.css"
    swagger_favicon_url: Annotated[
        str,
        Doc(
            """
            String default URL where the Swagger favicon is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "https://ravyn.dev/statics/images/favicon.ico"
    with_google_fonts: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if the google fonts shall be used
            in the ReDoc OpenAPI Documentation.

            This is used as the default if no [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = True
    stoplight_js_url: Annotated[
        Optional[str],
        Doc(
            """
            String default URL where the Stoplight Javascript is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "https://unpkg.com/@stoplight/elements/web-components.min.js"
    stoplight_css_url: Annotated[
        Optional[str],
        Doc(
            """
            String default URL where the Stoplight CSS is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "https://unpkg.com/@stoplight/elements/styles.min.css"
    stoplight_url: Annotated[
        Optional[str],
        Doc(
            """
            String default relative URL where the Stoplight documentation
            shall be accessed in the application.

            This is used as the default if no [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "/docs/elements"
    stoplight_favicon_url: Annotated[
        str,
        Doc(
            """
            String default URL where the Stoplight favicon is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "https://ravyn.dev/statics/images/favicon.ico"
    rapidoc_url: Annotated[
        Optional[str],
        Doc(
            """
            String default relative URL where the Rapidoc documentation
            shall be accessed in the application.

            Example: `/docs/rapidoc`.
            """
        ),
    ] = "/docs/rapidoc"
    rapidoc_js_url: Annotated[
        Optional[str],
        Doc(
            """
            String default URL where the RapiDoc Javascript is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "https://unpkg.com/rapidoc@9.3.4/dist/rapidoc-min.js"
    rapidoc_favicon_url: Annotated[
        Optional[str],
        Doc(
            """
            String default URL where the RapiDoc favicon is located
            and used within OpenAPI documentation,

            Example: `https://ravyn.dev/statics/images/favicon.ico`.
            """
        ),
    ] = "https://ravyn.dev/statics/images/favicon.ico"

    # Shell configuration
    ipython_args: list[str] = ["--no-banner"]
    ptpython_config_file: str = "~/.config/ptpython/config.py"

    ignore_reload: Annotated[bool, Doc("""Ignore the reload settings.""")] = False

    @property
    def reload(self) -> bool:
        """
        Boolean flag indicating if the server should have hot reload
        or not.
        """
        if self.environment in [EnvironmentType.DEVELOPMENT, EnvironmentType.TESTING]:
            return True
        return False

    @property
    def password_hashers(self) -> list[str]:
        """
        list of available password hashers of Ravyn.
        These password hashers are used withing the `ravyn.contrib.*` and aims
        to simplify the process of creating and validating password.

        Read more about the [password hashers](https://ravyn.dev/password-hashers/?h=passwor).

        Return:
            list of strings with the module and object location of the password hashers.

        Default:
            ```python
            [
                "ravyn.contrib.auth.hashers.BcryptPasswordHasher",
            ]
            ```

        **Example**

        ```python
        from ravyn import RavynSettings
        from ravyn.contrib.auth.hashers import BcryptPasswordHasher

        # myapp.hashers.py
        class CustomHasher(BcryptPasswordHasher):
            '''
            All the hashers inherit from BasePasswordHasher
            '''
            salt_entropy = 3000

        # settings.py

        class AppSettings(RavynSettings):

            @property
            def password_hashers(self) -> list[str]:
                return ["myapp.hashers.CustomHasher"]
                ```
        ```
        """
        return [
            "ravyn.contrib.auth.hashers.BcryptPasswordHasher",
        ]

    @property
    def routes(self) -> list[Union[APIGateHandler, "Include"]]:
        """
        A global `list` of ravyn routes. Those routes may vary and those can
        be `Gateway`, `WebSocketGateWay` or even `Include`.

        This is also the entry-point for the routes of the application itself
        but it **does not rely on only one [level](https://ravyn.dev/application/levels/)**.

        Read more about how to use and leverage
        the [Ravyn routing system](https://ravyn.dev/routing/routes/).

        Returns:
            list of routes

        Default:
            []

        **Example**

        ```python
        from ravyn import Ravyn, Gateway, Request, get, Include, RavynSettings

        @get()
        async def homepage(request: Request) -> str:
            return "Hello, home!"


        @get()
        async def another(request: Request) -> str:
            return "Hello, another!"


        class APPSettings(RavynSettings):

            @property
            def routes(self) -> list[Union[APIGateHandler, "Include"]]:
                return [
                    Gateway(handler=homepage)
                    Include("/nested",
                        routes=[
                            Gateway(handler=another)
                        ]
                    )
                ]
        ```
        """
        return []

    @property
    def csrf_config(self) -> Optional[CSRFConfig]:
        """
        An instance of [CRSFConfig](https://ravyn.dev/configurations/csrf/).

        This configuration is passed to the [CSRFMiddleware](https://ravyn.dev/middleware/middleware/#csrfmiddleware) and enables the middleware.

        !!! Tip
            You can creatye your own `CRSFMiddleware` version and pass your own
            configurations. You don't need to use the built-in version although it
            is recommended to do it so.

        **Example**

        Default:
            None

        **Example**

        ```python
        from ravyn import RavynSettings


        class AppSettings(RavynSettings):
            secret: str = "n(0t=%_amauq1m&6sde4z#3mkdmfcad1942ny&#sjp1oygk-5_"

            @property
            def csrf_config(self) -> CSRFConfig:
                if not self.secret_key:
                    raise ImproperlyConfigured("`secret` setting not configured.")
                return CSRFConfig(secret=self.secret_key)
        ```
        """
        return None

    @property
    def async_exit_config(self) -> AsyncExitConfig:
        """
        Initial Default configuration for the CSRF.
        This can be overwritten in another setting or simply override `secret` or then override
        the `def async_exit_config()` property to change the behavior of the whole async_exit_config.

        This replaces the classic:
        `async_exit_config: Optional[AsyncExitConfig] = None`.

        Default:
            AsyncExitConfig

        **Example**

        ```python
        from ravyn import RavynSettings


        class AppSettings(RavynSettings):
            @property
            def async_exit_config(self) -> AsyncExitConfig:
                ...
        ```
        """
        return AsyncExitConfig()

    @property
    def template_config(self) -> Optional["TemplateConfig"]:
        """
        An instance of [TemplateConfig](https://ravyn.dev/configurations/template/).
        This configuration is a simple set of configurations that when passed enables the template engine.

        !!! Note
            You might need to install the template engine before
            using this. You can always run
            `pip install ravyn[templates]` to help you out.

        Default:
            JinjaTemplateEngine

        **Example**

        ```python
        from ravyn import RavynSettings


        class AppSettings(RavynSettings):
            @property
            def template_config(self) -> TemplateConfig:
                TemplateConfig(directory='templates')
        ```
        """
        return None

    @property
    def static_files_config(
        self,
    ) -> Union[StaticFilesConfig, list[StaticFilesConfig], tuple[StaticFilesConfig, ...], None]:
        """
        An instance of [StaticFilesConfig](https://ravyn.dev/configurations/staticfiles/).

        This configuration is used to enable and serve static files via
        Ravyn application.

        Default:
            None

        **Example**

        ```python
        from ravyn import RavynSettings

        class AppSettings(RavynSettings):
            @property
            def static_files_config(self) -> StaticFilesConfig:
                StaticFilesConfig(path='/', directories=...)
        ```
        """
        return None

    @property
    def cors_config(self) -> Optional[CORSConfig]:
        """
        An instance of [CORSConfig](https://ravyn.dev/configurations/cors/).

        This configuration is passed to the [CORSMiddleware](https://ravyn.dev/middleware/middleware/#corsmiddleware) and enables the middleware.

        Default:
            CORSConfig

        **Example**

        ```python
        from ravyn import RavynSettings


        class AppSettings(RavynSettings):
            allow_origins: list[str] = ['www.example.com', 'www.foobar.com']

            @property
            def cors_config(self) -> CORSConfig:
                ...
        ```
        """
        if not self.allow_origins:
            return None
        return CORSConfig(allow_origins=self.allow_origins)

    @property
    def session_config(self) -> Optional[SessionConfig]:
        """
        An instance of [SessionConfig](https://ravyn.dev/configurations/session/).

        This configuration is passed to the [SessionMiddleware](https://ravyn.dev/middleware/middleware/#sessionmiddleware) and enables the middleware.

        Default:
            None

        **Example**

        ```python
        from ravyn import RavynSettings


        class AppSettings(RavynSettings):

            @property
            def session_config(self) -> SessionConfig:
                SessionConfig(
                    secret_key=self..secret_key,
                    session_cookie="session"
                )
        ```
        """
        return None

    @property
    def logging_config(self) -> Optional[LoggingConfig]:  # noqa
        """
        An instance of [LoggingConfig](https://ravyn.dev/configurations/logging/).

        Default:
            StandardLogging()

        **Example**

        ```python
        from ravyn import RavynSettings


        class AppSettings(RavynSettings):

            @property
            def logging_config(self) -> LoggingConfig:
                LoggingConfig(
                    log_level="INFO",
                    log_format="%(levelname)s - %(message)s",
                    log_file="app.log"
                )
        ```
        """
        return cast(LoggingConfig, StandardLoggingConfig(level=self.logging_level))

    logging_level: Annotated[
        str,
        Doc(
            """
            The logging level for the application. Defaults to `DEBUG`.
            This is used by the `StandardLoggingConfig` to set the logging level.
            """
        ),
    ] = "INFO"

    @property
    def openapi_config(self) -> OpenAPIConfig:
        """
        An instance of [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/).

        This object is then used by Ravyn to create the [OpenAPI](https://ravyn.dev/openapi/) documentation.

        **Note**: Here is where the defaults for Ravyn OpenAPI are overriden and if
        this object is passed, then the previous defaults of the settings are ignored.

        !!! Tip
            This is the way you could override the defaults all in one go
            instead of doing attribute by attribute.

        Default:
            OpenAPIConfig

        **Example**

        ```python
        from ravyn import RavynSettings


        class AppSettings(RavynSettings):

            @property
            def openapi_config(self) -> OpenAPIConfig:
                    ...
        ```
        """
        return OpenAPIConfig(
            title=self.title,
            version=self.version,
            contact=self.contact,
            description=self.description,
            terms_of_service=self.terms_of_service,
            license=self.license,
            servers=self.servers,
            summary=self.summary,
            security=self.security,
            tags=self.tags,
            docs_url=self.docs_url,
            redoc_url=self.redoc_url,
            swagger_ui_oauth2_redirect_url=self.swagger_ui_oauth2_redirect_url,
            redoc_js_url=self.redoc_js_url,
            redoc_favicon_url=self.redoc_favicon_url,
            swagger_ui_init_oauth=self.swagger_ui_init_oauth,
            swagger_ui_parameters=self.swagger_ui_parameters,
            swagger_js_url=self.swagger_js_url,
            swagger_css_url=self.swagger_css_url,
            swagger_favicon_url=self.swagger_favicon_url,
            root_path_in_servers=self.root_path_in_servers,
            openapi_version=self.openapi_version,
            openapi_url=self.openapi_url,
            with_google_fonts=self.with_google_fonts,
            webhooks=self.webhooks,
            stoplight_css_url=self.stoplight_css_url,
            stoplight_js_url=self.stoplight_js_url,
            stoplight_url=self.stoplight_url,
            stoplight_favicon_url=self.stoplight_favicon_url,
            rapidoc_url=self.rapidoc_url,
            rapidoc_js_url=self.rapidoc_js_url,
            rapidoc_favicon_url=self.rapidoc_favicon_url,
        )

    @property
    def middleware(self) -> Sequence[Middleware]:
        """
        A global sequence of Lilya middlewares or `ravyn.middlewares` that are
        used by the application.

        Read more about the [Middleware](https://ravyn.dev/middleware/middleware/).

        Defaults:
            []

        **Example**

        ```python
        from ravyn import RavynSettings
        from ravyn.middleware import HTTPSRedirectMiddleware, TrustedHostMiddleware
        from lilya.middleware import Middleware as StarletteMiddleware


        class AppSettings(RavynSettings):

            @property
            def middleware(self) -> list[Middleware]:
                return [
                    StarletteMiddleware(
                        TrustedHostMiddleware, allowed_hosts=["example.com", "*.example.com"]
                    )
                ]

        ```
        """
        return []

    @property
    def scheduler_config(self) -> Any:
        """
        Ravyn comes with an internal scheduler connfiguration that can be used to schedule tasks with any scheduler at your choice.


        Ravyn also integrates out of the box with [Asyncz](https://asyncz.tarsild.io/)
        and the scheduler class is nothing more than the `AsyncIOScheduler` provided
        by the library.

        !!! Tip
            You can create your own scheduler class and use it with Ravyn.
            For that you must read the [Asyncz](https://asyncz.tarsild.io/schedulers/)
            documentation and how to make it happen.

        **Note** - To enable the scheduler, you **must** set the `enable_scheduler=True`.
        """
        return None

    @property
    def interceptors(self) -> list[Interceptor]:
        """
        A `list` of global interceptors from objects inheriting from
        `ravyn.interceptors.interceptor.RavynInterceptor`.

        Read more about how to implement the [Interceptors](https://ravyn.dev/interceptors/) in Ravyn and to leverage them.

        **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means
        these interceptors on a Ravyn instance, means **the whole application**.

        Returns:
            list of interceptors

        Default:
            []

        **Example**

        ```python
        from loguru import logger
        from lilya.types import Receive, Scope, Send

        from ravyn import Ravyn, RavynInterceptor, RavynSettings


        class LoggingInterceptor(RavynInterceptor):
            async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
                # Log a message here
                logger.info("This is my interceptor being called before reaching the handler.")


        class AppSettings(RavynSettings):
            def interceptors(self) -> list[Interceptor]:
                return [LoggingInterceptor]

        ```
        """
        return []

    @property
    def permissions(self) -> list[Permission]:
        """
        A `list` of global permissions from objects inheriting from
        `ravyn.permissions.BasePermission`.

        Read more about how to implement the [Permissions](https://ravyn.dev/permissions/#basepermission-and-custom-permissions) in Ravyn and to leverage them.

        **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means
        these permissions on a Ravyn instance, means **the whole application**.

        Default:
            []

        Returns:
            list of global permissions (not permissions on levels).

        **Example**

        ```python
        from ravyn import Ravyn, RavynSettings, BasePermission, Request
        from ravyn.types import APIGateHandler


        class IsAdmin(BasePermission):
            '''
            Permissions for admin
            '''
            async def has_permission(self, request: "Request", controller: "APIGateHandler"):
                is_admin = request.headers.get("admin", False)
                return bool(is_admin)


        class AppSettings(RavynSettings):
            def permissions(self) -> list[Permission]:
                return [IsAdmin]
        ```
        """
        return []

    @property
    def dependencies(self) -> Dependencies:
        """
        A dictionary of global dependencies. These dependencies will be
        applied to each **path** of the application.

        Read more about [Dependencies](https://ravyn.dev/dependencies/).

        Returns:
            A dictionary of global dependencies.

        Default:
            {}

        **Example**

        ```python
        from ravyn import Ravyn, RavynSettings, Inject

        def is_valid(number: int) -> bool:
            return number >= 5

        class AppSettings(RavynSettings):
            def dependencies(self) -> Dependencies:
                return {
                    "is_valid": Inject(is_valid)
                }
        ```
        """
        return {}

    @property
    def exception_handlers(self) -> ExceptionHandlerMap:
        """
        A global dictionary with handlers for exceptions.

        **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means
        these exception handlers on a Ravyn instance, means **the whole application**.

        Read more about the [Exception handlers](https://ravyn.dev/exception-handlers/).

        Returns:
            Mapping of exception handlers where the key is the exception object and the value
            is the callable.

        **Example**

        ```python
        from pydantic.error_wrappers import ValidationError
        from ravyn import (
            Ravyn,
            RavynSettings,
            JSONResponse,
            Request,
            ValidationErrorException,
        )

        async def validation_error_exception_handler(
            request: Request, exc: ValidationError
        ) -> JSONResponse:
            extra = getattr(exc, "extra", None)
            if extra:
                return JSONResponse(
                    {"detail": exc.detail, "errors": exc.extra.get("extra", {})},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            else:
                return JSONResponse(
                    {"detail": exc.detail},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )


        class AppSettings(RavynSettings):

            @property
            def exception_handlers(self) -> ExceptionHandlerMap:
                return {
                    ValidationErrorException: validation_error_exception_handler,
                }
        ```
        """
        return {}

    @property
    def on_startup(self) -> Union[list[LifeSpanHandler], None]:
        """
        A `list` of events that are trigger upon the application
        starts.

        Read more about the [events](https://ravyn.dev/lifespan-events/).

        Returns:
            list of events

        Default:
            None

        **Example**

        ```python
        from pydantic import BaseModel
        from saffier import Database, Registry

        from ravyn import Ravyn, RavynSettings, Gateway, post

        database = Database("postgresql+asyncpg://user:password@host:port/database")
        registry = Registry(database=database)


        class AppSettings(RavynSettings):

            @property
            def on_startup(self) -> Union[list[LifeSpanHandler], None]:
                return [
                    database.connect
                ]
        ```
        """
        return None

    @property
    def on_shutdown(self) -> Union[list[LifeSpanHandler], None]:
        """
        A `list` of events that are trigger upon the application
        shuts down.

        Read more about the [events](https://ravyn.dev/lifespan-events/).

        Returns:
            list of events

        Default:
            None

        **Example**

        ```python
        from pydantic import BaseModel
        from saffier import Database, Registry

        from ravyn import Ravyn, RavynSettings, Gateway, post

        database = Database("postgresql+asyncpg://user:password@host:port/database")
        registry = Registry(database=database)


        class AppSettings(RavynSettings):

            @property
            def on_shutdown(self) -> Union[list[LifeSpanHandler], None]:
                return [
                    database.connect
                ]
        ```
        """
        return None

    @property
    def lifespan(self) -> Optional["Lifespan"]:
        """
        A `lifespan` context manager handler. This is an alternative
        to `on_startup` and `on_shutdown` and you **cannot used all combined**.

        Read more about the [lifespan](https://ravyn.dev/lifespan-events/).
        """
        return None

    @property
    def extensions(self) -> dict[str, Union["Extension", "Pluggable", type["Extension"]]]:
        """
        A `list` of global extensions from objects inheriting from
        `ravyn.interceptors.interceptor.RavynInterceptor`.

        Read more about how to implement the [Plugables](https://ravyn.dev/pluggables/) in Ravyn and to leverage them.

        Returns:
            Mapping of extensions

        Defaults:
            {}

        **Example**

        ```python
        from typing import Optional

        from loguru import logger
        from pydantic import BaseModel

        from ravyn import Ravyn, RavynSettings, Extension, Pluggable
        from ravyn.types import DictAny


        class PluggableConfig(BaseModel):
            name: str


        class MyExtension(Extension):
            def extend(self, config: PluggableConfig = None) -> None:
                logger.success(f"Successfully passed a config {config.name}")

        class AppSettings(RavynSettings):

            @property
            def extensions(self) -> dict[str, Union["Extension", "Pluggable", type["Extension"]]]:
                my_config = PluggableConfig(name="my extension")

                return {
                    "my-extension": Pluggable(MyExtension, config=my_config),
                    "my-extension": MyExtension,
                }
        ```
        """
        return {}

    @property
    def pluggables(self) -> dict[str, Union["Extension", "Pluggable", type["Extension"]]]:
        """
        Deprecated
        """
        return {}

    @property
    def encoders(self) -> Union[list[Encoder], None]:
        """
        A `list` of encoders to be used by the application once it
        starts.

        Returns:
            list of encoders

        **Example**

        ```python
        from typing import Any

        from attrs import asdict, define, field, has
        from ravyn.encoders import Encoder


        class AttrsEncoder(Encoder):

            def is_type(self, value: Any) -> bool:
                return has(value)

            def serialize(self, obj: Any) -> Any:
                return asdict(obj)

            def encode(self, annotation: Any, value: Any) -> Any:
                return annotation(**value)


        class AppSettings(RavynSettings):

            @property
            def encoders(self) -> Union[list[Encoder], None]:
                return [AttrsEncoder]
        ```
        """
        return []

    @property
    def runserver_theme(self) -> dict[str, str]:
        """
        Returns a dictionary defining the color theme for the terminal UI
        when running the runserver.

        The theme includes styles for various elements such as tags, placeholders,
        text, selected items, results, progress indicators, errors, and log info.

        **Example**

        ```python
        from lilya.conf import Settings

        class AppSettings(Settings):
            @property
            def runserver_theme(self) -> dict[str, str]:
                return {
                    "tag.title": "white on #f11e64",
                    "tag": "white on #af1b4c",
                    "placeholder": "grey85",
                    "text": "white",
                    "selected": "#e92063",
                    "result": "grey85",
                    "progress": "on #af1b4c",
                    "error": "red",
                    "log.info": "black on blue",
                }
        ```
        """
        return {
            "tag.title": "white on #f11e64",
            "tag": "white on #af1b4c",
            "placeholder": "grey85",
            "text": "white",
            "selected": "#e92063",
            "result": "grey85",
            "progress": "on #af1b4c",
            "error": "red",
            "log.info": "black on blue",
        }

    def __hash__(self) -> int:
        values: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            values[key] = None
            if isinstance(value, (list, set)):
                values[key] = tuple(value)
            else:
                values[key] = value
        return hash((type(self),) + tuple(values))


RavynAPISettings = RavynSettings
