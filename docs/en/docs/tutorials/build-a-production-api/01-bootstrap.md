# Step 1: Bootstrap Project

Set up a minimal but production-oriented Ravyn project layout.

## Project structure

```text
myapp/
  app/
    main.py
    settings.py
    users/
      routes.py
      schemas.py
      service.py
```

## Create settings

```python
from ravyn import RavynSettings


class AppSettings(RavynSettings):
    title: str = "My Production API"
    version: str = "1.0.0"
    debug: bool = False
```

## Create application entrypoint

```python
from ravyn import Ravyn
from .settings import AppSettings

app = Ravyn(
    routes=[],
    settings_module=AppSettings,
)
```

## Run locally

```shell
palfrey app.main:app --reload
```

## Checkpoint

- app starts without errors
- settings are loaded from `AppSettings`

## Next step

Continue with [Routing and Models](./02-routing-and-models.md).
