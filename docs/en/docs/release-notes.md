---
hide:
  - navigation
---

# Release Notes

## 0.2.2

### Added

- Add response parameter to exception initialization.

### Changed

- Simplified `Factory` internals for cleaner nested provider handling and async consistency.
- The Dependency Injection system now supports async providers in nested dependencies.
- GenericAlias was changed since Python 3.9+ to types.GenericAlias.

### Fixed

- Exception handler for HTTPException was not properly handling the response from the shortcuts.

## 0.2.1

### Added

- Support for Python 3.14
- Support for contrib shortcuts provided by Lilya.

## 0.2.0

### Added

- `add_controller` alternative to `add_apiview`.

### Changed

- Update `runserver` directive to reflect the new Ravyn colour palette.
- Webhooks are now inside `routing.webhooks` and the handlers redundancy was removed.
- Routing apis is now called `controllers`. For importing reasons, this is the update:

    **Before

    ```python
    from ravyn.routing.apis
    ```

    **After**

    ```python
    from ravyn.routing.controllers
    ```
- `has_permission` has changed signature.

    **Before

    ```python
    def has_permission(request, apiview)
    ```

    **After**

    ```python
    def has_permission(request, controller)
    ```
- The `routing/apiview` URL in the docs is now pointing to `routing/controllers`.

### Removed

- `Ravyn` when it was Esmerald, had the `plugglables` as parameter but since the version `3.5.0`
of Esmerald, now Ravyn, that was considered deprecated and instead the `extensions` was added. This
version now removes it for good from the internals.

---

Why is this happening? Is Esmerald going away? **No, absolutely not. Esmerald remains and will remain as is and will keep growing**
as it has its own use cases **but under a new name, Ravyn**.

The reason for the rebranding its because the ecosystem has grown a lot and Esmerald was the first tool being created.
Since then it was released as version 3+.

This happened because of internal dependencies, and we already removed all of them but goes a bit off compared to the rest
of the ecosystem.

This is the reason for Ravyn to come into existence and to keep everything aligned with the future projects coming out.

Please check the [migration guide](./migration.md) for more details about how to migrate from Esmerald to Ravyn.

## 0.1.0

We are proud to announce the **first official release of Ravyn (0.1.0)** —
the async web framework that builds on the strengths of **Esmerald** while embracing a new identity and future roadmap.

## Highlights

- **New Identity:** Esmerald has been renamed to **Ravyn**. All imports, documentation, and branding now reflect this change.

## Migration from Esmerald

This is not mandatory **at all** but if you want to start using Ravyn right away, you can simply do:

- Replace all `esmerald` imports with `ravyn`.
- No breaking changes in core APIs — projects built on Ravyn should run with minimal adjustments.

Please check the [migration guide](./migration.md) for more details about how to migrate from Esmerald to Ravyn.

Again, **Ravyn** is a rebrand of Esmerald with the same concepts, same everything.

---

## Pior to Ravyn Rebranding

---

These are the releases done under the old Esmerald name and as you can
now see, we **have rebranded to Ravyn** to align with the ecosystem plans
starting a new set of versions from the 0.1.0.

## 3.9.5

### Fixed

- Autodetection of app in cli.
- Generic lifespan support in `run` directive.

## 3.9.4

### Changed

- `@directive(display_in_cli=True)` discovery improved by showing errors and not throw directly
an exception.
- Update minimum Sayer version to 0.6.0.
- Custom directives under `@directive` are now displayed in a "Custom directives" group.

## 3.9.3

### Added

- Support for `@directive` to be display when calling `ravyn` client.
- [display_in_cli](./directives/directive-decorator.md#the-display_in_cli-option) to `@directive`.
- [Relay](./relay.md) documentation section.

## 3.9.2

### Changed

- Allow minimum Lilya to be 0.20.5
- Esmerald cli now loses the `name` argument. This is now handled directly by the newest Sayer that
was internal refactored for the `@callback`.

## 3.9.1

### Added

- `is_json` and `is_form` properties for `Request`.
- Introduced [ravyn.contrib.mail](./contrib/mail.md) providing a full-featured, async-first email framework.
- Includes a high-level `Mailer` API for sending single, multiple, and templated messages.
- Supports multipart messages (text + HTML), custom headers, attachments (in-memory or files), and metadata.
- CLI integration, `ravyn mail sendtest`, for sending quick test emails via console backend.
- [send_file](./contrib/files/send-file.md) to **contrib**.
- [jsonify](./contrib/files/jsonify.md) to **contrib**.

#### Built-in Backends

These backends are shared with [Lilya](https://lilya.dev) as they are internally used.

- **SMTPBackend**: Async-friendly with connection pooling and TLS/authentication.
- **ConsoleBackend**: Writes messages to stdout for debugging.
- **FileBackend**: Saves emails as `.eml` files for inspection or archiving.
- **InMemoryBackend**: Stores emails in memory for development or testing scenarios.

#### Application Integration

* New `setup_mail(app, backend, template_dir, attach_lifecycle=True)` utility attaches a `Mailer` to `app.state.mailer`.
* Automatically opens/closes backend connections via startup/shutdown hooks.

#### Exception Hierarchy

* `MailError`: Base exception for all mail errors.
* `BackendNotConfigured`: Raised when no backend or template renderer is configured.
* `InvalidMessage`: Raised when an `EmailMessage` is incomplete or malformed.

### Changed

- Simplify `has_permission` function calls from the internals.

## 3.9.0

### Changed

- Morph path argument into path option and expose it for all commands.

### Fixed

- Properly detect wrapped Esmerald instances.
- Fix double initialization of app in runserver.
- Fix crash in runserver when no autodiscovery.

### Internal

- Add the new `format` in the `Taskfile` and `pyproject.toml`.

### Breaking

- `ravyn runserver` loses its path argument. You can specify it via `ravyn --path foo runserver`.

## 3.8.11

### Added

- `--version` attribute when running `createapp` directive allowing to generate a versioned scaffold.
- `--location` attribute when using `createapp` and `createproject` directive allowing to specify the location to be created.

### Changed

- To make Esmerald lighter and simpler, the some minimal changes for the `SessionMiddleware` import were added.

**Before**

```python
from ravyn.middleware import SessionMiddleware
```

**After**

```python
from esmerald.middleware.sessions import SessionMiddleware
```

!!! Warning
    Esmerald `SessionMiddleware` relies on `itsdangerous` Python package. You can install it by yourself or you can install
    the `esmerald[standard]` package that brings all of the niceties of Esmerald.

In theory you don't need to worry ever about this as Esmerald injects this for you when using the `session_config` but if you
are importing directly, the previous change needs to happen.

- To make Esmerald cleaner in the installation we have now separated the installation. The [Esmerald native client](./directives/index.md)
requires some additional packages and not everyone requires this or even desires but for those already using, the change is simple.

#### Before

```shell
$ pip install esmerald
```

#### After

```shell
$ pip install esmerald[standard]
```

This brings the current behaviour of Esmerald prior to version 3.8.11 and nothing changes at all.
**This is important if you are using the `Form` or `request.form()` as this comes with the `standard` packaging.

## 3.8.10

### Changed

- Moved the `security` module imports down to use the Lilya contrib security.

### Fixed

- Handlers were not preserving the original state.
- `@cache` decorator was not allowing proper serialization when used with handler.
- Fix cache key generator for classes.
- Typos in documentation.

## 3.8.9

### Changed

- Add `wraps` to the `scheduler` decorator of Asyncz preserving the original state of the function.
- Update Lilya minimum requirements.

## 3.8.8

### Fixed

- Typing for `scheduler`.

### Changed

- Rewrite the interceptor to be on a ASGI bases and not from the base handler only. This makes it 100% ASGI compliant and
allows to use the interceptor in any level independently.
- When a scheduler is instantiated and a lifespan is detected, then it should wrap it properly automatically.

## 3.8.7

### Fixed

- Leftover `breakpoint()`

### Changed

- Reformat with ruff and really apply line length limit.

## 3.8.6

### Fixed

- The way the permissions was being manipulated, although working 100% as they should, it was not respecting the ASGI life cycle.
- ake Esmerald permissions similar to ASGI Lilya in the internal life cycle.

## 3.8.5

### Fixed

- Typo in the description of `runserver`.

### Changed

- `run` directive now injects a global context for the directive using the lilya `g`. This is available anywhere by using
`from lilya.context import g`.

## 3.8.4

### Added

- `path` to runserver allowing the user to customise the path location of an Esmerald app.
- `refreshUrl` to OAuth2PasswordBearer.
- Missing `json_schema_extra` into the parameters.

### Changed

- Make `reload` in the runserver `False` by default.
- Minimum default of Lilya as base.

### Fixed

- Allowed hosts return default.

## 3.8.3

### Added

- Support for a second form of declaring [directives](./directives/directive-decorator.md).
- Support for `@directive` decorator on top of a [Sayer](https://sayer.dymmond.com) command making it a directive as
long as it still follows the directive lookup for files.

### Fixed

- `EsmeraldAPISettings` was not properly declared for backwards compatibility.
- Migration to Sayer missed the `run` directive argument required as False.
- Fix a regression on `EsmeraldAPISettings` when importing from `esmerald`.
- Broken documentation references.

## 3.8.2

### Added

- Missing `logging_level` in the EsmeraldAPISettings.
- New naming convention for `EsmeraldAPISettings` to be now called `EsmeraldSettings`. The old `EsmeraldAPISettings` will remain
as is for backwards compatibility but it will eventually be removed in the future.

### Changed

- Upgraded the internal requirements and Lilya.
- Revamped `runserver` to be modern and more informative.
- Updated the documentation for the `EsmeraldSettings`.

## 3.8.1

### Changed

- Update to latest mypy and removed old code.
- Updated the internals to support the latest Lilya version.
- Make sure the str types when annotations are passed and parsed are discovered by `get_type_hints` when the create signature is triggered.

### Fixed

- Documentation references.

## 3.8.0

Due to advanced changes in the internals of Esmerald, this release is a major one and it will be under the version `3.8`
and it will follow Lilya's integration which means, we will be dropping the support for Python 3.9 and focus solely on 3.10+
for syntaxes and tooling.

### Added

- Integration with the newest client, [Sayer](https://sayer.dymmond.com). This brings a whole new experience to the Esmerald
cli and allows to have a more interactive experience with the framework.

### Changed

- Drop support for Python 3.9 due technology advancements.

## 3.7.8

### Fixed

- Bump Lilya version
- Removed constraints for rich.
- Fixed `runserver` extra display message.
- Fix for new click versions.
- Fix redis cache.
- Fix memory cache (it was much slower as it had to be).

## 3.7.7

### Changed

- Added warning message to `runserver` explaining the usage in development mode only.
- Lazy evaluate the environment variable for the settings import. This relaxes the restraints on the import order.
  You can e.g. import lilya settings before adjusting `ESMERALD_SETTINGS_MODULE` as long as you don't access the settings object.


### Fixed

- Typing for the handlers (@get, @post...) that was causing mypy to give false positives.
- Documentation examples.
- Documentation references.
- `encoders` ENCODER_TYPES was a static snapshot of a ContextVar. Leverage a TransparentCage instead.

## 3.7.6

### Changed

- `esmerald createproject <PROJECT-NAME> --edgy` Now generates the settings also plugged with `DatabaseSettings` automatically.
- Bump internal Lilya version to 0.13.0 minimum.
- `esmerald.logging` is now delegated to the thread-safe version of `lilya.logging`. Nothing changes in the Esmerald
interface.

## 3.7.5

### Added

- New [LoggingConfig](./configurations/logging.md) for the logging configuration. This now allows you to setup
your own logging system and plug it with anything you want and then use the global logger from Esmerald to log your
messages by simply using:

```python
from esmerald.logging import logger

logger.info("My message in my logger.")
```
- `StandardLogging` as the new default logging system of Esmerald, removing the dependency of `loguru` and make this one
optional.

!!! Warning
    If you use loguru and this might now "break" your code, simple run `pip install loguru` and add it into your dependencies.

- New `esmerald createproject --edgy <PROJECT-NAME>` directive to create a new project with the scaffold for Edgy ORM.

### Changed

- As part the continuous effort to make Esmerald cleaner, the `esmerald.protocols` now lives inside `esmerald.core.protocols`.
The only thing that needs changing **its just that small import**. The rest remains the same.

### Fixed

- Typing for handler on Gateway/WebSocketGateway.
- Partial imports on handlers.

## 3.7.4

### Fixed

- Partial imports on CSRF typing was causing the app to sometimes crash.
- Partial imports in types was causing the asyncz tests to crash.

### Changed

- Move router methods in a mixin, so we have it in only two places.

## 3.7.3

### Changed

- Bump Lilya version.
- Update settings loading module with [Monkay](https://monkay.dymmond.com).
- Change base of Esmerald to BaseLilya.
- `whead` renamed to `whhead` for naming consistency.
- Monkay lazy loading now its at the `__init__` of Esmerald.

### Deprecated

- [Saffier](https://saffier.tarsild.io) was the beginning of a big journey to what it later on became [Edgy](https://edgy.dymmond.com)
and for that reason, it makes no longer sense of keeping the support where Saffier is not growing as the same as Edgy.

!!! Note
    [Saffier](https://saffier.tarsild.io) is under the name of its creator and he is more than happy to donate the ORM and the pypi
    package to anyone who would like to continue maintaining it.

### Breaking Change

- This is not 100% sure but since passlib stopped maintenance a long time ago, since python 3.13 some other issues will
arise and therefore the decision to move away from it to bcrypt. Unfortunately this means that the `password` hashing will not be compatible with the previous versions of Esmerald and
we know this might not be ideal but this is the best way to move forward due to security constraints.

## 3.7.2

### Changed

- `esmerald shell` now also imports the `reverse` function from Lilya to make it simpler to test in the command-line.
- `esmerald.routing.views` to import the APIView must now be done via `esmerald.routing.apis`. The reason for this change
it was to keep the consistency in the codebase. Previously it was just an alias.

### Fixed

- `esmerald show_urls` was displaying an extra parameter in the reverse lookup.

### Removed

- `memory_cache` as this is not documented and should not be used. This is a leftover from internal testing.

## 3.7.1

!!! Warning
    This release introduces some import changes as part of the ongoing internal restructure of Esmerald.
    This will be done in different phases during different releasing but you can already see the **Changed**
    section to understand where the new imports must be done. Very likely that you won't need to do this but
    those serve as a reference.

### Added

- When using `Requires` and a callable is not passed, Esmerald will generate a lambda callable automatically.
- New [experimental](./experimental/index.md) documentation section with the new features that are being tested.
- New [gRPC](./experimental/grpc.md) documentation section with the new gRPC functionality.
- New `wrap_middleware` from `esmerald.utils.middleware`. This serves as alternative when setting up a middleware
which **also allows** the fully module naming to be passed.

    ```python
    from esmerald.utils.middleware import wrap_middleware
    ```

- New [Learning and Examples](./guides/index.md) section. This section will be growing in time and will help newcomers
to understand a bit more about Esmerald.

#### Experimental

- [GRPC](./experimental/grpc.md) - Support for GRPC endpoints and introduction to the newly `GrpcGateway` wrapper. This functionality
is experimental to test in the next releases. If successful, it will be marked as final.

### Fixed

- Bump Pydantic internal version to 2.11+.

### Changed

The following **must be updated if you are using any of these**.

This is now part of the phase migration of modules to make them more consistent and easier to use.

- `esmerald.datastructures` is now `esmerald.core.datastructures`.
- `esmerald.caches` is now `esmerald.core.caches`.
- `esmerald.config` is now `esmerald.core.config`.
- `esmerald.interceptors` is now `esmerald.core.interceptors`.
- `esmerald.transformers` is now `esmerald.core.transformers`.

## 3.7.0

### Added

- Decorator `controller`. This decorator allows to, as the name suggests, create a controller from
a normal python objects. This is a simple way of creating a controller without the need of subclassing the `Controller` class.
- [Decorators](./decorators.md) documentation section with the available Esmerald decorators.
- Support for [**native** caching](./caching.md) with support for custom backends.
- [Observables](./observables.md) documentation section. This is a new feature that allows to create
observables that can be used to create a more reactive programming style.

#### Example

```python
from esmerald.utils.decorators import controller
from esmerald import get, post

@controller(path="/items")
class ItemHandler:

    @get("/{item_id}")
    async def get_item(self, item_id: int) -> dict:
        return {"item_id": item_id}

    @post("/")
    async def create_item(self, data: dict) -> dict:
        return {"message": "Item created", "data": data}
```

The rest remains as per normal usage of Esmerald.

## 3.6.8

### Added

- Esmerald now allows the import of Lilya EnvironLoader directly using it directly via:

    ```python
    from esmerald.utils.environments import EnvironmentLoader
    ```

- [Factory](./dependencies.md) now accepts `kwargs` parameters.
- You can now declare dependencies [without using explicitly the `Inject()`](./dependencies.md#use-without-inject).

### Changed

- Event lifecycle fully delegated to Lilya internals removing duplication.
- Cleanup internals for the path and delegate to Lilya.
- Background tasks pointing 100% to Lilya.
- Moved `concurrecy` to `esmerald.utils.concurrency`.
- Moved `esmerald.enums` to `esmerald.utils.enums`.
- Refactored `parse_form_data` from `esmerald.parsers` into a cleaner version.

### Fixed

- Documentation pointing to the state of the CI.

### Removed

- Official support for Mako template engine as previously announced.

## 3.6.7

### Added

- `before_request` and `after_request` WebSocketGateway handler added.
- `before_request` and `after_request` added as default to the settings. This was not required
as the settings loading system of Esmerald defaults values but this should be added to the settings
for consistency reasons of the framework.

### Changed

- Reverse order on Gateway `after_request`.

### Fixed

- `override_settings` was not taking into account async functions.

## 3.6.6

### Added

- `Esmerald`, `Include`, `Host`, `Gateway`, `HTTPHandler` and `Router` now support `before_request` and `after_request`
life cycles. This can be particularly useful to those who want to perform actions before and after
a request is performed. E.g.: Telemetry.
- Missing before and after request in the handler helpers.
- `BaseController` alias for the `View`. This serves a preparation for the internal renaming.

### Fixed

- Internal permission checking for Lilya and Esmerald was not extended to `View` base of Controllers.
- Inheritance extending previous permissions on Controllers.

## 3.6.5

### Added

- Esmerald now **also** supports **Pure ASGI Permissions**. That means you can pass the same
style of permissions as the ones used in Lilya as alternative to the native Esmerald permission
system.
- New [Lilya permissions](./permissions/lilya.md) documentation section.

### Changed

- [Permissions section](./permissions/ravyn.md) moved and renamed to Esmerald Permissions.

### Fixed

- `set_cookie` was causing an issue when multiple were being generated.

## 3.6.4

### Added

- Support for `async` jinja templates.
- Missing `esmerald --version` command to the cli.

### Changed

- Removed hard dependency of `nest_asyncio`.
- Use ORJSON as parsing json.

### Fixed

- Internal pattern for OAuth2 form password.
- Fixed internal typings of passthrough in Response and TemplateResponse.
- Esmerald permissions on Include were being overriten by Lilya too early.

## 3.6.3

### Added

- [Requires()](./dependencies.md#requires-and-security) as a new independent way to manage dependencies.
- A more thorough explanation about the [Security()](./dependencies.md#requires-and-security), how to use it and examples.

### Changed

- Expose `Controller` in `esmerald` as alternative to `APIView`. This was already available to use but not directly
accessible via `from esmerald import Controller`.

### Fixed

- Fix escaped " in TemplateResponse.
- Fix TemplateResponse's auto-detection of the media-type when used directly.
- Don't mangle strings by default for other media-types than json.
- Don't mangle returned responses.
- Reverse lookup or Class based views and nested naming using `path_for`

## 3.6.2

### Added

- `name` parameter to StaticFiles config allowing to reverse lookup internally.
- Support for Python 3.13
- Support for `redirect_slashes` in the Include.
- `status_code` to ResponseContainer to be parameter detectable.

### Changed

- Cleanup Response.
- Move `transform` method to lilya but provide speedup in a mixin.
- Esmerald `Response` behaves like `make_response` in lilya with a plain `Response`.
- Special handle None (nothing is returned) in `Response`. It shouldn't map to `null` so not all handlers have to return a value.

### Fixed

- `data` and `payload` special kwargs are now allowed when a not-bodyless method is available for the handler. They default to None.
- `bytes` won't be encoded as json when returned from a handler. This would unexpectly lead to a base64 encoding.
- SessionConfig has a unneccessarily heavily restricted secret_key parameter.
- Gracefully handle situations where cookies are None in `get_cookies`.
- Fix validation of parameters requiring a body.

## 3.6.1

### Added

- Allow passing extensions as string.

### Changed

- Change `media_type` parameter of `Response` from `MediaType.JSON` to `None` to match the default of the underlying lilya Response.

### Fixed

- OpenAPI responses.
- Enum definitions.

## 3.6.0

### Added

- New [Security](./security/index.md) section with all the explanations how to use the internals of Esmerald.
- Added new `Security` object used for security dependencies using Esmerald `esmerald.security` package.

### Changed

- Updates from python-jose to PyJWT as dependency contrib library.
- Remove OpenAPI security as they where redundant and not 100% compliant with OpenAPI security.
- Allow the new Lilya StaticFiles allowing to provide multiple directories with fallthrough behaviour.
- Deprecate support for Mako.
- Internal code organisation and cleaning.

### Fixed

- Fix cli detection of wrapped esmerald instances or different ASGI servers.
- Allow passing multiple `StaticFilesConfig` configurations in a tuple.
- Allow passing multiple directories to `StaticFiles` by removing the stringification in `StaticFilesConfig` so a fallthrough behavior can be established.
  Note: this requires a newer lilya version.

## 3.5.1

### Changed

- Use assigned encoders at requests for json_encoder.
- Allow overwriting the `LILYA_ENCODER_TYPES` for different encoder sets or tests.
- Use more OrJSON for encoding requests.

## 3.5.0

### Added

- Allow passing HTTP/WebSocket handlers directly to routes. They are automatically wrapped in Gateways-
- Allow passing HTTP/WebSocket handlers directly to routes as alternative to defining a Gateway/WebsocketGateway.

### Changed

- Esmerald is now under the License BSD-3. This aims to protect the maintainers and contributors and
the license will be now the final.
- Pluggables can now receive plain Extensions and Extension classes.
- Rename of Pluggables to Extensions:
    - **Breaking**: The `pluggables` attribute and parameter are now renamed to `extensions`. The old name is still available but deprecated.
    - **Breaking**: The `add_pluggable` method is now renamed to `add_extension`. The old name is still available but deprecated.
    - The documentation will refer now to extensions with `Pluggable` as a setup wrapper.

### Fixed

- Directive `runserver` now allows the use of ASGI middlewares.
- Remove the dependency of an app being an `esmerald` instance for `runserver`.
- Check the environment variables instead of settings variable for esmerald settings in the runserver.

## 3.4.4

### Added

- Support for [Taskfile](https://taskfile.dev) when generating a project via directive.
- Add taskfile for development mode.

### Changed

- Internal JSONResponse is now natively supporting ORJSON.

## 3.4.3

### Changed

- PydanticEncoder now tries mode `json` first as default.
- Stop ignoring warnings in the tests.
- Stop shadowing the BaseDirective `help` from Lilya.
- Asyncz settings for empty tasks.
- Update the docs for the templates.

## 3.4.2

### Changed

- OpenAPI for inheritance models using pydantic or any type of encoders.
- Stop supporting Python 3.8.
- Changed internal schema location in the helpers.

## 3.4.1

### Changed

- OpenAPI now if no `description` is provided from the handlers, it will read directly from
the docstrings.
- Internal code cleaning and organisation.

### Fixed

- OpenAPI query parameters were not rendering properly for optional `dict` or `list` types. This
was due to the internal evaluation of the `None` field which is now skipping for OpenAPI purposes.

#### Example

Now it is possible to do something like this:

```python
from typing import Dict, List, Union, Optional

from esmerald import Gateway, JSONResponse, Query, get


@get("/item")
async def check_item(q: Union[List[str], None]) -> JSONResponse:
    return JSONResponse({"value": q})


@get("/another-item")
async def check_item(q: Optional[Dict[str, str]]) -> JSONResponse:
    return JSONResponse({"value": q})
```

## 3.4.0

### Added

- New ways of providing the [request data](./extras/request-data.md) allowing to pass a more complex body
using also the [encoders](./encoders.md). The [complex body](./extras/request-data.md#complex-request-data) is explained
and how to achieve this result.

!!! Warning
    This is an **additional** functionality to the existing one and it does not represent any replacement. Be sure
    you read the [documentation](./extras/request-data.md) and if you understand it.

#### Example

As per some examples of the documentation:

```python
from pydantic import BaseModel, EmailStr

from esmerald import Esmerald, Gateway, post


class User(BaseModel):
    name: str
    email: EmailStr


class Address(BaseModel):
    street_name: str
    post_code: str


@post("/create")
async def create_user(user: User, address: Address) -> None:
    """
    Creates a user in the system and does not return anything.
    Default status_code: 201
    """


app = Esmerald(routes=[Gateway(handler=create_user)])
```

You can expect to send a payload like this:

```json
{
    "user": {
        "name": "John",
        "email": "john.doe@example.com",
    },
    "address": {
        "street_name": "123 Queens Park",
        "post_code": "90241"
    }
}
```

More details can and must be read in the [request data](./extras/request-data.md) section.

### Changed

- Overriding the `status_code` in any response is now possible directly by specifying the intended response and ignoring
the default from the `handler`.

#### Example

```python
@get()
def create(name: Union[str, None]) -> Response:
    if name is None:
        return Response("Ok")
    if name == "something":
        return Response("Ok", status_code=status.HTTP_401_UNAUTHORIZED)
    if name == "something-else":
        return Response("Ok", status_code=status.HTTP_300_MULTIPLE_CHOICES)
```

If none of the conditions are met, then it will always default to the `status_code` of the handler which in the `get` case,
its `200`.

### Fixed

- Internal parsing of the encoders for OpenAPI representation and removed unused code *(deprecated)*.

## 3.3.7

### Added

- New application generator using `--context` allowing to generate application scaffolds containing
more complex structures.

### Changed

- jinja2 templating is now 100% delegated to its base, Lilya.
- Added examples in the documentation for windows users.

### Fixed

- Lookup for summary in the handler for OpenAPI.

## 3.3.6

### Added

- `allow_private_networks` property to `CORSMiddleware`.

### Changed

- `Gateway` now allows to pass also an optional `operation_id` as parameter for OpenAPI documentation allowing
multiple gateways to use the same handler and being recognised automatically by OpenAPI documentation.
- OpenAPI documentation when multiple gateways use the same handler and no `operation_id` is declared,
automatically tries to generate a unique `operation_id` for it.
- Internal code organisation for class based `View` to generate the routes in one place and reducing
code duplication.
- Updated internal testing requirements for Edgy and Saffier and Lilya.

## 3.3.5

This was missed from the release [3.3.4](#334) and it was supposed to be included.

### Added

- Native types for Esmerald transformer models/
- Hashing list internally for the signature allowing lists to be declared for OpenAPI representation.

### Changed

- Query parameters when declared as `list`, `List`, `dict` and `Dict` automatically parses the values
to the declared type.
- OpenAPI understands the native types, objects and lists (arrays).

## 3.3.4

### Added

- Missing documentation for [Query Parameters](./extras/query-params.md) and [Path Parameters](./extras/path-params.md).

### Changed

- Documentation for `Extra, Advanced && Useful` is now renamed `Advanced & Useful` and its located in the `Features`
section.
- Removed unused internal functions for validations now used by Esmerald encoders.

### Fixed

- Regression caused by the introduction of the dynamic encoders when diplaying the query parameters in the OpenAPI
documentation.
- Annotation discovery for the Signature.

## 3.3.3

### Changed

- Internal implementation of the exceptions.
- Removed redundant exception declaration and delegate the internals to Lilya.
- Internal code cleaning.

### Added

- [ValidationError](./exceptions.md#validatorerror) for custom independent raising exceptions within
any Esmerald application

### Fixed

- `is_server_error` for dependencies was causing an exception to be raised in a `loc[-1]`.

## 3.3.2

### Changed

- Update the internals of contrib for Asyncz to match the new Asyncz specifications and API.

## 3.3.1

### Changed

- Automatic detection of a response for a default status code when using OpenAPI documentation.
- Addressing `from __future__ import annotation` when using the dependency injection defaulting to Any.

## 3.3.0

### Fixed

- Fixes `PydanticEncoder` when checking for subclasses of `BaseModel` causing the dependency injection to fail
for those specific types

### Added

- Esmerald is ow using `python-slugify` instead of `awesome-slugify` for internals.
- OpenAPI Schemas Pydantic is now fully integrated with Esmerald OpenAPI.
- Esmerald now supports `app` as decorator prodiving another way of declaring the routing.

#### Example

```python
#!/usr/bin/env python
import uvicorn

from esmerald import Esmerald, Gateway, JSONResponse, Request, get


app = Esmerald()


@app.get("/esmerald")
def welcome() -> JSONResponse:
    return JSONResponse({"message": "Welcome to Esmerald"})


@app.get("/esmerald/{user}")
def user(user: str) -> JSONResponse:
    return JSONResponse({"message": f"Welcome to Esmerald, {user}"})


@app.get("/esmerald/in-request/{user}")
def user_in_request(request: Request) -> JSONResponse:
    user = request.path_params["user"]
    return JSONResponse({"message": f"Welcome to Esmerald, {user}"})


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
```

The same is also applied to the `Router` object.

## 3.2.7

This was missed from version [3.2.6](#326).

### Changed

- Removed unused middleware.
- Updated AppSettingsMiddleware for lazy loading
- Updated `globalise_settings`.

### Fixed

- Performance issues caused by `AppSettingsModule`.

## 3.2.6

### Added

- `XFrameOptionsMiddleware` to handle with options headers.
- `SecurityMiddleware` adding various security headers to the request/response lifecycle.
- `override_settings` as new decorator that allows to override the Esmerald settings in any given test.
- New `--simple` flag for `createproject` directive generating simple structured projects.
- Integration with new `rapidoc` as another alternative to display the OpenAPI docs.

### Changed

- Internal `asyncz` decorator inside a wrapper.
- Updated pydantic an lilya requirements.

## 3.2.5

### Fixed

- Added missing options into get_scheduler of AsynczConfig.

## 3.2.4

### Added

!!! danger
	This new version deprecates an old style declaring the scheduler for Esmerald.
	There is a new [SchedulerConfig](./configurations/scheduler.md).

- New [SchedulerConfig](./configurations/scheduler.md) interface for Esmerald schedulers and
custom schedulers.
- New [AsynczConfig]() that implements the configuration for Asyncz scheduler.
- New `scheduler_config` parameter to Esmerald and EsmeraldAPISettings.

### Changed

- Deprecate `scheduler_class`, `scheduler_configurations` and `scheduler_tasks`
in favour of the new [SchedulerConfig](./configurations/scheduler.md) approach.
- Deprecate the use of the `EsmeraldScheduler`.

#### Breaking changes

You must update the imports to be:

From:

```python
from asyncz.contrib.esmerald.decorator import scheduler
```

To:

```python
from esmerald.contrib.schedulers.asyncz.decorator import scheduler
```

Check the documentation about the [Scheduler](https://www.esmerald.dev/scheduler/scheduler/), [handlers](https://www.esmerald.dev/scheduler/handler/) and the [SchedulerConfig](./configurations/scheduler.md) to
see how to update your current project to the new version with the minimum disruption.

This change should not break existing functionality, instead, its just an update to make it more modular.
There is an [example](https://github.com/dymmond/scheduler-example) how to simply use this.

### Fixed

- Added missing options `--settings` into the `runserver` directive.

## 3.2.3

### Changed

- `EsmeraldScheduler` integration with Asyncz is not assembled before the configuration of the routing,
allowing multiple events to be triggered without overriding.

## 3.2.2

These changes were missed from the version 3.2.1

### Changed

- Updated the default scheduler class to be in the configuration.
- Internal Dispatcher implemented for the routing and response handlers update.

## 3.2.1

### Changed

- `Context` is not inheriting directly from Lilya.

### Fixed

- The default `scheduler_class` internal settings validation.

## 3.2.0

### Added

- `settings_module` also supports import as string.
- New `encoders` to Esmerald settings and instance parameters.
- New `register_encoder` encoder in any Esmerald and ChildEsmerald instances.
- New `encoders` to Esmerald responses. This allows to use any Response as ASGI application.
with unique custom encoders.
- [Encoders](./encoders.md) documentation.

### Changed

- Internal refactor of the `classmethods` of the `TransformerModel`. The class methods
are now normal python functions.
- Unifying the transformers in the signature model.
- Rename `EsmeraldSignature` to `SignatureModel`.

## 3.1.5

### Added

This change was supposed to be shipped in the version [3.1.4](#314) but it missed the release.

- Printing the stack trace when an Esmerald application is in `debug=True` providing a deeper
level of understanding the source of the errors.

## 3.1.4

### Fixed

- AsyncExitMiddleware raising exception.
- OpenAPI error when generating the parameters with dependencies.
- OpenAPI security schemes.

## 3.1.3

### Changed

- Internal support for `hatch` and removed the need for a `Makefile`.
- Internals for Directives. [#308](https://github.com/dymmond/esmerald/pull/308) by [@devkral](https://github.com/devkral).
- Documentation references and refinements [#311](https://github.com/dymmond/esmerald/pull/311) by [@paolodina](https://github.com/paolodina).
- `WSGIMiddleware` is now pointing to Lilya.

## 3.1.2

### Fixed

- Regression with `typing_extensions`.

## 3.1.1

### Added

- `--with-basic-controller` flag in `createapp` directive. [#PR 284](https://github.com/dymmond/esmerald/pull/284) by [@tarsil](https://github.com/tarsil).

### Changed

- Documentation improvements.

### Fixed

- Typo in the create project directive urls file descripton.
- `operation_id` being generated to include the class based view name when coming from class based views handlers. [#PR 289](https://github.com/dymmond/esmerald/pull/289) by [@tarsil](https://github.com/tarsil).

## 3.1.0

### Added

- `settings_module` when passed in the instance of Esmerald will take precedence
over the global settings, removing the need of using constantly the `ESMERALD_SETTINGS_MODULE`.
- `ApplicationSettingsMiddleware` as internal that handles with the `settings_module` provided and maps
the context of the settings.

### Example of the way the settings are evaluated

```python
from esmerald import Esmerald, EsmeraldAPISettings, Gateway, Include, JSONResponse, get, settings


@get()
async def home() -> JSONResponse:
    return JSONResponse({"title": settings.title})


class NewSettings(EsmeraldAPISettings):
    title: str = "Main app"


class NestedAppSettings(EsmeraldAPISettings):
    title: str = "Nested app"


app = Esmerald(
    settings_module=NewSettings,
    routes=[
        Gateway("/home", handler=home),
        Include(
            "/child",
            app=Esmerald(
                settings_module=NestedAppSettings,
                routes=[
                    Gateway("/home", handler=home),
                ],
            ),
        ),
    ],
)
```

In the context of the `controller home`, based on the path being called, it should return the
corresponding value of the `title` according to the settings of the app that is included.

### Changed

- `createapp` directive `views.py` file generated renamed to `controllers.py`.
- Make the `EsmeraldAPISettings` hashable.
- Remove `settings_config` in favor of the `settings_module`.
- Bump Lilya version to 0.3.3.

### Fixed

- Documentation references. [#PR 282](https://github.com/dymmond/esmerald/pull/282) by [@DJWOMS](https://github.com/DJWOMS)

## 3.0.0

### Changed

- Moved from beta v3 version to the official v3 of Esmerald fully supporting [Lilya](https://lilya.dev).

## 3.0.0-beta2

### Added

- Allow the use `from lilya.middleware import Middleware` as alternative to `DefineMiddleware`,

### Changed

- Cleaned the `ServerErrorMiddleware` from the lilya import.

## 3.0.0-beta1

!!! Warning
	This is a major release and it will be under the the version `3` of Esmerald.
	You should not be affected but in case you are, please report any issues
	so we can correct it.

### Added

- Support for `Lilya` and drop `Starlette`.

### Changed

- `CSRFConfig` `cookie_secure` renamed to `secure`.
- `CSRFConfig` `httponly` renamed to `httponly`.
- `CSRFConfig` `cookie_samesite` renamed to `samesite`.
- `CSRFConfig` `cookie_domain` renamed to `domain`.
- `CSRFConfig` `cookie_secure` renamed to `secure`.
- Removed support for the `BasicMiddleware` as this can be imported from any other ASGI application.

#### Internal

In the past, `Middleware` was being used but with the introduction of Lilya, now is `DefineMiddleware` that
is applied.

```python
from lilya.middleware import DefineMiddleware
```

- The `PlainTextResponse` was renamed to `PlainText`.

## 2.7.4

### Fixed

- `WSGIMiddleware` optional was being called in the core middlewares.

## 2.7.3

### Added

- Allowing `app` to load as a string as alternative to an object inside the `Include`.

### Changed

- Internal code for lazy objects.
- Make `a2wsgi` optional for `WSGIMiddleware`.
- `httpx` is now only a depedency for testing.
- Cleared some core dependencies.

## 2.7.2

### Changed

- Security update for python multipart.
- Update minimum Starlette requirement.

## 2.7.1

### Added

- `settings_module` as replacement for `settings_config`.
- Deprecation warning for `settings_config` in favour of `settings_module` parameter.

### Changed

- Added improvements to the scaffold generated by `esmerald createproject` in the tests.
- Added extra origin type for when a MsgSpec Struct is passed in the payload of a handler.

### Fixed

- OpenAPI Tags not loading from top down if handler had `tags=None`.
- TestClient to allow passing pluggables inside `create_client`.

## 2.7.0

### Changed

- `Token.decode()` is now a `classmethod`. This allows to subclass the `Token` and add extra fields into the model
allowing operations like `encode()` with extra claims. This can be useful for situations like claiming a `refresh` or `access` token.
- Internal handlers decorators are now wrapped in a function decorator. This does not affect anything but allows more control over the middleware
calls to async ASGI applications.

### Fixed

- OpenAPI when overriding the response for the default status codes of the handlers.

## 2.6.0

### Added

- New [createdeployment](./directives/directives.md#create-deployment) directive allowing
the generation of deployment scaffolds for any Esmerald project.

### Changed

- Added `requirements` to the `createproject` directive generating the minimum requirements
for an Esmerald project.

### Fixed

- `BaseAuthentication` for `self.app` when its of the type of HTTPHandler and WebSocketHandler.

## 2.5.0

### Changed

- Upgraded internal dependencies.
- The internals for the middleware are now delegated to Starlette directly.
- Middlewares of Gateway and WebSocket Gateways are now delegated to Starlette.

### Fixed

- Internals to be compliant with new version of Starlette.
- Building middleware stack for the `Middleware` object.
- Internal testing to reflect the new way of the `Include` to be compliant with the ASGI spec.


## 2.4.3

### Fixed

- OpenAPI `contact` it was not parsing properly on transformation.
- Rename `include` attribute from `Param` (base) and call `include_in_schema`.
- Missing `nest_asyncio` dependency when using `esmerald shell`.

## 2.4.2

### Changed

- Pin starlette version to `0.32.0.post1`

## 2.4.1

### Fix

- Regression when performing a `model_dump` of pydantic models in the responses.
- Re-enable `orjson` for generic response parsing.

## 2.4.0

### Changed

- Updated SwaggerUI version.
- Updated [responses](./responses.md) with a `msgspec` response example.

### Added

- Support for [payload](./extras/request-data.md) as alternative to `data`. This aims
to make the process more intuitive and easy to implement. [#199](https://github.com/dymmond/esmerald/pull/199).
- [Context](./context.md) - The new context object for the [handlers](https://esmerald.dev/routing/handlers/).
- Support for [msgspec](./msgspec.md) natively allowing to have more than just Pydantic.

!!! Note
    Esmerald is not fully tight with Pydantic which means it's more flexible and extendible and allows more versatility.

### Fixed

- Missing [Request](./requests.md) document.
- Removed the use of `random` for the secrets in favour of the `secrets` library instead.
- Contrib documentation updates regarding the Authorization headers.

## 2.3.1

### Fixed

- `Middleware` as an independent ASGI app on an `Include` level.

!!! Warning
    This was supposed to go in the release [2.3.0](#230) but it was not merged on time to make the
    release.

## 2.3.0

### Changed

- OpenAPI fields are permanently moved to [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/)
making the codebase cleaner. The options are still available via `settings` in case of wanting to
override the defaults but not via instantiation parameters. Via instantiation the `OpenAPIConfig` is the
one to be used.

!!! Warning
	This is a breaking change. The functionality itself still works as it is supposed to but from now on
	instead of passing via Esmerald instance, you need to pass the variables via [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/).
	object instead.

### Added

- Annotated for documentation generators.
- Add new documentation structure for Esmerald base.
- Add [API Reference](http://esmerald.dev/references/) . [#196](https://github.com/dymmond/esmerald/pull/196)

### Fixed

- Allow tags for levels. When a tag is added to an `Include`, `Gateway`, or any other level,
the tags are appended to the final handler. This allows inheriting from existing tags for OpenAPI.
- `Middleware` on levels treating each level as an independent ASGI app.

## 2.2.0

### Changed

- Updated `OpenAPIConfig` documentation.
- Deprecate `v1`. Esmerald prior to version 2.0 is no longer supported.

### Added

-  Allow importing from from string into `Factory`. [#179](https://github.com/dymmond/esmerald/pull/179) by [@tarsil](https://github.com/tarsil).
-  New security objects for OpenAPI documentation.
-  New [OpenAPI](./openapi.md) documentation describing the ways of using it and what is available with examples.
-  New [SimpleAPIView](./routing/controller.md#simpleapiview) supported.
-  New [CreateAPIView](./routing/controller.md#createapiview) supported.
-  New [ReadAPIView](./routing/controller.md#readapiview) supported.
-  New [DeleteAPIView](./routing/controller.md#deleteapiview) supported.
-  New [ListAPIView](./routing/controller.md#listapiview) supported.

### Fixed

- OpenAPI `security` was not working as intended.


## 2.1.0

### Changed

- Update base requirements and pydantic to 2.4.

### Added

- New Factory added for dependency injection allowing to pass any time via Factory instantiation. [PR #163](https://github.com/dymmond/esmerald/pull/163) by [@ShahriyarR](https://github.com/ShahriyarR).
- Support for [Mongoz](https://mongoz.tarsild.io) showcasing how to integrate Esmerald with an ODM (MongoDB).
- Documentation about how to use Esmerald contrib with [Mongoz](./databases/mongoz/motivation.md).

### Fixed

- Typos in the documentation.
- Pydantic 2.4 compatibility and updating to new names for the functions.

## 2.0.6

### Changed

- Updated requirements for Pydantic and Starlette.
- Removed unnecessary dependencies.

### Added

- Support for async `has_permission` on Permissions.
- Add new landing page.

### Fixed

- `email-validator` error being thrown from `openapi-schemas-pydantic` requirement.

## 2.0.5

### Changed

- Updated the way `esmerald` client operates internally.
- Updated internal minimum requirements.

### Fix

- Regression in OpenAPI when adding middleware to `Gateway` or `HTTPHandler`. When a middleware
was added, the OpenAPI would not generate the docs for it. The API would still work but not OpenAPI
docs.

## 2.0.4

### Changed

- Updated functional internal crypto to only use the system random.
- Cleaner codebase for the application settings.
- Updated version of Asyncz to be at least 0.5.0.

### Added

- Custom exception handlers, `from esmerald.exception_handlers import value_error_handler`.
- New native exception handler for pydantic v2 Validation errors in general.
- Dataclasses (normal and Pydantic dataclases) are now supported as Esmerald Responses.
- Support for [OpenAPI Webhooks](./routing/webhooks.md).
- Improved [Responses](./responses.md) documentation with examples using Pydantic BaseModel and dataclasses.
- OpenAPI Spotlight Elements documentation. When starting the application, accesing the default `/docs/elements`.
- Support for [Edgy](https://edgy.tarsild.io) ORM. [Docs here](https://esmerald.dev/databases/edgy/motivation/).

### Fixed

- Removed old pydantic v1 syntax from tests and applications.
- `add_include()` that wasn't generating signature models upon import.
- OpenAPI query params with defaults weren't loading properly.

## 2.0.3

!!! Note
    This addition was supposed to go in the release [2.0.2](#202) but somehow it was missed in the merge of
    the pull requests. It is not a bug fix but instead is a simple new
    [directive](./directives/shell.md) that can be useful for those who like using the command-line.

    It is important to understand that this support **won't be available on releases** of Esmerald
    1.X.

### Added

- [Interactive shell](./directives/shell.md) support directive for any Esmerald application.

## 2.0.2

### Changed

- Updated Field, Form and Body from `esmerald.params` with current defaults.
- Removed redundant cast from `File` to `Body` as it is a subclass.

### Added

- Added `strict` and `max_digits` esmerald params `esmerald.params`.
- Deprecate `example` as OpenAPI 3.10 supports `examples`. Use examples instead of `example`.

### Fixed

- [UploadFile](./extras/upload-files.md) sending as a list and as normal.
This got broken when the migration to pydantic 2.0 happened.
- `File` and `Form` from `esmerald.params` now accept `annotation`.
- OpenAPI for `UploadFile` as single and list now being parsed as a model.


## 2.0.1

This is a small fix into the parser of lists for the OpenAPI specification.

### Fixed

- [OpenAPIResponse](https://esmerald.dev/responses#openapi-responses) now allows proper parse of
lists as definition. [More details](https://esmerald.dev/responses/#lists).

## 2.0.0

!!! Warning
	When upgrading Esmerald to version 2, this also means the use of Pydantic 2.0 at its core as well as corresponsing technologies
	already updated to version 2 of Pydantic (Saffier, Asyncz...).
	If you still wish to continue to use Pydantic 1 with Esmerald, it is recommended to use Esmerald prior to version 2.0 which it will
	be maintained for a shor period but we **strongly recommend to always use the latest version**.

### Changed

- **Major update of the core of Esmerald from Pydantic v1 to Pydantic v2.**
- `ResponseSpecification` renamed to `OpenAPIResponse`, `from esmerald.openapi.datastructures import OpenAPIResponse`.
- Changed deprecated functions such as `validator` and `root_validator` to `field_validator` and `model_validator`.
- Transformers no longer support custom fields. Pydantic natively handles that.
- EsmeraldSignature updated for the new version of the FieldInfo.
- `params` reflect the new Pydantic FieldInfo.
- Deprecated OpenAPIView in favour of the new OpenAPI documentation generator.
- Changed OpenAPI config to reflect the new generation of OpenAPI documentation.
- Internal data field is now returning Body type parameter making it easier to integrate with Pydantic 2.0.
- General codebase cleanup.
- Removed old OpenAPI document generator in favour to the newest, fastest, simplest and more effective approach in v2.
- Remove the support of pydantic 1.0. Esmerald 2+ will only support pydantic 2+.

### Added

- OpenAPI support for OAuth2.

### Fixed

- FileResponse `stat_result` and Stream `iterator` typing.
- Fix typing across the whole codebase.
- Transformers are now generating Param fields directly.
- Updated __fields__ in favour of the new pydantic model_fields approach.

## 1.3.0

### Changed

- OpenAPI imports and removed unused dependencies.
- Deprecate `pydantic_factories` in favour of `pyfactories`.
- Dropped support for Tortoise ORM natively.

### Fixed

- Rename `scripts/format` to `scripts/lint` for consistency.
- `get_hasher` from contrib fixed with the return value of the algorithm.
- Typing of the codebase updated.

## 1.2.5

### Fixed

- Removed deprecated functions allowing the mount and host.
- Fixed show_urls for openapi specification.

## 1.2.4

### Changed

- Updated pyproject.toml keywords.
- Updated to the latest [Starlette 0.28.0](https://www.lilya.dev/release-notes/).
- Exception handler logic refactored.

## 1.2.3

### Fixed

- Upgrade Starlette version to >=0.27.0 for a security release. Details on [Starlette's security](https://github.com/encode/starlette/security/advisories/GHSA-v5gw-mw7f-84px)

## 1.2.2

### Fixed

- Exception handler message when `run` directive does not find custom directive properly.

## 1.2.1

### Fixed

- Lifespan generator for the `run` directive.

## 1.2.0

### Changed

- Updated native requirements of the project.
- Removed old core management in favour of click.
- Deprecated `management` package in favour of `directives`. [#83](https://github.com/dymmond/esmerald/pull/83).
- Deprecate `esmerald-admin`. Now you can simply call `esmerald` with the same directives
as before. Simplification via command line [#86](https://github.com/dymmond/esmerald/pull/86).
	- Example:
		- `esmerald createproject <NAME>`
		- `esmerald createpapp <NAME>`

### Added

- Support for Ruff.
- New esmerald core admin management directives [#83](https://github.com/dymmond/esmerald/pull/83).
- New directives client.
- Added rich for command line colours, tables.
- New native directives:
	- [directives](./directives/directives.md#list-available-directives).
	- [runserver](./directives/directives.md#runserver).
	- [show_urls](./directives/directives.md#show-urls).

### Fixed

- Linting and formatting issues with Ruff.

## 1.1.0

### Changed

- Updated support for Starlette 0.26.1
- Updated support for Lifespan [./lifespan.md] events
- Requests url_for parsing the URL type to return string on parsing [#69](https://github.com/dymmond/esmerald/pull/69).
- Esmerald official documentation also available on https://esmerald.dev [#70](https://github.com/dymmond/esmerald/pull/70).
- Updated Github CI to deploy also to https://esmerald.dev [#73](https://github.com/dymmond/esmerald/pull/73)

### Added

- Internal implementation of on_startup and on_shutdown. [#74](https://github.com/dymmond/esmerald/pull/74).
- Added new internal implementation of on_event and add_event_handler functions. [#74](https://github.com/dymmond/esmerald/pull/74).
- Missing documentation about the background tasks [#71](https://github.com/dymmond/esmerald/pull/71)
- Documentation for lifespan events [#72](https://github.com/dymmond/esmerald/pull/72)
- Added condition to allow cached_properties from the EsmeraldAPISettings and in the settings without raising an Exception.
- New handlers. OPTIONS, HEAD and TRACE. Check out the  [handlers](./routing/handlers.md) for more details.

### Fixed

- New Starlette Lifespan [#75](https://github.com/dymmond/esmerald/pull/75). This is now also available to be done in the same way Starlette does. Internally Esmerald also implements the on_startup and on_shutdown but that is an unique implementation. This implementation follows the same pattern as the official [Starlette Bridge](https://starlette-bridge.tarsild.io/)

## 1.0.0

### Changed

- ChildEsmerald now supports the parent which means it can share middlewares and interceptors
across main application and children.

    !!! Note
        Prior to version 1.0.0, sharing resources between Esmerald and ChildEsmerald was not allowed
        and it needed to be treated as completely isolated application. In the version 1.0.0 you can
        still isolate them but you can also share resources.


## 0.15.0

### Added

-  Esmerald Pluggables [#60](https://github.com/dymmond/esmerald/pull/60).

	This is the feature for the esmerald ecosystem that allows you to create plugins and extensions for any application
	as well as distribute them as installable packages.

- New [add_child_ravyn](./routing/router.md#add_child_ravyn) allowing adding via function, ChildEsmerald [#61](https://github.com/dymmond/esmerald/pull/61).

	Add child esmeralds via functions once the application is created and dynamically.


## 0.14.0

### Added

- Brand new support for [Saffier](https://saffier.tarsild.io). A brand new ORM running
on the top of SQLAlchemy in an async fashion.
- New `base_user` and `middleware` support for Saffier with Esmerald.
- New docs regarding the [Saffier](https://esmerald.dev/databases/saffier/motivation/) integration.
Those include also an example how to use it.

### Changed

- **Breaking change** - Removed support for python 3.7. This was blocking the technology from
evolving at a normal pace and blocking security patches from being properly applied.

### Fixed

- Old package versioning conflicts.

## 0.13.0

### Changed

- Added support for Starlette 0.25.0

### Fixed

- Internal mapping types [#45](https://github.com/dymmond/esmerald/pull/56)

## 0.12.0

### Changed

- Added support for Starlette 0.24.0.

### Fixed

- `debug` parameter regression.

## 0.11.2

### Changed

- Code clean for responses and encoders.
- JWTConfig leeway parameter to accept int and str.

### Fixed

- `ujson` dumps parameter error.

## 0.11.1

### Changed

- Improved `OrJSON`, `UJSON`, `ORJSONResponse` and `UJSONResponse` when importing dependency.

## 0.11.0

### Added

To make esmerald more optional and feature modular, this release brings some backwards
incompatibilities that should be addressed when moving to this version. Check out
the dcumentation for more details if this release notes doesn't cover it all.

### Changed

- Moved `UJSON`, `UJSONResponse`, `OrJSON` and `ORJSONResponse` to be optional dependencies [#45](https://github.com/dymmond/esmerald/pull/45).
- Changed the imports for `ORJSONResponse` to `from esmerald.responses.encoders import ORJSONResponse` [#45](https://github.com/dymmond/esmerald/pull/45).
- Changed the imports for `UJSONResponse` to `from esmerald.responses.encoders import UJSONResponse` [#45](https://github.com/dymmond/esmerald/pull/45).
- Changed the imports for `OrJSON` to `from esmerald.datastructures.encoders import OrJSON` [#45](https://github.com/dymmond/esmerald/pull/45).
- Changed the imports for `UJSON` to `from esmerald.datastructures.encoders import UJSON` [#45](https://github.com/dymmond/esmerald/pull/45).
- Moved the scheduler to optional installation with `pip install esmerald[schedulers]` [#45](https://github.com/dymmond/esmerald/pull/45).

#### Backwards compatibility
This is only applied for those who have esmerald prior to `0.11.0`.
If you already had template configurations, jwt, schedulers or all the features you need to update the imports to:

- **TemplateConfig**:
    ```python
    from esmerald.core.config.template import TemplateConfig
    ```

- **JWTConfig**:
    ```python
    from esmerald.core.config.jwt import JWTConfig
    ```
- Scheduler class is now imported directly from `asyncz`:
    ```python
    from asyncz.schedulers import AsyncIOScheduler # for the Scheduler class
    from asyncz.contrib.esmerald.decorator import scheduler # for the decorator
    ```

## 0.10.0

### Added

- `add_apiview` to the Esmerald class.
- [JSON](./responses.md#json), [OrJSON](./responses.md#orjson) and [UJSON](./responses.md#ujson) responses [#44](https://github.com/dymmond/esmerald/pull/44).

### Changed

- `Template` now accepts an extra `alternative_template` for the cases of raising TemplateNotFound [#44](https://github.com/dymmond/esmerald/pull/44).
- Removed `handle_status_code` internal functionality as it is no longer used.

### Fixed

- `handler` type for Gateway and WebsocketGateway.
- The split bytes intead of b''.

## 0.9.0

### Added

- `DirectInjects` object for the direct dependency injection without using Inject and `dependencies` from the handler [#42](https://github.com/dymmond/esmerald/pull/42).

### Fixed

- `include_in_schema` on a Gateway level for OpenAPI specification [#42](https://github.com/dymmond/esmerald/pull/42).
- `redirect_slashes` when instantiating an Esmerald/ChildEsmerald application wasn't
validating the value properly.
- TemplateNotFound raised when a template is not found [#42](https://github.com/dymmond/esmerald/pull/42).
- jinja2 Environment to have autoescape by default [#43](https://github.com/dymmond/esmerald/pull/43)

## 0.8.1

### Added

- Added Template and Redirect to app imports.
This was supposed to go in the release 0.8.0 but somehow it was missed.

## 0.8.0

January 22, 2023

### Added

- New `File` and `Form` params to Esmerald.
- Add new `Injects` as parameter function.
- Add new `ArbitraryHashableBaseModel` to handle the `Inject` with arbitrary types.
- Add new [settings_config](./application/settings.md#the-settings_module) parameter. [#40](https://github.com/dymmond/esmerald/pull/40).

### Changed

- Removed unused internal parameters for old functions.
- `scheduler_class` is now a property in the EsmeraldSettings. This allows to override fields
without issues.
- Deprecate `settings` parameter from `RequestSettingsMiddleware`.

### Fixed

- Error messages being thrown.
- Fix `enable_openapi` boolean for ChildEsmerald and submodules and `include_in_schema` for Include [#37](https://github.com/dymmond/esmerald/pull/37)
- Fix types for OpenAPI for applications that are subclasses of Esmerald or ChildEsmerald [#38](https://github.com/dymmond/esmerald/pull/38)

## 0.7.0

### Added

- New [RequestSettingsMiddleware](./middleware/middleware.md#requestsettingsmiddleware) allowing accessing the settings of the application
from the request.
- Settings resolution for the whole application [#30](https://github.com/dymmond/esmerald/issues/30).

### Changed

- Request now has a `settings` property that can be accessed upon the installation
of the [RequestSettingsMiddleware](./middleware/middleware.md#requestsettingsmiddleware).

### Fixed

- `license` reference upon instantiation from the settings.

## 0.6.2

### Changed

- Add support for kwargs in the Dao and AsyncDAO [#28](https://github.com/dymmond/esmerald/issues/28)

### Fixed

- Mypy references for the Gateway and WebsocketGateway being added to the handler.
- References to the Esmerald types causing the IDE to misread them.

## 0.6.1

### Changed

- Include now supports its own middleware handling and loading [#26](https://github.com/dymmond/esmerald/pull/26).
This hange make sure that the parent level doesn't get affected and do not influence the middleware
of other includes.
- [JWTConfig](./configurations/jwt.md) `api_key_header` now defaults to `Authorization`.

### Fixed

- JWT Token encoding and decoding [#26](https://github.com/dymmond/esmerald/pull/26).
- JWT middleware handling the headers

## 0.6.0

### Added

- Added support to the new [Interceptors](./interceptors.md). [#25](https://github.com/dymmond/esmerald/pull/25)

### Changed

- Added support to httpx 0.23.3
- Updated document references pointing to [Interceptors](./interceptors.md).

### Fixed

- `JWTAuthMiddleware` from `esmerald.contrib.auth.tortoise.middleware` raising exception
on invalid token.
- Fixed code references to the `Void`.

## 0.5.4

### Changed

- Updated version of asyncz to support 0.1.4.
- Fixed dependencies when installing Esmerald based on Asyncz requirements.
- Minor fixes.

## 0.5.3

### Changed

- Added support to httpx 0.23.2

## 0.5.2

### Changed

- Support for Asyncz 0.1.3

## 0.5.1

### Changed

- Add support for Asyncz 0.1.2

## 0.5.0

!!! Warning
    This changes might contain some backward incompatibilities if you are already using the
    previous scheduler.

## Changed

- **Deprecated** the integration with `APScheduler` in favour of [Asyncz](https://asyncz.tarsild.io).
[#15](https://github.com/dymmond/esmerald/pull/15)
- Upgraded the Esmerald official symbol.

!!! Warning
    If you are using the `@scheduler` with the `func` and `identifier` params, please check the
    [documentation](./scheduler/handler.md) to understand how to upgrade to the new scheduler.
    It is almost the same but with some minor changes to the parameters

## 0.4.2

### Changed

- Created `BaseModelExtra` parser removing repetition of code across transformers.

### Fix

- Configurations for scheduler being passed as params.
- Scheduler in the slots.

## 0.4.1

### Changed

- Added support for Starlette 0.23.1.

## 0.4.0

### Changed

- Updated support to Starlette 0.23.0
- Updated the RavynTestClient to support headers.

### Fixed

- [Token](./configurations/jwt.md#token-model) parameters being passed to `python-jose`.
- Update internal references to the JWT.

## 0.3.1

### Added

- HashableBaseModel allowing the __hash__ to be done via pydantic BaseModels.

### Changed

- Update transformer model field and functions.

### Fixed

- Minor doc fixes.

## 0.3.0

### Changed

- Deprecated kwargs and signature to give place to Esmerald transformers.
- Code cleaning and improved performance by applying pure pydantic models internally.

## 0.2.11

### Fixed

- When instantiating an `Esmerald` object, `app_name` should be passed instead of `name`.

## 0.2.10

### Changed

- Supporting Starlette version 0.22.0.

### Fixed

- `max_age` from [SessionConfig](./configurations/session.md) allowing negative numbers being passed
and can be used for testing purposes or to clear a session.

## 0.2.9

### Fixed

- `redirect_slashes` property added to the main Esmerald object and settings options.

## 0.2.8

### Fixed

- `@router` allowing validation for Options for CORS middleware.

## 0.2.7

### Added

- Officially supporting python 3.11.

## 0.2.6

### Changed

- Removed Tortoise ORM dependency from the main package.
- Removed `asyncpg` from the main package as dependency.

## 0.2.5

### Changed

- Removed `auth.py` from security package as is no longer used. This was supposed to go in the release 0.2.4.

## 0.2.4

### Changed

- Removed `settings.py` from permissions as it is no longer used.

## 0.2.3

### Fixed

- OpenAPI documentation rendering for the same path with different http methods.

## 0.2.2

### Added

- `httpx` and `itsdangerous` dependencies.

## 0.2.1

### Changed

- Removed `archive`.
- Removed unnecessary comments.

### Fixed

- Generation of projects and apps using `esmerald` by removing the clutter.

## 0.2.0

### Added

- `esmerald` entrypoint allowing generating projects and apps via [directives](./directives/directives.md).

### Fixed

- Namespace conflicts when importing the `Include` and the `include` internal function.

## 0.1.3

### Changed

- `add_route` - Fixed the way the add_route was managing the paths and import to OpenAPI docs.


## 0.1.2

### Changed

- `add_routes` - Fixed the way the add_route was managing the paths and import to OpenAPI docs.

## 0.1.1

### Changed

- `pyproject.toml` - Added missing dependencies.

## 0.1.0

This release is the first release of Esmerald and it contain all the essentials to start a project from the simplest
version to the most advanced.

### Added

- **Fluid and Fast**: Thanks to Starlette and Pydantic.
- **Fast to develop**: Thanks to the simplicity of design, the development times can be reduced exponentially.
- **Intuitive**: If you are used to the other frameworks, Esmerald is a no brainer to develop.
- **Easy**: Developed with design in mind and easy learning.
- **Short**: With the OOP available natively there is no need for code duplication. SOLID.
- **Ready**: Get your application up and running with production-ready code.
- **OOP and Functional**: Design APIs in any desired way. OOP or Functional is available.
- **Async and Sync**: Do you prefer sync or async? You can have both.
- **Middleware**: Apply middlewares on the application level or API level.
- **Exception Handlers**: Apply exception handlers on any desired level.
- **Permissions**: Apply specific rules and permissions on each API.
- **DAO and AsyncDAO**: Avoid database calls directly from the APIs. Use business objects instead.
- **Tortoise ORM**: Native support for Tortoise ORM.
- **APIView**: Class Based endpoints for your beloved OOP design.
- **JSON serialization/deserialization**: Both UJSON and ORJON support.
- **Lifespan**: Support for the newly lifespan and on_start/on_shutdown events.
- **Dependency Injection**: Like any other great framework out there.
- **Scheduler**: Yes, that's right, it comes with a scheduler for those automated tasks.
- **Simplicity from settings**: Yes, we have a way to make the code even cleaner by introducing settings
based systems.
