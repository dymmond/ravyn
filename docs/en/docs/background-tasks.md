# Background Tasks

Imagine you're running a coffee shop. When a customer orders a latte, you don't make them stand at the counter while you:

1. Grind the beans
2. Steam the milk
3. Clean the espresso machine
4. Update your inventory spreadsheet

Instead, you hand them a receipt immediately and do the rest while they grab a seat. That's exactly what background tasks do for your API.

Background tasks let you execute code **after** sending a response to the client. This keeps your API fast by not making users wait for slow operations like sending emails or processing files.

## What You'll Learn

- When to use background tasks (and when not to)
- Adding tasks via handlers
- Adding tasks via responses
- Running multiple background tasks
- Real-world examples and gotchas

## Quick Start

Let's say you're building a user registration system. When someone signs up, you need to:

- Save their account (fast - 50ms)
- Send a welcome email (slow - 2 seconds)

Without background tasks, your user waits 2+ seconds staring at a loading spinner. With background tasks, they get an instant response:

```python
from ravyn import Ravyn, post, BackgroundTask
from ravyn.responses import JSONResponse

def send_welcome_email(email: str):
    """This runs after the response is sent"""
    print(f"Sending welcome email to {email}")
    # Email sending logic here

@post("/register")
def register_user(email: str, background_tasks: BackgroundTask) -> JSONResponse:
    # Save user to database (fast)
    user_id = 123
    
    # Send email in background (slow)
    background_tasks = BackgroundTask(send_welcome_email, email)
    
    # Response sent immediately, email sent after
    return JSONResponse(
        {"user_id": user_id, "message": "Registration successful"},
        background=background_tasks
    )

app = Ravyn()
app.add_route(register_user)
```

**The result?** Your user sees "Registration successful" in 50ms instead of 2+ seconds. The email still gets sent, just after they've already moved on to explore your app.

---

## When to Use Background Tasks

### Perfect For:

- **Sending emails** - Registration confirmations, notifications
- **Processing files** - Image resizing, video transcoding
- **Logging/Analytics** - Recording events, updating metrics
- **External API calls** - Webhooks, third-party integrations
- **Cleanup operations** - Deleting temporary files, cache invalidation

### Not Suitable For:

- **Long-running jobs** - Use a task queue (Celery, RQ) instead
- **Critical operations** - If it must succeed, use a proper queue
- **Operations needing results** - Background tasks can't return values to the client

!!! tip
    Background tasks are great for "fire and forget" operations that take a few seconds. For longer jobs, use a dedicated task queue.

---

## Adding Tasks Via Handlers

You can define background tasks directly in your route decorators.

### Single Task

```python
from ravyn import Ravyn, post, BackgroundTask, get

def log_request(endpoint: str):
    print(f"Request to {endpoint} completed")

@post("/users", background=BackgroundTask(log_request, "/users"))
def create_user(name: str) -> dict:
    return {"created": name}

app = Ravyn()
app.add_route(create_user)
```

### Multiple Tasks

```python
from ravyn import Ravyn, post, BackgroundTasks

def send_email(to: str):
    print(f"Email sent to {to}")

def log_event(event: str):
    print(f"Event logged: {event}")

def update_analytics():
    print("Analytics updated")

@post(
    "/register",
    background=BackgroundTasks(tasks=[
        BackgroundTask(send_email, "admin@example.com"),
        BackgroundTask(log_event, "user_registered"),
        BackgroundTask(update_analytics)
    ])
)
def register(email: str) -> dict:
    return {"registered": email}

app = Ravyn()
app.add_route(register)
```

---

## Adding Tasks Via Response

More commonly, you'll add tasks inside your handler where you have access to request data.

### Single Task via Response

```python
from ravyn import Ravyn, post, BackgroundTask
from ravyn.responses import JSONResponse

def send_notification(user_id: int, message: str):
    print(f"Notification to user {user_id}: {message}")

@post("/notify")
def notify_user(user_id: int, message: str) -> JSONResponse:
    # Create background task with request data
    task = BackgroundTask(send_notification, user_id, message)
    
    return JSONResponse(
        {"status": "notification queued"},
        background=task
    )

app = Ravyn()
app.add_route(notify_user)
```

### Multiple Tasks via Response

```python
from ravyn import Ravyn, post, BackgroundTask, BackgroundTasks
from ravyn.responses import JSONResponse

def send_email(email: str):
    print(f"Email sent to {email}")

def update_database(user_id: int):
    print(f"Database updated for user {user_id}")

def log_action(action: str):
    print(f"Action logged: {action}")

@post("/process")
def process_order(user_id: int, email: str) -> JSONResponse:
    # Create multiple tasks
    tasks = BackgroundTasks(tasks=[
        BackgroundTask(send_email, email),
        BackgroundTask(update_database, user_id),
        BackgroundTask(log_action, "order_processed")
    ])
    
    return JSONResponse(
        {"status": "processing"},
        background=tasks
    )

app = Ravyn()
app.add_route(process_order)
```

### Using add_task Method

The `add_task()` method lets you build tasks dynamically:

```python
from ravyn import Ravyn, post, BackgroundTasks
from ravyn.responses import JSONResponse

def send_email(to: str, subject: str):
    print(f"Email to {to}: {subject}")

def write_log(message: str):
    print(f"Log: {message}")

@post("/action")
def perform_action(user_email: str, action_type: str) -> JSONResponse:
    tasks = BackgroundTasks()
    
    # Add tasks conditionally
    if action_type == "important":
        tasks.add_task(send_email, user_email, "Important Action")
        tasks.add_task(write_log, f"Important action by {user_email}")
    else:
        tasks.add_task(write_log, f"Regular action by {user_email}")
    
    return JSONResponse(
        {"status": "completed"},
        background=tasks
    )

app = Ravyn()
app.add_route(perform_action)
```

The `add_task()` method accepts:

- **Task function** - The function to run
- **Positional arguments** - Passed to the function
- **Keyword arguments** - Passed to the function

---

## Async and Sync Functions

Background tasks work with both `def` and `async def` functions:

```python
from ravyn import Ravyn, post, BackgroundTask
from ravyn.responses import JSONResponse
import asyncio

# Sync function
def sync_task(message: str):
    print(f"Sync: {message}")

# Async function
async def async_task(message: str):
    await asyncio.sleep(1)
    print(f"Async: {message}")

@post("/mixed")
def handler() -> JSONResponse:
    tasks = BackgroundTasks(tasks=[
        BackgroundTask(sync_task, "Hello"),
        BackgroundTask(async_task, "World")
    ])
    
    return JSONResponse({"status": "ok"}, background=tasks)

app = Ravyn()
app.add_route(handler)
```

Ravyn automatically handles both types correctly.

---

## Practical Examples

### Example 1: User Registration Flow

```python
from ravyn import Ravyn, post, BackgroundTasks
from ravyn.responses import JSONResponse

def send_welcome_email(email: str):
    print(f"Sending welcome email to {email}")

def create_user_profile(user_id: int):
    print(f"Creating profile for user {user_id}")

def notify_admin(user_email: str):
    print(f"New user registered: {user_email}")

@post("/register")
def register_user(email: str, password: str) -> JSONResponse:
    # Quick database insert
    user_id = 123  # Simulated
    
    # Background tasks
    tasks = BackgroundTasks()
    tasks.add_task(send_welcome_email, email)
    tasks.add_task(create_user_profile, user_id)
    tasks.add_task(notify_admin, email)
    
    return JSONResponse(
        {"user_id": user_id, "message": "Registration successful"},
        status_code=201,
        background=tasks
    )

app = Ravyn()
app.add_route(register_user)
```

### Example 2: File Upload Processing

```python
from ravyn import Ravyn, post, BackgroundTask
from ravyn.responses import JSONResponse

def process_uploaded_file(filename: str, user_id: int):
    print(f"Processing {filename} for user {user_id}")
    # Image resizing, virus scanning, etc.

@post("/upload")
async def upload_file(filename: str, user_id: int) -> JSONResponse:
    # Save file quickly
    file_path = f"/uploads/{filename}"
    
    # Process in background
    task = BackgroundTask(process_uploaded_file, filename, user_id)
    
    # Return immediately with 202 Accepted
    return JSONResponse(
        {"message": "File uploaded, processing started", "file": filename},
        status_code=202,
        background=task
    )

app = Ravyn()
app.add_route(upload_file)
```

### Example 3: Webhook Notifications

```python
from ravyn import Ravyn, post, BackgroundTask
from ravyn.responses import JSONResponse
import httpx

async def send_webhook(url: str, data: dict):
    async with httpx.AsyncClient() as client:
        await client.post(url, json=data)

@post("/orders")
async def create_order(item: str, quantity: int, webhook_url: str) -> JSONResponse:
    order_id = 456  # Simulated
    
    # Send webhook notification in background
    webhook_data = {"order_id": order_id, "item": item, "quantity": quantity}
    task = BackgroundTask(send_webhook, webhook_url, webhook_data)
    
    return JSONResponse(
        {"order_id": order_id, "status": "created"},
        status_code=201,
        background=task
    )

app = Ravyn()
app.add_route(create_order)
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Expecting Return Values

**Problem:** Background tasks can't return values to the client.

```python
# Wrong - can't get result
def calculate_total(items: list) -> int:
    return sum(items)

@post("/calculate")
def handler() -> JSONResponse:
    task = BackgroundTask(calculate_total, [1, 2, 3])
    # Can't access the result!
    return JSONResponse({}, background=task)
```

**Solution:** Use background tasks only for side effects, not for results:

```python
# Correct - side effect only
def log_calculation(items: list):
    total = sum(items)
    print(f"Calculated total: {total}")

@post("/calculate")
def handler() -> JSONResponse:
    items = [1, 2, 3]
    total = sum(items)  # Calculate in handler
    
    task = BackgroundTask(log_calculation, items)  # Log in background
    return JSONResponse({"total": total}, background=task)
```

### Pitfall 2: Long-Running Tasks

**Problem:** Imagine asking your waiter to cook a 3-course meal before bringing your coffee. That's what happens when you run long tasks in the background - your server gets stuck waiting.

```python
# Wrong - blocks server for 10 minutes
def process_large_file(filename: str):
    time.sleep(600)  # 10 minutes!
    # Process file...

@post("/process")
def handler(filename: str) -> JSONResponse:
    task = BackgroundTask(process_large_file, filename)
    return JSONResponse({}, background=task)
```

**Solution:** For anything longer than a few seconds, use a proper task queue like Celery. Think of it as hiring a dedicated chef instead of making your waiter do everything:

```python
# Correct - use Celery or similar
from celery_app import celery

@celery.task
def process_large_file(filename: str):
    # Long processing here
    pass

@post("/process")
def handler(filename: str) -> JSONResponse:
    process_large_file.delay(filename)  # Queue it
    return JSONResponse({"status": "queued"})
```

### Pitfall 3: Not Handling Errors

**Problem:** Background task errors are silent.

```python
# Wrong - errors disappear
def risky_operation(data: dict):
    result = data["missing_key"]  # KeyError!

@post("/risky")
def handler() -> JSONResponse:
    task = BackgroundTask(risky_operation, {})
    return JSONResponse({}, background=task)
```

**Solution:** Add error handling in background tasks:

```python
# Correct - handle errors
import logging

logger = logging.getLogger(__name__)

def risky_operation(data: dict):
    try:
        result = data["missing_key"]
    except KeyError as e:
        logger.error(f"Background task error: {e}")

@post("/risky")
def handler() -> JSONResponse:
    task = BackgroundTask(risky_operation, {})
    return JSONResponse({}, background=task)
```

### Pitfall 4: Accessing Request After Response

**Problem:** Request object may not be available in background task.

```python
# Risky - request might be gone
from ravyn import Request

def log_request_data(request: Request):
    print(request.url)  # Might fail!

@post("/test")
def handler(request: Request) -> JSONResponse:
    task = BackgroundTask(log_request_data, request)
    return JSONResponse({}, background=task)
```

**Solution:** Extract data from request before passing to task:

```python
# Correct - extract data first
@post("/test")
def handler(request: Request) -> JSONResponse:
    url = str(request.url)  # Extract data
    task = BackgroundTask(lambda: print(url))  # Use extracted data
    return JSONResponse({}, background=task)
```

---

## Background Tasks vs Task Queues

| Feature | Background Tasks | Task Queues (Celery/RQ) |
|---------|-----------------|-------------------------|
| **Setup** | Built-in, no setup | Requires broker (Redis/RabbitMQ) |
| **Duration** | Seconds | Minutes to hours |
| **Reliability** | Best effort | Guaranteed execution |
| **Retries** | No | Yes |
| **Monitoring** | No | Yes |
| **Scaling** | Limited | Unlimited workers |
| **Use Case** | Quick side effects | Critical long jobs |

---

## Technical Details

Ravyn's `BackgroundTask` and `BackgroundTasks` come from Lilya with added type hints.

You can import directly from Lilya if needed:

```python
from lilya.background import BackgroundTask, BackgroundTasks
```

Learn more in the [Lilya Background Tasks docs](https://www.lilya.dev/tasks/).

**API Reference:** See the [BackgroundTask Reference](references/background.md).

---

## Next Steps

Now that you understand background tasks, explore:

- [Scheduler](./scheduler.md) - Schedule recurring tasks
- [Lifespan Events](./lifespan-events.md) - Run code on startup/shutdown
- [Middleware](./middleware/index.md) - Process all requests
- [Responses](./responses.md) - Different response types
```
