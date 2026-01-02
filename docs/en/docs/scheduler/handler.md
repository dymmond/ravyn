# Task Handlers

Create and configure scheduled tasks using the @scheduler decorator with Asyncz triggers.

## What You'll Learn

- Using the @scheduler decorator
- Available triggers (cron, interval, date)
- Task configuration options
- Advanced scheduling patterns

## Quick Start

```python
from ravyn.contrib.schedulers.asyncz.decorator import scheduler

@scheduler(name="daily_cleanup", trigger="cron", hour=2, minute=0)
async def cleanup_old_data():
    """Runs every day at 2:00 AM."""
    await delete_old_records()
    print("Cleanup completed")
```

!!! info
    Install scheduler support: `pip install ravyn[schedulers]`

---

## The @scheduler Decorator

The `@scheduler` decorator marks a function as a scheduled task.

### Basic Usage

```python
from ravyn.contrib.schedulers.asyncz.decorator import scheduler

@scheduler(name="my_task", trigger="interval", hours=1)
async def my_scheduled_task():
    """Runs every hour."""
    print("Task executed!")
```

### Decorator Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `name` | str | Task name | `None` |
| `trigger` | str/object | Trigger type or instance | `None` |
| `id` | str | Explicit task ID | `None` |
| `misfire_grace_time` | int | Seconds after scheduled time task can still run | `undefined` |
| `coalesce` | bool | Run once if multiple executions missed | `undefined` |
| `max_instances` | int | Max concurrent instances | `undefined` |
| `store` | str | Task store alias | `None` |
| `executor` | str | Executor alias | `None` |
| `is_enabled` | bool | Enable/disable task | `True` |

---

## Triggers

### CronTrigger - Schedule Like Cron

Run tasks at specific times using cron-style scheduling:

```python
from ravyn.contrib.schedulers.asyncz.decorator import scheduler

# Every day at 9:00 AM
@scheduler(name="morning_report", trigger="cron", hour=9, minute=0)
async def generate_morning_report():
    await create_daily_report()

# Every Monday at 10:00 AM
@scheduler(
    name="weekly_summary",
    trigger="cron",
    day_of_week="mon",
    hour=10,
    minute=0
)
async def weekly_summary():
    await send_weekly_email()

# First day of month at midnight
@scheduler(name="monthly_billing", trigger="cron", day=1, hour=0, minute=0)
async def process_monthly_billing():
    await generate_invoices()
```

**Cron Parameters:**

| Parameter | Type | Description | Range |
|-----------|------|-------------|-------|
| `year` | int/str | 4-digit year | - |
| `month` | int/str | Month | 1-12 |
| `day` | int/str | Day of month | 1-31 |
| `week` | int/str | ISO week | 1-53 |
| `day_of_week` | int/str | Weekday | 0-6 or mon-sun |
| `hour` | int/str | Hour | 0-23 |
| `minute` | int/str | Minute | 0-59 |
| `second` | int/str | Second | 0-59 |

### IntervalTrigger - Fixed Intervals

Run tasks at regular intervals:

```python
# Every 30 minutes
@scheduler(name="sync_data", trigger="interval", minutes=30)
async def sync_with_api():
    await fetch_latest_data()

# Every 2 hours
@scheduler(name="backup", trigger="interval", hours=2)
async def backup_database():
    await create_backup()

# Every day
@scheduler(name="cleanup", trigger="interval", days=1)
async def daily_cleanup():
    await remove_old_files()

# Complex interval
@scheduler(
    name="complex_task",
    trigger="interval",
    weeks=1,
    days=2,
    hours=3,
    minutes=30
)
async def complex_interval():
    # Runs every 1 week, 2 days, 3 hours, and 30 minutes
    pass
```

**Interval Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `weeks` | int | Number of weeks |
| `days` | int | Number of days |
| `hours` | int | Number of hours |
| `minutes` | int | Number of minutes |
| `seconds` | int | Number of seconds |
| `start_date` | datetime/str | Start time |
| `end_date` | datetime/str | End time |

### DateTrigger - One-Time Execution

Run a task once at a specific date/time:

```python
from datetime import datetime

# Run once at specific time
@scheduler(
    name="campaign_launch",
    trigger="date",
    run_date=datetime(2026, 12, 25, 9, 0)
)
async def launch_campaign():
    await activate_holiday_campaign()

# Run once (immediately if no date specified)
@scheduler(name="one_time_task", trigger="date")
async def run_once():
    await initialize_system()
```

---

## Advanced Triggers

### OrTrigger - Multiple Schedules

Run when ANY trigger fires:

```python
from asyncz.triggers import CronTrigger, IntervalTrigger, OrTrigger

# Run at 9 AM OR every 3 hours
trigger = OrTrigger([
    CronTrigger(hour=9, minute=0),
    IntervalTrigger(hours=3)
])

@scheduler(name="flexible_task", trigger=trigger)
async def flexible_execution():
    await process_data()
```

### AndTrigger - Combined Conditions

Run when ALL triggers agree:

```python
from asyncz.triggers import CronTrigger, AndTrigger

# Run on weekdays AND between 9-5
trigger = AndTrigger([
    CronTrigger(day_of_week="mon-fri"),
    CronTrigger(hour="9-17")
])

@scheduler(name="business_hours_task", trigger=trigger)
async def during_business_hours():
    await send_notifications()
```

---

## Task Configuration

### Preventing Overlaps

```python
# Only 1 instance at a time
@scheduler(
    name="heavy_task",
    trigger="interval",
    minutes=5,
    max_instances=1
)
async def heavy_processing():
    await process_large_dataset()
```

### Handling Missed Runs

```python
# If missed, run only once (not multiple times)
@scheduler(
    name="sync_task",
    trigger="interval",
    minutes=10,
    coalesce=True
)
async def sync_data():
    await sync_with_external_api()
```

### Grace Period

```python
# Allow 60 seconds after scheduled time
@scheduler(
    name="time_sensitive",
    trigger="cron",
    hour=9,
    minute=0,
    misfire_grace_time=60
)
async def time_sensitive_task():
    await send_morning_email()
```

---

## Complete Example

```python
from ravyn import Ravyn
from ravyn.contrib.schedulers.asyncz.config import AsynczConfig
from ravyn.contrib.schedulers.asyncz.decorator import scheduler

# Define tasks
@scheduler(name="hourly_sync", trigger="interval", hours=1)
async def sync_data():
    """Sync data every hour."""
    print("Syncing data...")
    await fetch_from_api()

@scheduler(name="daily_report", trigger="cron", hour=8, minute=0)
async def generate_report():
    """Generate report at 8 AM daily."""
    print("Generating report...")
    await create_daily_report()

@scheduler(
    name="cleanup",
    trigger="cron",
    hour=2,
    minute=0,
    max_instances=1
)
async def cleanup_old_data():
    """Cleanup at 2 AM, prevent overlaps."""
    print("Cleaning up...")
    await delete_old_records()

# Configure app
app = Ravyn(
    scheduler_config=AsynczConfig(),
    enable_scheduler=True,
    scheduler_tasks={
        "hourly_sync": "tasks.sync_data",
        "daily_report": "tasks.generate_report",
        "cleanup": "tasks.cleanup_old_data"
    }
)
```

---

## Best Practices

### 1. Use Descriptive Names

```python
# Good - clear purpose
@scheduler(name="user_cleanup_daily", trigger="cron", hour=2)
async def cleanup_inactive_users():
    pass
```

### 2. Prevent Overlaps for Long Tasks

```python
# Good - prevent concurrent runs
@scheduler(
    name="heavy_processing",
    trigger="interval",
    hours=1,
    max_instances=1
)
async def process_large_files():
    pass
```

### 3. Handle Errors Gracefully

```python
# Good - error handling
@scheduler(name="api_sync", trigger="interval", minutes=15)
async def sync_with_api():
    try:
        await fetch_data()
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        # Maybe send alert
```

---

## Stores and Executors

Configure custom stores and executors:

```python
from ravyn import Ravyn
from ravyn.contrib.schedulers.asyncz.config import AsynczConfig

app = Ravyn(
    scheduler_config=AsynczConfig(),
    enable_scheduler=True,
    scheduler_configurations={
        "stores": {
            "default": {"type": "memory"},
            "redis": {"type": "redis", "host": "localhost"}
        },
        "executors": {
            "default": {"type": "asyncio"},
            "threadpool": {"type": "threadpool", "max_workers": 20}
        }
    }
)

# Use custom store/executor
@scheduler(
    name="redis_task",
    trigger="interval",
    hours=1,
    store="redis",
    executor="threadpool"
)
async def task_with_custom_config():
    pass
```

---

## Learn More

- [Asyncz Documentation](https://asyncz.dymmond.com) - Complete trigger reference
- [Scheduler Setup](./scheduler.md) - Configure the scheduler
- [SchedulerConfig](../configurations/scheduler.md) - Configuration options

---

## Next Steps

- [Scheduler Configuration](./scheduler.md) - Enable and configure
- [Background Tasks](../background-tasks.md) - One-off tasks
- [Lifespan Events](../lifespan-events.md) - Application lifecycle
