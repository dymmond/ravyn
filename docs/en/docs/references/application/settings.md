# **`RavynSettings`** class

Reference for the `RavynSettings` class object and how to use it.

Read more about [how to use the settings](https://ravyn.dev/application/settings/) in your
application and leverage the system.

The settings are used by **any Ravyn application** and used as the defaults for the
[Ravyn](../ravyn.md) class instance if nothing is provided.

## How to import

```python
from ravyn import settings
```

**Via conf**

```python
from ravyn.conf import settings
```

**Via application instance**

```python
from ravyn import Ravyn

app = Ravyn()
app.settings
```

::: ravyn.RavynSettings
    options:
        filters:

        - "!^model_config"
        - "!^ipython_args"
        - "!^ptpython_config_file"
        - "!^async_exit_config"
