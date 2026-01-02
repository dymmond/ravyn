# Observables

Observables enable reactive, event-driven programming in Ravyn. When something happens in your application, multiple parts can react independently without tight coupling.

## What You'll Learn

- What observables are and when to use them
- Using the `@observable` decorator
- Sending and listening to events
- Practical event-driven patterns
- Decoupling application logic

## Quick Start

```python
from ravyn import Ravyn, post
from ravyn.utils.decorators import observable

# Handler that sends an event
@post("/register")
@observable(send=["user_registered"])
async def register(email: str, password: str) -> dict:
    # Create user...
    return {"registered": True, "email": email}

# Listener that reacts to the event
@observable(listen=["user_registered"])
async def send_welcome_email():
    print("Sending welcome email...")

# Another listener for the same event
@observable(listen=["user_registered"])
async def assign_default_role():
    print("Assigning default role...")

app = Ravyn()
app.add_route(register)
```

When `/register` is called, both listeners execute automatically!

---

## Why Use Observables?

### Benefits:

- **Decoupling** - Event producers don't know about consumers

- **Scalability** - Add new listeners without changing existing code

- **Maintainability** - Each listener has single responsibility

- **Concurrency** - Listeners execute asynchronously

- **Reusability** - Same event can trigger multiple actions

### Perfect For:

- User registration workflows (email, logging, analytics)
- Payment processing (notifications, fulfillment, receipts)
- Data changes (cache invalidation, webhooks, logging)
- Background tasks (cleanup, processing, notifications)

---

## How Observables Work

1. **Send Event** - Handler decorated with `@observable(send=["event_name"])`
2. **Listen to Event** - Functions decorated with `@observable(listen=["event_name"])`
3. **Automatic Execution** - When sender executes, all listeners execute

```
Handler with send=["event"] → Listener 1 ┐
                            → Listener 2 ├→ All execute automatically
                            → Listener 3 ┘
```

---

## The @observable Decorator

### Sending Events

```python
from ravyn import post
from ravyn.utils.decorators import observable

@post("/login")
@observable(send=["user_logged_in"])
async def login(email: str, password: str) -> dict:
    # Authenticate user...
    return {"token": "abc123"}
```

### Listening to Events

```python
from ravyn.utils.decorators import observable

@observable(listen=["user_logged_in"])
async def log_login_activity():
    print("Logging user login activity...")

@observable(listen=["user_logged_in"])
async def update_last_login():
    print("Updating last login timestamp...")
```

### Multiple Events

Send or listen to multiple events:

```python
# Send multiple events
@post("/purchase")
@observable(send=["payment_success", "order_created"])
async def process_purchase() -> dict:
    return {"order_id": 123}

# Listen to multiple events
@observable(listen=["payment_success", "order_created"])
async def send_confirmation():
    print("Sending confirmation...")
```

---

## Practical Examples

### Example 1: User Registration

```python
from ravyn import post
from ravyn.utils.decorators import observable

# Registration endpoint - sends event
@post("/register")
@observable(send=["user_registered"])
async def register_user(email: str, name: str, password: str) -> dict:
    # Create user in database...
    return {"message": "User registered successfully!", "email": email}

# Listener: Send welcome email
@observable(listen=["user_registered"])
async def send_welcome_email():
    print("� Sending welcome email...")

# Listener: Assign default roles
@observable(listen=["user_registered"])
async def assign_default_roles():
    print("� Assigning default roles to the user...")

# Listener: Log registration
@observable(listen=["user_registered"])
async def log_registration():
    print("Logging user registration...")
```

**What happens:**
1. User calls `POST /register`
2. User is created
3. All three listeners execute automatically
4. Response is returned

---

### Example 2: Payment Processing

```python
from ravyn import post
from ravyn.utils.decorators import observable

# Payment endpoint - sends event
@post("/pay")
@observable(send=["payment_success"])
async def process_payment(amount: float, user_id: int) -> dict:
    # Process payment...
    return {"message": "Payment processed!", "amount": amount}

# Listener: Notify user
@observable(listen=["payment_success"])
async def notify_user():
    print("💳 Notifying user about payment confirmation...")

# Listener: Update database
@observable(listen=["payment_success"])
async def update_database():
    print("� Updating payment database records...")

# Listener: Generate invoice
@observable(listen=["payment_success"])
async def generate_invoice():
    print("📄 Generating invoice for the payment...")
```

One event triggers multiple independent processes

Fully decoupled logic for better maintainability

---

### Example 3: Logging User Activity

```python
from ravyn import post
from ravyn.utils.decorators import observable

@post("/login")
@observable(send=["user_logged_in"])
async def login(email: str, password: str) -> dict:
    # Authenticate...
    return {"message": "User logged in!", "token": "abc123"}

@observable(listen=["user_logged_in"])
async def log_login_activity():
    print("📝 Logging user login activity...")
```

Logs login activity without modifying authentication logic

---

### Example 4: Real-Time Notifications

```python
from ravyn import post
from ravyn.utils.decorators import observable

@post("/comment")
@observable(send=["new_comment"])
async def add_comment(post_id: int, content: str) -> dict:
    # Save comment...
    return {"message": "Comment added!", "post_id": post_id}

@observable(listen=["new_comment"])
async def send_notification():
    print("🔔 Sending notification about the new comment...")
```

Users get notified immediately after a comment is posted

---

### Example 5: Background Data Processing

```python
from ravyn import post
from ravyn.utils.decorators import observable

@post("/upload")
@observable(send=["file_uploaded"])
async def upload_file(filename: str) -> dict:
    # Save file...
    return {"message": "File uploaded!", "filename": filename}

@observable(listen=["file_uploaded"])
async def process_file():
    print("⚙️ Processing uploaded file in background...")

@observable(listen=["file_uploaded"])
async def generate_thumbnail():
    print("🖼️ Generating thumbnail...")
```

Heavy file processing runs asynchronously, without blocking the request

---

### Example 6: Scheduled Tasks & Cleanup

```python
from ravyn.utils.decorators import observable

# Scheduled task sends event
@observable(send=["daily_cleanup"])
async def run_daily_cleanup():
    print("🧹 Running daily cleanup...")
    return {"status": "cleanup_started"}

# Cleanup listeners
@observable(listen=["daily_cleanup"])
async def delete_old_logs():
    print("🗑️ Deleting old log files...")

@observable(listen=["daily_cleanup"])
async def archive_data():
    print("📦 Archiving old data...")

@observable(listen=["daily_cleanup"])
async def clear_temp_files():
    print("🧼 Clearing temporary files...")
```

Scheduled task runs automatically → Triggers multiple cleanup tasks

---

## Common Pitfalls & Fixes

### Pitfall 1: Forgetting the Decorator

**Problem:** Event not sent or received.

```python
# Wrong - missing @observable decorator
@post("/register")
async def register(email: str) -> dict:
    return {"registered": True}

# This listener will never execute!
@observable(listen=["user_registered"])
async def send_email():
    print("Sending email...")
```

**Solution:** Add `@observable` decorator:

```python
# Correct
@post("/register")
@observable(send=["user_registered"])
async def register(email: str) -> dict:
    return {"registered": True}

@observable(listen=["user_registered"])
async def send_email():
    print("Sending email...")
```

### Pitfall 2: Wrong Event Name

**Problem:** Sender and listener use different event names.

```python
# Wrong - event names don't match
@post("/register")
@observable(send=["user_created"])  # "user_created"
async def register() -> dict:
    return {}

@observable(listen=["user_registered"])  # "user_registered" - different!
async def send_email():
    print("Email")
```

**Solution:** Use same event name:

```python
# Correct
@post("/register")
@observable(send=["user_registered"])
async def register() -> dict:
    return {}

@observable(listen=["user_registered"])  # Same name!
async def send_email():
    print("Email")
```

### Pitfall 3: Blocking Operations in Listeners

**Problem:** Slow listener blocks execution.

```python
# Wrong - slow operation
@observable(listen=["user_registered"])
async def slow_email_send():
    import time
    time.sleep(5)  # Blocks for 5 seconds!
    send_email()
```

**Solution:** Use async operations:

```python
# Correct - non-blocking
@observable(listen=["user_registered"])
async def fast_email_send():
    await email_queue.add_task()  # Queue for background processing
```

### Pitfall 4: Error in Listener

**Problem:** Exception in listener.

```python
# Wrong - unhandled error
@observable(listen=["payment_success"])
async def failing_listener():
    raise Exception("Oops!")  # May affect other listeners
```

**Solution:** Handle errors:

```python
# Correct - error handling
@observable(listen=["payment_success"])
async def safe_listener():
    try:
        process_payment()
    except Exception as e:
        logger.error(f"Error in listener: {e}")
```

---

## Best Practices

### 1. Use Descriptive Event Names

```python
# Good - clear event names
"user_registered"
"payment_completed"
"order_shipped"
"cache_invalidated"

# Bad - vague names
"event1"
"update"
"process"
```

### 2. Keep Listeners Focused

```python
# Good - single responsibility
@observable(listen=["user_registered"])
async def send_welcome_email():
    await send_email("Welcome!")

@observable(listen=["user_registered"])
async def create_user_profile():
    await create_profile()

# Bad - doing too much
@observable(listen=["user_registered"])
async def do_everything():
    await send_email("Welcome!")
    await create_profile()
    await assign_permissions()
    await log_analytics()
```

### 3. Document Your Events

```python
# Good - documented events
@post("/register")
@observable(send=["user_registered"])
async def register(email: str) -> dict:
    """
    Register a new user.
    
    Events emitted:

    - user_registered: Triggered after successful registration
    """
    return {"registered": True}
```

---

## Next Steps

Now that you understand observables, explore:

- [Background Tasks](./background-tasks.md) - Async processing
- [Lifespan Events](./lifespan-events.md) - Application lifecycle
- [Interceptors](./interceptors.md) - Request interception
- [Dependencies](./dependencies.md) - Dependency injection
