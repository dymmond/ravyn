# Application Settings

Settings let you configure your Ravyn application for different environments (development, testing, production) without changing code. Ravyn uses Pydantic-based settings inspired by Django's approach, making configuration clean and type-safe.

## What You'll Learn

- How to use default settings vs custom settings
- Creating environment-specific configurations
- Using `RAVYN_SETTINGS_MODULE` environment variable
- Using `settings_module` for modular applications
- Accessing settings in your application

## Quick Start

### Using Default Settings

The simplest Ravyn app uses built-in defaults:

```python
from ravyn import Ravyn

app = Ravyn()  # Uses default RavynSettings
```

### Custom Settings

Create environment-specific settings:

```python
from ravyn import RavynSettings
from ravyn.conf.enums import EnvironmentType

class DevelopmentSettings(RavynSettings):
    app_name: str = "My App (Dev)"
    debug: bool = True
    environment: str = EnvironmentType.DEVELOPMENT
```

Load it with an environment variable:

```shell
# MacOS/Linux
RAVYN_SETTINGS_MODULE='myapp.settings.DevelopmentSettings' uvicorn app:app

# Windows
$env:RAVYN_SETTINGS_MODULE="myapp.settings.DevelopmentSettings"; uvicorn app:app
```

!!! tip
    If no `RAVYN_SETTINGS_MODULE` is set, Ravyn uses sensible defaults automatically.

---

## How Settings Work

Ravyn has two ways to configure your application:

1. **`RAVYN_SETTINGS_MODULE`** - Environment variable for global settings
2. **`settings_module`** - Parameter for instance-specific settings

Both work together with a clear priority order.

### Default Settings (RavynSettings)

When you create a Ravyn instance without parameters, it loads `RavynSettings`:

```python
from ravyn import Ravyn

app = Ravyn()  # Automatically uses RavynSettings defaults
```

> [!INFO]
> `RavynSettings` was previously called `RavynAPISettings`. The old name still works for backwards compatibility, but use `RavynSettings` for new code.

### Overriding with Parameters

You can override any setting by passing parameters directly:

```python
from ravyn import Ravyn

app = Ravyn(
    app_name="My Custom App",
    debug=True,
    enable_openapi=True
)
```

**Priority:** Parameters > `settings_module` > `RAVYN_SETTINGS_MODULE` > defaults

---

## Creating Custom Settings

All custom settings **must inherit from `RavynSettings`**.

### Single Environment

```python
from ravyn import RavynSettings

class MyAppSettings(RavynSettings):
    app_name: str = "My Application"
    debug: bool = False
    secret_key: str = "your-secret-key-here"
```

### Multiple Environments (Recommended)

Create a base settings class and environment-specific classes:

#### Base Settings

```python
# myapp/settings/base.py
from ravyn import RavynSettings

class AppSettings(RavynSettings):
    """Common settings across all environments"""
    app_name: str = "My Application"
    secret_key: str = "change-me-in-production"
```

#### Development Settings

```python
# myapp/settings/development.py
from ravyn.conf.enums import EnvironmentType
from .base import AppSettings

class DevelopmentSettings(AppSettings):
    debug: bool = True
    environment: str = EnvironmentType.DEVELOPMENT
    
    @property
    def database_url(self) -> str:
        return "postgresql://localhost/myapp_dev"
```

#### Testing Settings

```python
# myapp/settings/testing.py
from ravyn.conf.enums import EnvironmentType
from .base import AppSettings

class TestingSettings(AppSettings):
    debug: bool = True
    environment: str = EnvironmentType.TESTING
    
    @property
    def database_url(self) -> str:
        return "postgresql://localhost/myapp_test"
```

#### Production Settings

```python
# myapp/settings/production.py
from ravyn.conf.enums import EnvironmentType
from .base import AppSettings

class ProductionSettings(AppSettings):
    debug: bool = False
    environment: str = EnvironmentType.PRODUCTION
    
    @property
    def database_url(self) -> str:
        return "postgresql://prod-server/myapp"
```

---

## Using RAVYN_SETTINGS_MODULE

Set the environment variable to load your custom settings:

### Development

```shell
# MacOS/Linux
RAVYN_SETTINGS_MODULE='myapp.settings.development.DevelopmentSettings' uvicorn app:app --reload

# Windows
$env:RAVYN_SETTINGS_MODULE="myapp.settings.development.DevelopmentSettings"; uvicorn app:app --reload
```

### Production

```shell
# MacOS/Linux
RAVYN_SETTINGS_MODULE='myapp.settings.production.ProductionSettings' uvicorn app:app

# Windows
$env:RAVYN_SETTINGS_MODULE="myapp.settings.production.ProductionSettings"; uvicorn app:app
```

### Without Environment Variable

If you don't set `RAVYN_SETTINGS_MODULE`, Ravyn uses defaults:

```shell
uvicorn app:app  # Uses RavynSettings defaults
```

---

## Using settings_module (Modular Apps)

The `settings_module` parameter lets you create modular applications with their own settings. This is perfect for:

- Pluggable applications
- Microservices
- Child applications with unique configs

### Basic Example

```python
from ravyn import Ravyn, RavynSettings

class PluginSettings(RavynSettings):
    app_name: str = "My Plugin"
    plugin_enabled: bool = True

app = Ravyn(settings_module=PluginSettings)
```

### Child Application with Custom Settings

```python
from ravyn import Ravyn, ChildRavyn, RavynSettings, Include

class ChildSettings(RavynSettings):
    app_name: str = "Child App"
    debug: bool = True

child_app = ChildRavyn(
    routes=[...],
    settings_module=ChildSettings
)

main_app = Ravyn(
    routes=[
        Include("/child", app=child_app)
    ]
)
```

---

## Settings Priority Order

Ravyn checks settings in this order (first match wins):

1. **Instance parameters** - `Ravyn(debug=True)`
2. **`settings_module`** - `Ravyn(settings_module=MySettings)`
3. **`RAVYN_SETTINGS_MODULE`** - Environment variable
4. **Default `RavynSettings`** - Built-in defaults

### Example

```python
from ravyn import Ravyn, RavynSettings

class GlobalSettings(RavynSettings):
    debug: bool = False
    app_name: str = "Global App"

class InstanceSettings(RavynSettings):
    debug: bool = True
    app_name: str = "Instance App"

# Set environment variable
# RAVYN_SETTINGS_MODULE='myapp.GlobalSettings'

app = Ravyn(
    settings_module=InstanceSettings,  # Takes priority over RAVYN_SETTINGS_MODULE
    app_name="Override App"  # Takes priority over everything
)

# Result:
# - app_name = "Override App" (from parameter)
# - debug = True (from settings_module, since no parameter)
```

---

## Combining Both Approaches

You can use `RAVYN_SETTINGS_MODULE` for global settings and `settings_module` for instance-specific overrides:

### Global Settings

```python
# src/configs/main_settings.py
from ravyn import RavynSettings

class AppSettings(RavynSettings):
    app_name: str = "My Application"
    debug: bool = False
```

### Instance Settings

```python
# src/configs/instance_settings.py
from ravyn import RavynSettings

class InstanceSettings(RavynSettings):
    app_name: str = "Custom Instance"
    enable_openapi: bool = True
```

### Application

```python
# src/app.py
from ravyn import Ravyn
from src.configs.instance_settings import InstanceSettings

app = Ravyn(settings_module=InstanceSettings)
```

### Run It

```shell
# MacOS/Linux
RAVYN_SETTINGS_MODULE='src.configs.main_settings.AppSettings' uvicorn src:app --reload

# Windows
$env:RAVYN_SETTINGS_MODULE="src.configs.main_settings.AppSettings"; uvicorn src:app --reload
```

**Result:** `InstanceSettings` values override `AppSettings` values.

---

## Accessing Settings

There are multiple ways to access settings in your application:

### From Request Object

```python
from ravyn import Ravyn, get, Request

app = Ravyn()

@app.get("/info")
def app_info(request: Request) -> dict:
    return {
        "app_name": request.app.settings.app_name,
        "debug": request.app.settings.debug
    }
```

### From Global Settings

```python
from ravyn import get
from ravyn.conf import settings

@get("/info")
def app_info() -> dict:
    return {
        "app_name": settings.app_name,
        "debug": settings.debug
    }
```

### From conf.settings

```python
from ravyn import get
from ravyn.conf.global_settings import settings

@get("/info")
def app_info() -> dict:
    return {
        "app_name": settings.app_name,
        "debug": settings.debug
    }
```

!!! warning
    If you pass parameters directly to `Ravyn()` instead of using settings, those values won't be in `request.app.settings`. Access them via `request.app.app_name` directly.

---

## Available Settings Parameters

All settings parameters are documented in the [Settings Reference](../references/application/settings.md).

Common settings include:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `app_name` | `str` | `"Ravyn"` | Application name |
| `debug` | `bool` | `False` | Debug mode |
| `environment` | `str` | `"production"` | Environment type |
| `secret_key` | `str` | Auto-generated | Secret key for security |
| `enable_openapi` | `bool` | `True` | Enable OpenAPI docs |
| `allowed_hosts` | `List[str]` | `["*"]` | Allowed host headers |

### Configuration Objects

Settings can include configuration objects for specific features:

- [CORS](../configurations/cors.md) - Cross-Origin Resource Sharing
- [CSRF](../configurations/csrf.md) - Cross-Site Request Forgery protection
- [Session](../configurations/session.md) - Session management
- [JWT](../configurations/jwt.md) - JSON Web Token configuration
- [StaticFiles](../configurations/staticfiles.md) - Static file serving
- [Template](../configurations/template.md) - Template engine configuration
- [OpenAPI](../configurations/openapi/config.md) - OpenAPI documentation

---

## Common Pitfalls & Fixes

### Pitfall 1: Settings Not Loading

**Problem:** Custom settings aren't being used.

```python
# Wrong - environment variable not set
uvicorn app:app  # Uses defaults, not your custom settings
```

**Solution:** Set `RAVYN_SETTINGS_MODULE` before running:

```shell
# Correct
RAVYN_SETTINGS_MODULE='myapp.settings.DevelopmentSettings' uvicorn app:app
```

### Pitfall 2: Settings Class Not Inheriting from RavynSettings

**Problem:** `ImproperlyConfigured` exception.

```python
# Wrong
class MySettings:  # Doesn't inherit from RavynSettings
    debug: bool = True
```

**Solution:** Always inherit from `RavynSettings`:

```python
# Correct
from ravyn import RavynSettings

class MySettings(RavynSettings):
    debug: bool = True
```

### Pitfall 3: Accessing Parameter Values from Settings

**Problem:** Values passed as parameters aren't in `request.app.settings`.

```python
app = Ravyn(app_name="Custom Name")  # Passed as parameter

@app.get("/info")
def info(request: Request) -> dict:
    # Wrong - won't find it in settings
    return {"name": request.app.settings.app_name}
```

**Solution:** Access parameter values directly from the app:

```python
# Correct
@app.get("/info")
def info(request: Request) -> dict:
    return {"name": request.app.app_name}  # Direct access
```

### Pitfall 4: Wrong Module Path

**Problem:** `ModuleNotFoundError` when setting `RAVYN_SETTINGS_MODULE`.

```shell
# Wrong - typo in path
RAVYN_SETTINGS_MODULE='myapp.setting.DevelopmentSettings' uvicorn app:app
```

**Solution:** Double-check the full module path:

```shell
# Correct
RAVYN_SETTINGS_MODULE='myapp.settings.DevelopmentSettings' uvicorn app:app
```

### Pitfall 5: Mixing Settings and Parameters Unexpectedly

**Problem:** Not understanding priority order leads to unexpected values.

```python
class MySettings(RavynSettings):
    debug: bool = False

app = Ravyn(
    settings_module=MySettings,
    debug=True  # This overrides settings!
)
# debug will be True, not False
```

**Solution:** Remember the priority: Parameters > settings_module > RAVYN_SETTINGS_MODULE > defaults

---

## Settings Patterns

### Pattern 1: Environment-Based Settings

```
myapp/
├── settings/
│   ├── __init__.py
│   ├── base.py
│   ├── development.py
│   ├── testing.py
│   └── production.py
└── app.py
```

Use different settings per environment:

```shell
# Development
RAVYN_SETTINGS_MODULE='myapp.settings.development.DevelopmentSettings' uvicorn app:app --reload

# Production
RAVYN_SETTINGS_MODULE='myapp.settings.production.ProductionSettings' uvicorn app:app
```

### Pattern 2: .env Files with Pydantic

```python
from ravyn import RavynSettings
from pydantic_settings import SettingsConfigDict

class Settings(RavynSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    database_url: str
    secret_key: str
    debug: bool = False
```

### Pattern 3: Feature Flags

```python
from ravyn import RavynSettings

class Settings(RavynSettings):
    feature_new_ui: bool = False
    feature_beta_api: bool = False
    
@app.get("/features")
def features(request: Request) -> dict:
    return {
        "new_ui": request.app.settings.feature_new_ui,
        "beta_api": request.app.settings.feature_beta_api
    }
```

---

## Next Steps

Now that you understand settings, explore:

- [Settings Reference](../references/application/settings.md) - All available parameters
- [CORS Configuration](../configurations/cors.md) - Configure CORS
- [CSRF Configuration](../configurations/csrf.md) - CSRF protection
- [JWT Configuration](../configurations/jwt.md) - JWT authentication
- [Application Levels](./levels.md) - Understand application hierarchy
- [Deployment](../deployment/intro.md) - Deploy with environment-specific settings
