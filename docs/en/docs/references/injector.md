# Inject, Factory and Injects

Ravyn dependency injection system is actually pretty simple and can
be checked in the [official dependency injection section](https://ravyn.dev/dependencies/)
for more details.

```python
from ravyn import Inject, Injects, Factory
```

::: ravyn.Inject
    options:
        filters:
        - "!^model_config"
        - "!^__hash__"
        - "!^__call__"
        - "!^__eq__"

::: ravyn.Injects
    options:
        filters:
        - "!^model_config"
        - "!^__hash__"
        - "!^__call__"
        - "!^__eq__"

::: ravyn.Factory
    options:
        filters:
        - "!^model_config"
        - "!^__hash__"
        - "!^__call__"
        - "!^__eq__"
