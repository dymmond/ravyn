# Extensions

Extensions let you add reusable behavior to a Ravyn application without coupling everything to handlers.

Use them for integrations such as databases, clients, telemetry, feature flags, and service wiring.

## What You'll Learn

- Difference between `Extension` and `Pluggable`.
- How extension initialization works.
- How to pass configuration into extensions.
- How to register extensions from app or settings.

## Quick Start

```python
from ravyn import Extension, Pluggable, Ravyn


class GreetingExtension(Extension):
    def extend(self, **kwargs):
        self.app.state.greeting = kwargs.get("greeting", "hello")


app = Ravyn(
    routes=[],
    extensions={
        "greeting": Pluggable(GreetingExtension, greeting="hello from extension")
    },
)
```

## Core concepts

### `Extension`

`Extension` is the base class you subclass.

- Ravyn injects the app instance into `self.app`.
- You implement `extend(**kwargs)`.
- `extend()` is where initialization logic should happen.

### `Pluggable`

`Pluggable` is a lazy wrapper around an extension class.

It can receive:

- Extension class object.
- Import string path to an extension class.

This is useful to delay imports and keep configuration declarative.

## Creating an extension

```python
from ravyn import Extension


class CacheExtension(Extension):
    def extend(self, **kwargs):
        ttl = kwargs.get("default_ttl", 60)
        self.app.state.cache_default_ttl = ttl
```

## Registering extensions

### Via `Ravyn(...)`

```python
from ravyn import Pluggable, Ravyn

app = Ravyn(
    routes=[],
    extensions={
        "cache": Pluggable(CacheExtension, default_ttl=300),
    },
)
```

### Via settings

```python
from ravyn import Pluggable, Ravyn, RavynSettings


class AppSettings(RavynSettings):
    @property
    def extensions(self):
        return {
            "cache": Pluggable(CacheExtension, default_ttl=300),
        }


app = Ravyn(routes=[], settings_module=AppSettings)
```

### Manual registration

```python
app.add_extension("cache", Pluggable(CacheExtension, default_ttl=300))
```

## Extension ordering

If one extension depends on another, you can enforce order:

```python
class MetricsExtension(Extension):
    def extend(self, **kwargs):
        self.app.extensions.ensure_extension("cache")
        self.app.state.metrics_ready = True
```

This guarantees `cache` is initialized first.

## Good practices

- Keep `extend()` focused on wiring, not business rules.
- Store shared resources in `self.app.state`.
- Use explicit extension keys (`"cache"`, `"mailer"`, `"metrics"`).
- Prefer `Pluggable` for configuration-heavy integrations.

## API reference

- [Extension reference](./references/extensions.md)
- [Pluggable reference](./references/pluggables.md)
