# Background Tasks

In this section, you'll learn how to run background tasks in Ravyn, allowing you to perform non-blocking operations
after sending a response.

---

## What are Background Tasks?

Background tasks are functions that run asynchronously **after** the response is returned to the client.

They're perfect for:

- Sending emails
- Writing logs
- Triggering external webhooks
- Cleanup operations

---

## Using BackgroundTask

Ravyn provides a simple interface for background execution:

```python
from ravyn import BackgroundTask, get

async def notify_user(email: str):
    # Imagine this sends an email
    await some_email_function(email)

@get("/send-notification", background=BackgroundTask(notify_user, "user@example.com"))
def send_notification() -> dict:
    return {
        "message": "Scheduled"
    }
```

---

## Using BackgroundTasks for Multiple Tasks

You can queue multiple tasks with `BackgroundTasks`:

```python
from ravyn import BackgroundTasks, post

async def cleanup(file_path: str):
    await remove_file(file_path)

async def log_event(event_id: int):
    await save_log(event_id)

@post("/submit", background=BackgroundTasks(
    tasks=[
        BackgroundTask(cleanup, "/tmp/tempfile"),
        BackgroundTask(log_event, 42),
    ]
))
def submit(background: BackgroundTasks) -> dict:
    return {"status": "submitted"}
```

---

## Sync vs Async Tasks

Background tasks can be either synchronous or asynchronous. Both are supported.

```python
def write_log_sync():
    with open("log.txt", "a") as f:
        f.write("Log entry\n")

@get("/log", background=BackgroundTasks(
    tasks=[
        BackgroundTask(write_log_sync)
    ]
))
def log():
    return {"message": "logged"}
```

---

## What's Next?

You've now learned how to:

- Add and run background tasks
- Combine multiple tasks
- Mix sync and async behavior

👉 Next up: [dependencies](08-dependencies.md) — learn how to use `Inject`, `Injects`, and shared state across your app.
