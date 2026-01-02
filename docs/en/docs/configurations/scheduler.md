# SchedulerConfig

Configure task scheduling in your Ravyn application for running background jobs and periodic tasks.

## What You'll Learn

- What task scheduling is
- Configuring the scheduler
- Creating scheduled tasks
- Common scheduling patterns

## Quick Start

```python
from ravyn import Ravyn
from ravyn.config import SchedulerConfig

app = Ravyn(
    scheduler_config=SchedulerConfig(
        enabled=True
    )
)
```

!!! info
    Install scheduler support: `pip install ravyn[schedulers]` or `pip install asyncz`

---

## What is Task Scheduling?

**Task scheduling** allows you to run functions automatically at specific times or intervals. Perfect for:

- **Periodic Tasks** - Run every hour, day, week

- **Cleanup Jobs** - Delete old data regularly

- **Data Sync** - Sync with external APIs

- **Reports** - Generate daily/weekly reports

- **Monitoring** - Health checks and alerts

---

## Basic Configuration

### Minimal Setup

```python
from ravyn import Ravyn
from ravyn.config import SchedulerConfig

app = Ravyn(
    scheduler_config=SchedulerConfig(
        enabled=True
    )
)
```

### Complete Configuration

```python
app = Ravyn(
    scheduler_config=SchedulerConfig(
        enabled=True,
        timezone="UTC",
        max_instances=3,
        coalesce=True
    )
)
```

---

## Configuration Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `enabled` | bool | Enable scheduler | `False` |
| `timezone` | str | Timezone for tasks | `"UTC"` |
| `max_instances` | int | Max concurrent instances | `1` |
| `coalesce` | bool | Combine missed runs | `False` |

---

## Creating Scheduled Tasks

### Using @scheduler Decorator

```python
from ravyn import Ravyn
from ravyn.config import SchedulerConfig
from ravyn.contrib.schedulers.asyncz.decorator import scheduler

app = Ravyn(
    scheduler_config=SchedulerConfig(enabled=True)
)

@scheduler(name="cleanup_task", trigger="interval", hours=1)
async def cleanup_old_data():
    """Run every hour."""
    await delete_old_records()
    print("Cleanup completed")
```

### Cron-Style Scheduling

```python
@scheduler(
    name="daily_report",
    trigger="cron",
    hour=9,
    minute=0
)
async def generate_daily_report():
    """Run every day at 9:00 AM."""
    report = await create_report()
    await send_email(report)
```

---

## Trigger Types

### Interval Trigger

Run at fixed intervals:

```python
# Every 30 minutes
@scheduler(name="sync", trigger="interval", minutes=30)
async def sync_data():
    await sync_with_api()

# Every 2 hours
@scheduler(name="backup", trigger="interval", hours=2)
async def backup_database():
    await create_backup()

# Every day
@scheduler(name="cleanup", trigger="interval", days=1)
async def daily_cleanup():
    await cleanup()
```

### Cron Trigger

Run at specific times:

```python
# Every day at 3:00 AM
@scheduler(name="backup", trigger="cron", hour=3, minute=0)
async def nightly_backup():
    await backup_database()

# Every Monday at 9:00 AM
@scheduler(name="report", trigger="cron", day_of_week="mon", hour=9)
async def weekly_report():
    await generate_report()

# Every 1st of month at midnight
@scheduler(name="billing", trigger="cron", day=1, hour=0)
async def monthly_billing():
    await process_billing()
```

### Date Trigger

Run once at a specific date/time:

```python
from datetime import datetime

@scheduler(
    name="campaign",
    trigger="date",
    run_date=datetime(2026, 12, 31, 23, 59)
)
async def end_campaign():
    await close_campaign()
```

---

## Common Patterns

### Pattern 1: Database Cleanup

```python
@scheduler(name="cleanup", trigger="cron", hour=2, minute=0)
async def cleanup_old_sessions():
    """Delete old sessions every day at 2 AM."""
    from datetime import datetime, timedelta
    
    cutoff = datetime.utcnow() - timedelta(days=30)
    await Session.filter(created_at__lt=cutoff).delete()
    
    print(f"Cleaned up sessions older than {cutoff}")
```

### Pattern 2: API Sync

```python
@scheduler(name="sync_users", trigger="interval", minutes=15)
async def sync_users_from_api():
    """Sync users every 15 minutes."""
    import httpx
    
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/users")
        users = response.json()
        
        for user_data in users:
            await User.update_or_create(
                id=user_data["id"],
                defaults=user_data
            )
```

### Pattern 3: Report Generation

```python
@scheduler(name="daily_report", trigger="cron", hour=8, minute=0)
async def send_daily_report():
    """Send daily report at 8 AM."""
    # Generate report
    stats = await calculate_daily_stats()
    
    # Send email
    await send_email(
        to="admin@example.com",
        subject="Daily Report",
        body=f"Stats: {stats}"
    )
```

---

## Using with Settings

```python
from ravyn import RavynSettings
from ravyn.config import SchedulerConfig

class AppSettings(RavynSettings):
    scheduler_config: SchedulerConfig = SchedulerConfig(
        enabled=True,
        timezone="America/New_York",
        max_instances=3
    )

app = Ravyn(settings_module=AppSettings)
```

---

## Advanced Features

### Multiple Instances

```python
# Allow up to 3 concurrent instances
@scheduler(
    name="heavy_task",
    trigger="interval",
    minutes=5,
    max_instances=3
)
async def heavy_processing():
    await process_large_dataset()
```

### Coalescing

```python
# If missed runs, execute only once
@scheduler(
    name="sync",
    trigger="interval",
    minutes=10,
    coalesce=True
)
async def sync_data():
    await sync_with_external_api()
```

### Conditional Execution

```python
@scheduler(name="backup", trigger="cron", hour=3)
async def conditional_backup():
    """Only backup if data changed."""
    if await has_data_changed():
        await create_backup()
    else:
        print("No changes, skipping backup")
```

---

## Best Practices

### 1. Use Appropriate Intervals

```python
# Good - reasonable intervals
@scheduler(name="health_check", trigger="interval", minutes=5)
async def health_check():
    pass

# Wrong - too frequent
@scheduler(name="check", trigger="interval", seconds=1)
async def constant_check():
    pass
```

### 2. Handle Errors Gracefully

```python
# Good - error handling
@scheduler(name="sync", trigger="interval", hours=1)
async def sync_with_retry():
    try:
        await sync_data()
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        # Maybe retry or alert
```

### 3. Use Timezone Aware Times

```python
# Good - explicit timezone
app = Ravyn(
    scheduler_config=SchedulerConfig(
        enabled=True,
        timezone="America/New_York"
    )
)
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Forgot to Enable

**Problem:** Scheduler not running.

```python
# Wrong - scheduler disabled
app = Ravyn()  # enabled=False by default
```

**Solution:** Enable scheduler:

```python
# Correct
app = Ravyn(
    scheduler_config=SchedulerConfig(enabled=True)
)
```

### Pitfall 2: Missing Dependencies

**Problem:** Import error.

```bash
# Wrong - asyncz not installed
ModuleNotFoundError: No module named 'asyncz'
```

**Solution:** Install dependencies:

```bash
# Correct
pip install ravyn[schedulers]
# or
pip install asyncz
```

### Pitfall 3: Blocking Operations

**Problem:** Using sync code in async task.

```python
# Wrong - blocking operation
@scheduler(name="task", trigger="interval", minutes=5)
async def blocking_task():
    time.sleep(60)  # Blocks event loop!
```

**Solution:** Use async operations:

```python
# Correct
@scheduler(name="task", trigger="interval", minutes=5)
async def async_task():
    await asyncio.sleep(60)  # Non-blocking
```

---

## Next Steps

- [LoggingConfig](./logging.md) - Application logging
- [Lifespan Events](../lifespan-events.md) - Application lifecycle
- [Background Tasks](../background-tasks.md) - One-off tasks
