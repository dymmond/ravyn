# Scheduler Setup

Imagine having a personal assistant who remembers to:

- Send birthday cards every year (cron job)
- Pay bills on the 1st of each month (scheduled task)
- Water your plants every Tuesday (recurring event)
- Remind you about meetings 10 minutes before (one-time task)

That's what the scheduler does for your application. It runs tasks automatically on a schedule, so you don't have to remember or manually trigger them. Your assistant never forgets, never sleeps, and works 24/7.

Configure and enable the built-in task scheduler in your Ravyn application using Asyncz.

## What You'll Learn

- Installing scheduler support
- Enabling the scheduler
- Configuring AsynczConfig
- Registering tasks
- Best practices

## Quick Start

```python
from ravyn import Ravyn
from ravyn.contrib.schedulers.asyncz.config import AsynczConfig

app = Ravyn(
    scheduler_config=AsynczConfig(),
    enable_scheduler=True,
    scheduler_tasks={
        "daily_cleanup": "tasks.cleanup_old_data",
        "hourly_sync": "tasks.sync_data"
    }
)
```

---

## Why Use the Scheduler?

- **Automated Tasks** - Run jobs automatically

- **No Cron Needed** - Built into your application

- **Asyncz Integration** - Powerful scheduling library

- **Easy Configuration** - Simple setup

---

## Requirements

Install scheduler support:

```bash
pip install ravyn[schedulers]
```

This installs [Asyncz](https://asyncz.dymmond.com), the scheduling library used by Ravyn.

---

## AsynczConfig

The `AsynczConfig` class manages the scheduler integration with Asyncz.

### Basic Configuration

```python
from ravyn import Ravyn
from ravyn.contrib.schedulers.asyncz.config import AsynczConfig

app = Ravyn(
    scheduler_config=AsynczConfig(),
    enable_scheduler=True
)
```

### Configuration Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `scheduler_class` | class | Asyncz scheduler type | `AsyncIOScheduler` |
| `tasks` | dict | Task name to path mapping | `{}` |
| `timezone` | str | Scheduler timezone | `"UTC"` |
| `configurations` | dict | Extra scheduler config | `{}` |

---

## Enabling the Scheduler

The scheduler is **disabled by default**. Enable it with `enable_scheduler=True`.

### Via Application

```python
from ravyn import Ravyn
from ravyn.contrib.schedulers.asyncz.config import AsynczConfig

app = Ravyn(
    scheduler_config=AsynczConfig(),
    enable_scheduler=True  # Required!
)
```

### Via Settings

```python
from ravyn import RavynSettings
from ravyn.contrib.schedulers.asyncz.config import AsynczConfig

class AppSettings(RavynSettings):
    enable_scheduler: bool = True
    scheduler_config: AsynczConfig = AsynczConfig()

app = Ravyn(settings_module=AppSettings)
```

!!! warning
    Without `enable_scheduler=True`, the scheduler will not start!

---

## Registering Tasks

Tasks must be registered with the application.

### Task Registration

```python
# tasks.py
from ravyn.contrib.schedulers.asyncz.decorator import scheduler

@scheduler(name="cleanup", trigger="cron", hour=2, minute=0)
async def cleanup_old_data():
    """Runs daily at 2 AM."""
    await delete_old_records()

@scheduler(name="sync", trigger="interval", hours=1)
async def sync_data():
    """Runs every hour."""
    await fetch_from_api()
```

### Register in Application

```python
# app.py
from ravyn import Ravyn
from ravyn.contrib.schedulers.asyncz.config import AsynczConfig

app = Ravyn(
    scheduler_config=AsynczConfig(),
    enable_scheduler=True,
    scheduler_tasks={
        "cleanup": "tasks.cleanup_old_data",
        "sync": "tasks.sync_data"
    }
)
```

**Task mapping format:**
- **Key** - Task name (from @scheduler decorator)
- **Value** - Import path to the task function

---

## Complete Example

### 1. Create Tasks

```python
# tasks.py
from ravyn.contrib.schedulers.asyncz.decorator import scheduler

@scheduler(name="daily_report", trigger="cron", hour=8, minute=0)
async def generate_daily_report():
    """Generate report at 8 AM daily."""
    print("Generating daily report...")
    await create_report()

@scheduler(name="data_sync", trigger="interval", minutes=30)
async def sync_external_data():
    """Sync data every 30 minutes."""
    print("Syncing data...")
    await fetch_data()

@scheduler(name="cleanup", trigger="cron", hour=2, minute=0)
async def cleanup_database():
    """Cleanup at 2 AM daily."""
    print("Cleaning up...")
    await delete_old_records()
```

### 2. Configure Application

```python
# app.py
from ravyn import Ravyn
from ravyn.contrib.schedulers.asyncz.config import AsynczConfig

app = Ravyn(
    scheduler_config=AsynczConfig(timezone="America/New_York"),
    enable_scheduler=True,
    scheduler_tasks={
        "daily_report": "tasks.generate_daily_report",
        "data_sync": "tasks.sync_external_data",
        "cleanup": "tasks.cleanup_database"
    }
)
```

### 3. Run Application

```bash
ravyn run
```

Tasks will run automatically according to their schedules!

---

## Using Settings

### Settings File

```python
# settings.py
from ravyn import RavynSettings
from ravyn.contrib.schedulers.asyncz.config import AsynczConfig

class AppSettings(RavynSettings):
    enable_scheduler: bool = True
    
    scheduler_config: AsynczConfig = AsynczConfig(
        timezone="UTC"
    )
    
    scheduler_tasks: dict = {
        "daily_report": "tasks.generate_daily_report",
        "data_sync": "tasks.sync_external_data",
        "cleanup": "tasks.cleanup_database"
    }
```

### Application

```python
# app.py
from ravyn import Ravyn
from settings import AppSettings

app = Ravyn(settings_module=AppSettings)
```

### Run with Settings

```bash
# Linux/Mac
RAVYN_SETTINGS_MODULE=settings.AppSettings ravyn run

# Windows
$env:RAVYN_SETTINGS_MODULE="settings.AppSettings"; ravyn run
```

---

## Advanced Configuration

### Custom Stores and Executors

```python
from ravyn import Ravyn
from ravyn.contrib.schedulers.asyncz.config import AsynczConfig

app = Ravyn(
    scheduler_config=AsynczConfig(),
    enable_scheduler=True,
    scheduler_configurations={
        "stores": {
            "default": {"type": "memory"},
            "redis": {
                "type": "redis",
                "host": "localhost",
                "port": 6379
            }
        },
        "executors": {
            "default": {"type": "asyncio"},
            "threadpool": {
                "type": "threadpool",
                "max_workers": 20
            }
        }
    },
    scheduler_tasks={
        "task1": "tasks.my_task"
    }
)
```

### Using Custom Stores

```python
# tasks.py
from ravyn.contrib.schedulers.asyncz.decorator import scheduler

@scheduler(
    name="redis_task",
    trigger="interval",
    hours=1,
    store="redis",  # Use Redis store
    executor="threadpool"  # Use thread pool executor
)
async def task_with_redis():
    await process_data()
```

---

## Best Practices

### 1. Use Environment Variables

```python
# Good - configurable
import os

class AppSettings(RavynSettings):
    enable_scheduler: bool = os.getenv("ENABLE_SCHEDULER", "true") == "true"
    
    scheduler_config: AsynczConfig = AsynczConfig(
        timezone=os.getenv("TIMEZONE", "UTC")
    )
```

### 2. Organize Tasks

```
app/
  tasks/
    __init__.py
    cleanup.py
    reports.py
    sync.py
  app.py
  settings.py
```

### 3. Use Descriptive Task Names

```python
# Good - clear names
scheduler_tasks = {
    "user_cleanup_daily": "tasks.cleanup.cleanup_inactive_users",
    "sales_report_weekly": "tasks.reports.generate_sales_report",
    "api_sync_hourly": "tasks.sync.sync_with_external_api"
}
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Scheduler Not Starting

**Problem:** Forgot to enable scheduler.

```python
# Wrong - scheduler disabled
app = Ravyn(
    scheduler_config=AsynczConfig()
    # Missing enable_scheduler=True!
)
```

**Solution:** Enable the scheduler:

```python
# Correct
app = Ravyn(
    scheduler_config=AsynczConfig(),
    enable_scheduler=True
)
```

### Pitfall 2: Tasks Not Found

**Problem:** Wrong import path.

```python
# Wrong - incorrect path
scheduler_tasks = {
    "cleanup": "cleanup_old_data"  # Missing module!
}
```

**Solution:** Use full import path:

```python
# Correct
scheduler_tasks = {
    "cleanup": "tasks.cleanup_old_data"
}
```

### Pitfall 3: Timezone Issues

**Problem:** Tasks run at wrong times.

```python
# Wrong - using default UTC
scheduler_config = AsynczConfig()  # Defaults to UTC
```

**Solution:** Set correct timezone:

```python
# Correct
scheduler_config = AsynczConfig(
    timezone="America/New_York"
)
```

---

## Scheduler Lifecycle

The scheduler integrates with Ravyn's lifecycle:

```python
from ravyn import Ravyn

app = Ravyn(
    scheduler_config=AsynczConfig(),
    enable_scheduler=True
)

# Scheduler starts on application startup
# Scheduler stops on application shutdown
```

For custom lifecycle management, see [Lifespan Events](../lifespan-events.md).

---

## Learn More

- [Asyncz Documentation](https://asyncz.dymmond.com) - Complete scheduler reference
- [Task Handlers](./handler.md) - Create scheduled tasks
- [SchedulerConfig](../configurations/scheduler.md) - Configuration options

---

## Next Steps

- [Task Handlers](./handler.md) - Create your first task
- [Background Tasks](../background-tasks.md) - One-off tasks
- [Lifespan Events](../lifespan-events.md) - Application lifecycle
