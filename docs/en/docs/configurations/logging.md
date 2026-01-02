# LoggingConfig

Configure centralized logging for your Ravyn application with flexible backend support.

## What You'll Learn

- Why Ravyn has LoggingConfig
- Using the global logger
- Creating custom logging backends
- Best practices for logging

## Quick Start

```python
from ravyn import Ravyn
from ravyn.logging import logger

app = Ravyn()  # Uses StandardLoggingConfig by default

# Use logger anywhere
logger.info("Application started")
logger.error("Something went wrong")
```

---

## Why LoggingConfig?

Ravyn introduced `LoggingConfig` to provide:

- **Consistency** - Predictable logging across your app

- **Flexibility** - Support for standard logging, Loguru, Structlog, or custom backends

- **Simplicity** - One global logger for the entire app

- **Extensibility** - Easy to create custom logging configurations

---

## The Global Logger

Access the logger anywhere in your application:

```python
from ravyn.logging import logger

# In any file
logger.info("User logged in")
logger.warning("Rate limit approaching")
logger.error("Database connection failed")
logger.debug("Request details: %s", request_data)
```

The logger automatically uses the configured backend.

---

## Available Backends

### Standard Python Logging (Default)

```python
from ravyn import Ravyn

# Uses StandardLoggingConfig by default
app = Ravyn()
```

### Custom Configuration

```python
from ravyn import Ravyn
from ravyn.config import StandardLoggingConfig

app = Ravyn(
    logging_config=StandardLoggingConfig(
        level="INFO",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
)
```

---

## Creating Custom Logging

### Custom LoggingConfig

```python
from ravyn.config import LoggingConfig
import logging

class CustomLoggingConfig(LoggingConfig):
    def configure(self) -> None:
        """Configure the logging system."""
        logging.basicConfig(
            level=logging.INFO,
            format='[%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('app.log')
            ]
        )
    
    def get_logger(self):
        """Return the logger instance."""
        return logging.getLogger("ravyn")

# Use it
app = Ravyn(logging_config=CustomLoggingConfig())
```

### Using Loguru

```python
from ravyn.config import LoggingConfig
from loguru import logger as loguru_logger

class LoguruConfig(LoggingConfig):
    def configure(self) -> None:
        """Configure Loguru."""
        loguru_logger.add(
            "app.log",
            rotation="500 MB",
            retention="10 days",
            level="INFO"
        )
    
    def get_logger(self):
        """Return Loguru logger."""
        return loguru_logger

app = Ravyn(logging_config=LoguruConfig())
```

---

## Using with Settings

```python
from ravyn import RavynSettings
from ravyn.config import StandardLoggingConfig

class AppSettings(RavynSettings):
    logging_config: StandardLoggingConfig = StandardLoggingConfig(
        level="INFO"
    )

app = Ravyn(settings_module=AppSettings)
```

---

## Logging Levels

| Level | When to Use |
|-------|-------------|
| `DEBUG` | Detailed diagnostic information |
| `INFO` | General informational messages |
| `WARNING` | Warning messages for potential issues |
| `ERROR` | Error messages for failures |
| `CRITICAL` | Critical failures requiring immediate attention |

### Example Usage

```python
from ravyn.logging import logger

# Debug - detailed info
logger.debug("Processing request: %s", request_id)

# Info - general events
logger.info("User %s logged in", user_id)

# Warning - potential issues
logger.warning("Cache miss for key: %s", cache_key)

# Error - failures
logger.error("Failed to connect to database: %s", error)

# Critical - severe issues
logger.critical("Out of memory! Shutting down...")
```

---

## Best Practices

### 1. Use Structured Logging

```python
# Good - structured data
logger.info("User login", extra={
    "user_id": user.id,
    "ip_address": request.client.host,
    "timestamp": datetime.utcnow()
})
```

### 2. Log at Appropriate Levels

```python
# Good - correct levels
logger.debug("Cache lookup for key: %s", key)  # Debug details
logger.info("User created: %s", user.id)       # Important events
logger.error("Payment failed: %s", error)      # Errors
```

### 3. Don't Log Sensitive Data

```python
# Wrong - logging passwords
logger.info("User login: %s / %s", email, password)

# Correct - no sensitive data
logger.info("User login attempt: %s", email)
```

---

## Common Patterns

### Pattern 1: Request Logging

```python
from ravyn import get, Request
from ravyn.logging import logger

@get("/api/users")
async def get_users(request: Request) -> list:
    logger.info(
        "Fetching users",
        extra={"path": request.url.path, "method": request.method}
    )
    users = await fetch_users()
    logger.info("Returned %d users", len(users))
    return users
```

### Pattern 2: Error Logging

```python
from ravyn import post
from ravyn.logging import logger

@post("/api/process")
async def process_data(data: dict) -> dict:
    try:
        result = await process(data)
        return result
    except Exception as e:
        logger.error(
            "Processing failed",
            exc_info=True,  # Include stack trace
            extra={"data_id": data.get("id")}
        )
        raise
```

---

## Next Steps

- [SchedulerConfig](./scheduler.md) - Task scheduling
- [SessionConfig](./session.md) - Session management
- [Application Settings](../application/settings.md) - Configuration
