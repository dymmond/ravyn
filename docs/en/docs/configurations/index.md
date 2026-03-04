# Configurations

Ravyn uses configuration objects to enable built-in features with explicit, typed settings.

## Available configurations

### Core configs (top-level imports)

- `CORSConfig`
- `CSRFConfig`
- `SessionConfig`
- `StaticFilesConfig`
- `OpenAPIConfig`
- `LoggingConfig`

```python
from ravyn import (
    CORSConfig,
    CSRFConfig,
    LoggingConfig,
    OpenAPIConfig,
    SessionConfig,
    StaticFilesConfig,
)
```

### Additional configs

- `JWTConfig` from `ravyn.core.config.jwt`
- `TemplateConfig` from `ravyn.core.config.template`
- `SchedulerConfig` from `ravyn.contrib.schedulers`

```python
from ravyn.core.config.jwt import JWTConfig
from ravyn.core.config.template import TemplateConfig
from ravyn.contrib.schedulers import SchedulerConfig
```

## Quick examples

### CORS

```python
from ravyn import CORSConfig, Ravyn

app = Ravyn(
    routes=[],
    cors_config=CORSConfig(
        allow_origins=["https://example.com"],
        allow_methods=["GET", "POST"],
    ),
)
```

### CSRF

```python
from ravyn import CSRFConfig, Ravyn

app = Ravyn(
    routes=[],
    csrf_config=CSRFConfig(secret="your-secret-key"),
)
```

### Static files

```python
from ravyn import Ravyn, StaticFilesConfig

app = Ravyn(
    routes=[],
    static_files_config=StaticFilesConfig(path="/static", directory="static"),
)
```

## Configuration via settings

```python
from ravyn import CORSConfig, Ravyn, RavynSettings


class AppSettings(RavynSettings):
    @property
    def cors_config(self) -> CORSConfig:
        return CORSConfig(allow_origins=["*"])


app = Ravyn(routes=[], settings_module=AppSettings)
```

## Next steps

- [CORS](./cors.md)
- [CSRF](./csrf.md)
- [JWT](./jwt.md)
- [Sessions](./session.md)
- [Templates](./template.md)
- [Static files](./staticfiles.md)
- [OpenAPI config](./openapi/config.md)
- [Scheduler config](./scheduler.md)
- [Logging config](./logging.md)
