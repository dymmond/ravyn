from typing import Any, Optional, Sequence, Union

from pydantic import AnyUrl, BaseModel
from typing_extensions import Annotated, Doc

from ravyn.openapi.docs import (
    get_rapidoc_ui_html,
    get_redoc_html,
    get_stoplight_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from ravyn.openapi.models import Contact, License
from ravyn.openapi.openapi import get_openapi
from ravyn.openapi.schemas.v3_1_0.security_scheme import SecurityScheme
from ravyn.requests import Request
from ravyn.responses import HTMLResponse, JSONResponse
from ravyn.routing.handlers import get


class OpenAPIConfig(BaseModel):
    """
    An instance of [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/).

    This object is then used by Ravyn to create the [OpenAPI](https://ravyn.dev/openapi/) documentation.

    **Note**: Here is where the defaults for Ravyn OpenAPI are overriden and if
    this object is passed, then the previous defaults of the settings are ignored.

    !!! Tip
        This is the way you could override the defaults all in one go
        instead of doing attribute by attribute.

    **Example**

    ```python
    from ravyn import OpenAPIConfig

    openapi_config = OpenAPIConfig(
        title="Black Window",
        openapi_url="/openapi.json",
        docs_url="/docs/swagger",
        redoc_url="/docs/redoc",
    )

    app = Ravyn(openapi_config=openapi_config)
    ```

    !!! Important
        Ravyn when starting an application, checks the attributes and looks for an
        `openapi_config` parameter.

        If the parameter is not specified, `Ravyn` will automatically use the internal
        settings system to generate the default OpenAPIConfig and populate the values.
    """

    title: Annotated[
        Optional[str],
        Doc(
            """
            Title of the application/API documentation.
            """
        ),
    ] = None
    version: Annotated[
        Optional[str],
        Doc(
            """
            The version of the API documentation.
            """
        ),
    ] = None
    summary: Annotated[
        Optional[str],
        Doc(
            """
            Simple and short summary text of the application/API.
            """
        ),
    ] = None
    description: Annotated[
        Optional[str],
        Doc(
            """
            A longer and more descriptive explanation of the application/API documentation.
            """
        ),
    ] = None
    contact: Annotated[
        Optional[Contact],
        Doc(
            """
            API contact information. This is an OpenAPI schema contact, meaning, in a dictionary format compatible with OpenAPI or an instance of `ravyn.openapi.schemas.v3_1_0.contact.Contact`.
            """
        ),
    ] = None
    terms_of_service: Annotated[
        Optional[AnyUrl],
        Doc(
            """
            URL to a page that contains terms of service.
            """
        ),
    ] = None
    license: Annotated[
        Optional[License],
        Doc(
            """
            API Licensing information. This is an OpenAPI schema licence, meaning, in a dictionary format compatible with OpenAPI or an instance of `ravyn.openapi.schemas.v3_1_0.license.License`.
            """
        ),
    ] = None
    security: Annotated[
        Optional[list[SecurityScheme]],
        Doc(
            """
            API Security requirements information. This is an OpenAPI schema security, meaning, in a dictionary format compatible with OpenAPI or an instance of `ravyn.openapi.schemas.v3_1_0.security_requirement.SecurityScheme`.
            """
        ),
    ] = None
    servers: Annotated[
        Optional[list[dict[str, Union[str, Any]]]],
        Doc(
            """
            A python list with dictionary compatible with OpenAPI specification.
            """
        ),
    ] = None
    tags: Annotated[
        Optional[list[str]],
        Doc(
            """
            A list of OpenAPI compatible tag (string) information.
            """
        ),
    ] = None
    openapi_version: Annotated[
        Optional[str],
        Doc(
            """
            The version of the OpenAPI being used. Ravyn uses the version 3.1.0 by
            default and tis can be useful if you want to trick some of the existing tools
            that require a lower version.
            """
        ),
    ] = None
    openapi_url: Annotated[
        Optional[str],
        Doc(
            """
            URL of the `openapi.json` in the format of a path.

            Example: `/openapi.json.`
            """
        ),
    ] = None
    root_path_in_servers: Annotated[
        bool,
        Doc(
            """
            A `boolean` flag indicating if the root path should be included in the servers.
            """
        ),
    ] = True
    docs_url: Annotated[
        Optional[str],
        Doc(
            """
            String default relative URL where the Swagger documentation
            shall be accessed in the application.

            Example: '/docs/swagger`.
            """
        ),
    ] = None
    redoc_url: Annotated[
        Optional[str],
        Doc(
            """
            String default relative URL where the ReDoc documentation
            shall be accessed in the application.

            Example: '/docs/swagger`.
            """
        ),
    ] = None
    swagger_ui_oauth2_redirect_url: Annotated[
        Optional[str],
        Doc(
            """
            String default relative URL where the Swagger UI OAuth Redirect URL
            shall be accessed in the application.

            Example: `/docs/oauth2-redirect`.
            """
        ),
    ] = None
    redoc_js_url: Annotated[
        Optional[str],
        Doc(
            """
            String default URL where the ReDoc Javascript is located
            and used within OpenAPI documentation,

            Example: `https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js`.
            """
        ),
    ] = None
    redoc_favicon_url: Annotated[
        Optional[str],
        Doc(
            """
            String default URL where the ReDoc favicon is located
            and used within OpenAPI documentation,

            Example: `https://ravyn.dev/statics/images/favicon.ico`.
            """
        ),
    ] = None
    swagger_ui_init_oauth: Annotated[
        Optional[dict[str, Any]],
        Doc(
            """
            String default relative URL where the Swagger Init Auth documentation
            shall be accessed in the application.
            """
        ),
    ] = None
    swagger_ui_parameters: Annotated[
        Optional[dict[str, Any]],
        Doc(
            """
            A mapping with parameters to be passed onto Swagger.
            """
        ),
    ] = None
    swagger_js_url: Annotated[
        Optional[str],
        Doc(
            """
            Boolean flag indicating if the google fonts shall be used
            in the ReDoc OpenAPI Documentation.
            """
        ),
    ] = None
    swagger_css_url: Annotated[
        Optional[str],
        Doc(
            """
            String default URL where the Swagger Javascript is located
            and used within OpenAPI documentation,

            Example: `https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.1.3/swagger-ui-bundle.min.js`.
            """
        ),
    ] = None
    swagger_favicon_url: Annotated[
        Optional[str],
        Doc(
            """
            String default URL where the Swagger favicon is located
            and used within OpenAPI documentation,

            Example: `https://ravyn.dev/statics/images/favicon.ico`.
            """
        ),
    ] = None
    with_google_fonts: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if the google fonts shall be used
            in the ReDoc OpenAPI Documentation.
            """
        ),
    ] = True
    stoplight_js_url: Annotated[
        Optional[str],
        Doc(
            """
            Boolean flag indicating if the google fonts shall be used
            in the ReDoc OpenAPI Documentation.
            """
        ),
    ] = None
    stoplight_css_url: Annotated[
        Optional[str],
        Doc(
            """
            String default URL where the Stoplight CSS is located
            and used within OpenAPI documentation,

            Example: `https://unpkg.com/@stoplight/elements/styles.min.css`.
            """
        ),
    ] = None
    stoplight_url: Annotated[
        Optional[str],
        Doc(
            """
            String default relative URL where the Stoplight documentation
            shall be accessed in the application.

            Example: `/docs/elements`.
            """
        ),
    ] = None
    stoplight_favicon_url: Annotated[
        Optional[str],
        Doc(
            """
            String default URL where the Stoplight favicon is located
            and used within OpenAPI documentation,

            Example: `https://ravyn.dev/statics/images/favicon.ico`.
            """
        ),
    ] = None
    rapidoc_url: Annotated[
        Optional[str],
        Doc(
            """
            String default relative URL where the Rapidoc documentation
            shall be accessed in the application.

            Example: `/docs/rapidoc`.
            """
        ),
    ] = None
    rapidoc_js_url: Annotated[
        Optional[str],
        Doc(
            """
            String default URL where the Stoplight Javascript is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://ravyn.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = None
    rapidoc_favicon_url: Annotated[
        Optional[str],
        Doc(
            """
            String default URL where the RapiDoc favicon is located
            and used within OpenAPI documentation,

            Example: `https://ravyn.dev/statics/images/favicon.ico`.
            """
        ),
    ] = None
    webhooks: Annotated[
        Optional[Sequence[Any]],
        Doc(
            """
            This is the same principle of the `routes` but for OpenAPI webhooks.

            Read more [about webhooks](https://ravyn.dev/routing/webhooks).

            When a webhook is added, it will automatically add them into the
            OpenAPI documentation.
            """
        ),
    ] = None

    def openapi(self, app: Any) -> dict[str, Any]:
        """Loads the OpenAPI routing schema"""
        openapi_schema = get_openapi(
            app=app,
            title=self.title,
            version=self.version,
            openapi_version=self.openapi_version,
            summary=self.summary,
            description=self.description,
            routes=app.routes,
            tags=self.tags,
            servers=self.servers,
            terms_of_service=self.terms_of_service,
            contact=self.contact,
            license=self.license,
            webhooks=self.webhooks,
        )
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    def enable(self, app: Any) -> None:
        """Enables the OpenAPI documentation"""
        if self.openapi_url:
            urls = {server.get("url") for server in self.servers}
            server_urls = set(urls)

            @get(path=self.openapi_url)
            async def _openapi(request: Request) -> JSONResponse:
                root_path = request.scope.get("root_path", "").rstrip("/")

                if root_path not in server_urls:
                    if root_path and self.root_path_in_servers:
                        self.servers.insert(0, {"url": root_path})
                        server_urls.add(root_path)
                return JSONResponse(self.openapi(app))

            app.add_route(
                path="/",
                handler=_openapi,
                include_in_schema=False,
                activate_openapi=False,
            )

        if self.openapi_url and self.docs_url:

            @get(path=self.docs_url)
            async def swagger_ui_html(
                request: Request,
            ) -> HTMLResponse:  # pragma: no cover
                root_path = request.scope.get("root_path", "").rstrip("/")
                openapi_url = root_path + self.openapi_url
                oauth2_redirect_url = self.swagger_ui_oauth2_redirect_url
                if oauth2_redirect_url:
                    oauth2_redirect_url = root_path + oauth2_redirect_url
                return get_swagger_ui_html(
                    openapi_url=openapi_url,
                    title=self.title + " - Swagger UI",
                    oauth2_redirect_url=oauth2_redirect_url,
                    init_oauth=self.swagger_ui_init_oauth,
                    swagger_ui_parameters=self.swagger_ui_parameters,
                    swagger_js_url=self.swagger_js_url,
                    swagger_favicon_url=self.swagger_favicon_url,
                    swagger_css_url=self.swagger_css_url,
                )

            app.add_route(
                path="/",
                handler=swagger_ui_html,
                include_in_schema=False,
                activate_openapi=False,
            )

        if self.swagger_ui_oauth2_redirect_url:

            @get(self.swagger_ui_oauth2_redirect_url)
            async def swagger_ui_redirect(
                request: Request,
            ) -> HTMLResponse:  # pragma: no cover
                return get_swagger_ui_oauth2_redirect_html()

            app.add_route(
                path="/",
                handler=swagger_ui_redirect,
                include_in_schema=False,
                activate_openapi=False,
            )

        if self.openapi_url and self.redoc_url:

            @get(self.redoc_url)
            async def redoc_html(request: Request) -> HTMLResponse:  # pragma: no cover
                root_path = request.scope.get("root_path", "").rstrip("/")
                openapi_url = root_path + self.openapi_url
                return get_redoc_html(
                    openapi_url=openapi_url,
                    title=self.title + " - ReDoc",
                    redoc_js_url=self.redoc_js_url,
                    redoc_favicon_url=self.redoc_favicon_url,
                    with_google_fonts=self.with_google_fonts,
                )

            app.add_route(
                path="/",
                handler=redoc_html,
                include_in_schema=False,
                activate_openapi=False,
            )

        if self.openapi_url and self.stoplight_url:

            @get(self.stoplight_url)
            async def stoplight_html(
                request: Request,
            ) -> HTMLResponse:  # pragma: no cover
                root_path = request.scope.get("root_path", "").rstrip("/")
                openapi_url = root_path + self.openapi_url
                return get_stoplight_html(
                    openapi_url=openapi_url,
                    title=self.title + " - Stoplight Elements",
                    stoplight_js=self.stoplight_js_url,
                    stoplight_css=self.stoplight_css_url,
                    stoplight_favicon_url=self.stoplight_favicon_url,
                )

            app.add_route(
                path="/",
                handler=stoplight_html,
                include_in_schema=False,
                activate_openapi=False,
            )

        if self.openapi_url and self.rapidoc_url:

            @get(self.rapidoc_url)
            async def rapidoc_html(
                request: Request,
            ) -> HTMLResponse:  # pragma: no cover
                root_path = request.scope.get("root_path", "").rstrip("/")
                openapi_url = root_path + self.openapi_url

                return get_rapidoc_ui_html(
                    openapi_url=openapi_url,
                    title=self.title + " - RapiDoc",
                    rapidoc_js_url=self.rapidoc_js_url,
                    rapidoc_favicon_url=self.rapidoc_favicon_url,
                )

            app.add_route(
                path="/",
                handler=rapidoc_html,
                include_in_schema=False,
                activate_openapi=False,
            )

        app.router.activate()
