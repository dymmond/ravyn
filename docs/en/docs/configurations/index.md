# Configurations

Configure Ravyn's built-in features with these configuration classes.

## Available Configurations

### Security

- [CORSConfig](./cors.md) - Cross-Origin Resource Sharing
- [CSRFConfig](./csrf.md) - Cross-Site Request Forgery protection
- [JWTConfig](./jwt.md) - JSON Web Token authentication
- [SessionConfig](./session.md) - Session management

### Application Features

- [StaticFilesConfig](./staticfiles.md) - Static file serving
- [TemplateConfig](./template.md) - Template engine configuration
- [OpenAPIConfig](./openapi/config.md) - API documentation
- [SchedulerConfig](./scheduler.md) - Task scheduling
- [LoggingConfig](./logging.md) - Logging configuration

## Quick Examples

### CORS Configuration

```python
from ravyn import Ravyn
from ravyn.config import CORSConfig

app = Ravyn(
    cors_config=CORSConfig(
        allow_origins=["https://example.com"],
        allow_methods=["GET", "POST"]
    )
)
```

### CSRF Protection

```python
from ravyn.config import CSRFConfig

app = Ravyn(
    csrf_config=CSRFConfig(secret="your-secret-key")
)
```

### Static Files

```python
from ravyn.config import StaticFilesConfig

app = Ravyn(
    static_files_config=StaticFilesConfig(
        path="/static",
        directory="static"
    )
)
```

## Configuration via Settings

All configurations can be set via the settings module:

```python
from ravyn import RavynSettings
from ravyn.config import CORSConfig, CSRFConfig

class AppSettings(RavynSettings):
    cors_config: CORSConfig = CORSConfig(allow_origins=["*"])
    csrf_config: CSRFConfig = CSRFConfig(secret="secret-key")

app = Ravyn(settings_module=AppSettings)
```

## Next Steps

Choose a configuration to learn more:

- [CORS](./cors.md) - Enable cross-origin requests
- [CSRF](./csrf.md) - Protect against CSRF attacks
- [JWT](./jwt.md) - Implement JWT authentication
- [Templates](./template.md) - Set up template rendering
