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

Observables enable **event-driven architecture** where components react to events without knowing about each other. This promotes loose coupling and makes your application more maintainable.

### Benefits:

- **Decoupling** - Event producers don't know about consumers

- **Scalability** - Add new listeners without changing existing code

- **Maintainability** - Each listener has single responsibility

- **Concurrency** - Listeners execute asynchronously

- **Reusability** - Same event can trigger multiple actions

### Perfect For:

- **User registration workflows** - Email, logging, analytics
- **Payment processing** - Notifications, fulfillment, receipts
- **Data changes** - Cache invalidation, webhooks, logging
- **Background tasks** - Cleanup, processing, notifications

### When to Use Observables vs Background Tasks

**Use Observables when:**
- Multiple independent actions need to trigger from one event
- You want loose coupling between components
- Different parts of your app need to react to the same event
- You're building event-driven workflows

**Use Background Tasks when:**
- You need to defer a single, specific task
- Task should run after the response is sent to the client
- You want simple, one-off async operations
- Task doesn't need to trigger multiple handlers

**Example Comparison:**

```python
# Observables: Multiple handlers react to one event
from ravyn import post
from ravyn.utils.decorators import observable

@post("/register")
@observable(send=["user_registered"])
async def register(email: str) -> dict:
    return {"registered": True}

@observable(listen=["user_registered"])
async def send_email():
    print("Sending email...")

@observable(listen=["user_registered"])
async def log_analytics():
    print("Logging analytics...")

# Background Tasks: Single deferred task
from ravyn import post, BackgroundTask

@post("/process")
async def process_data(background_tasks: BackgroundTask) -> dict:
    background_tasks.add_task(expensive_computation)
    return {"processing": True}
```

**Decision Matrix:**

| Need | Use Observables | Use Background Tasks |
|------|----------------|---------------------|
| Multiple reactions to one event | ✅ Yes | ❌ No |
| Loose coupling | ✅ Yes | ❌ No |
| Simple deferred task | ❌ No | ✅ Yes |
| Event-driven architecture | ✅ Yes | ❌ No |
| One-off async operation | ❌ No | ✅ Yes |

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

A complete user registration flow demonstrating event-driven architecture:

```python
from ravyn import Ravyn, post
from ravyn.utils.decorators import observable

# Registration endpoint - sends event
@post("/register")
@observable(send=["user_registered"])
async def register_user(email: str, name: str, password: str) -> dict:
    # Create user in database...
    user_id = await create_user_in_database(email, name, password)

    return {
        "message": "User registered successfully!",
        "user_id": user_id,
        "email": email
    }

# Listener 1: Send welcome email
@observable(listen=["user_registered"])
async def send_welcome_email():
    """Send personalized welcome email to new user"""
    print("📧 Sending welcome email...")
    # Email sending logic here
    await send_email(to=email, template="welcome")

# Listener 2: Assign default roles
@observable(listen=["user_registered"])
async def assign_default_roles():
    """Assign default 'user' role and permissions"""
    print("🔒 Assigning default roles to the user...")
    # Role assignment logic here
    await assign_role(user_id, role="user")

# Listener 3: Log registration
@observable(listen=["user_registered"])
async def log_registration():
    """Log registration event for analytics"""
    print("📊 Logging user registration...")
    # Analytics logging here
    await log_analytics_event("user_registered", user_id=user_id)

# Listener 4: Create user profile
@observable(listen=["user_registered"])
async def create_user_profile():
    """Initialize empty user profile"""
    print("👤 Creating user profile...")
    await create_profile(user_id)

app = Ravyn()
app.add_route(register_user)
```

**What happens when `POST /register` is called:**
1. User is created in database
2. Response is prepared with `user_id` and `email`
3. `user_registered` event is triggered
4. All four listeners execute **concurrently**:
   - Welcome email is queued
   - Default role is assigned
   - Analytics event is logged
   - User profile is created
5. Response is returned to client

**Key Benefits:**
- Each listener is independent and focused
- Easy to add new listeners (e.g., Slack notification) without modifying registration logic
- Failure in one listener doesn't affect others

---

### Example 2: E-commerce Order Processing

Event-driven order fulfillment pipeline:

```python
from ravyn import post
from ravyn.utils.decorators import observable

# Order endpoint - triggers multiple events
@post("/orders")
@observable(send=["order_created", "payment_required"])
async def create_order(user_id: int, items: list, payment_method: str) -> dict:
    # Create order in database
    order_id = await save_order(user_id, items)
    total_amount = calculate_total(items)

    return {
        "order_id": order_id,
        "total": total_amount,
        "status": "pending_payment"
    }

# Listener: Process payment
@observable(listen=["payment_required"])
async def process_payment():
    """Charge customer's payment method"""
    print("💳 Processing payment...")
    payment_success = await charge_payment(payment_method, total_amount)

    if payment_success:
        # Trigger next event in the pipeline
        await trigger_event("payment_success")

# Listener: Send order confirmation
@observable(listen=["order_created"])
async def send_order_confirmation():
    """Email customer with order details"""
    print("📧 Sending order confirmation email...")
    await send_email(user_id, template="order_confirmation", order_id=order_id)

# Listener: Update inventory
@observable(listen=["payment_success"])
async def update_inventory():
    """Reduce stock for purchased items"""
    print("📦 Updating inventory...")
    for item in items:
        await reduce_stock(item.product_id, item.quantity)

# Listener: Notify warehouse
@observable(listen=["payment_success"])
async def notify_warehouse():
    """Send fulfillment request to warehouse"""
    print("🏭 Notifying warehouse for fulfillment...")
    await send_warehouse_notification(order_id)

# Listener: Track analytics
@observable(listen=["order_created"])
async def track_order_analytics():
    """Log order for business intelligence"""
    print("📊 Tracking order analytics...")
    await log_analytics("order_created", order_id=order_id, total=total_amount)
```

**Event Flow:**
```
POST /orders
    ↓
order_created event → [send_order_confirmation, track_order_analytics]
payment_required event → [process_payment]
    ↓
payment_success event → [update_inventory, notify_warehouse]
```

This pattern creates a **loosely-coupled pipeline** where each stage can evolve independently.

---

### Example 3: Real-Time Notifications with WebSockets

Combine observables with WebSockets for real-time updates:

```python
from ravyn import post, websocket
from ravyn.utils.decorators import observable

# Global WebSocket connections store
active_connections = []

@websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for real-time notifications"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            await websocket.receive_text()
    except:
        active_connections.remove(websocket)

@post("/comment")
@observable(send=["new_comment"])
async def add_comment(post_id: int, user_id: int, content: str) -> dict:
    # Save comment to database
    comment = await save_comment(post_id, user_id, content)

    return {
        "message": "Comment added!",
        "comment_id": comment.id,
        "post_id": post_id
    }

# Listener: Broadcast to all connected WebSocket clients
@observable(listen=["new_comment"])
async def broadcast_new_comment():
    """Send real-time notification to all connected clients"""
    print("🔔 Broadcasting new comment to all users...")

    notification = {
        "type": "new_comment",
        "post_id": post_id,
        "content": content
    }

    for connection in active_connections:
        await connection.send_json(notification)

# Listener: Send email to post author
@observable(listen=["new_comment"])
async def notify_post_author():
    """Email the post author about the new comment"""
    print("📧 Notifying post author...")
    post = await get_post(post_id)
    await send_email(post.author_email, template="new_comment")

# Listener: Update comment count cache
@observable(listen=["new_comment"])
async def update_comment_count():
    """Invalidate comment count cache"""
    print("🔄 Updating comment count...")
    from ravyn.core.caches.memory import InMemoryCache
    cache = InMemoryCache()
    await cache.delete(f"comment_count:{post_id}")
```

**Real-time event flow:**
1. User posts a comment via `POST /comment`
2. Comment is saved to database
3. `new_comment` event triggers three listeners:
   - WebSocket broadcast (instant UI update for all users)
   - Email notification (async, doesn't block response)
   - Cache invalidation (ensures fresh data on next request)

---

### Example 4: Cache Invalidation Pattern

Use observables to automatically invalidate caches when data changes:

```python
from ravyn import get, post, put, delete
from ravyn.utils.decorators import observable, cache
from ravyn.core.caches.memory import InMemoryCache

cache_backend = InMemoryCache()

# Cached GET endpoint
@get("/products")
@cache(ttl=600, backend=cache_backend)
async def get_products() -> dict:
    """Fetch all products (cached for 10 minutes)"""
    products = await fetch_products_from_db()
    return {"products": products}

# POST endpoint - triggers cache invalidation
@post("/products")
@observable(send=["product_modified"])
async def create_product(name: str, price: float) -> dict:
    product = await save_product(name, price)
    return {"created": True, "product": product}

# PUT endpoint - triggers cache invalidation
@put("/products/{product_id}")
@observable(send=["product_modified"])
async def update_product(product_id: int, name: str, price: float) -> dict:
    await update_product_in_db(product_id, name, price)
    return {"updated": True}

# DELETE endpoint - triggers cache invalidation
@delete("/products/{product_id}")
@observable(send=["product_modified"])
async def delete_product(product_id: int) -> dict:
    await delete_product_from_db(product_id)
    return {"deleted": True}

# Listener: Invalidate product cache
@observable(listen=["product_modified"])
async def invalidate_product_cache():
    """Clear product cache whenever products are modified"""
    print("🔄 Invalidating product cache...")
    await cache_backend.delete("get_products")
```

**Benefits:**
- Cache invalidation logic is centralized in one listener
- All modification endpoints trigger the same event
- Easy to extend (e.g., add webhook notifications)

---

### Example 5: Multi-Stage Data Processing Pipeline

Build complex data pipelines with observables:

```python
from ravyn import post
from ravyn.utils.decorators import observable

# Stage 1: File upload
@post("/upload")
@observable(send=["file_uploaded"])
async def upload_file(filename: str, file_data: bytes) -> dict:
    # Save file to storage
    file_path = await save_file(filename, file_data)

    return {
        "message": "File uploaded!",
        "filename": filename,
        "path": file_path
    }

# Stage 2: Validate file
@observable(listen=["file_uploaded"])
async def validate_file():
    """Check file format and size"""
    print("✅ Validating file...")
    is_valid = await validate_file_format(file_path)

    if is_valid:
        # Trigger next stage
        await trigger_event("file_validated")
    else:
        await trigger_event("file_invalid")

# Stage 3: Process file (only if valid)
@observable(listen=["file_validated"])
async def process_file():
    """Extract data from file"""
    print("⚙️ Processing uploaded file...")
    data = await extract_data_from_file(file_path)

    # Store extracted data
    await save_extracted_data(data)

    # Trigger next stage
    await trigger_event("file_processed")

# Stage 4: Generate thumbnail (parallel with processing)
@observable(listen=["file_validated"])
async def generate_thumbnail():
    """Create thumbnail if file is an image"""
    print("🖼️ Generating thumbnail...")

    if is_image_file(file_path):
        await create_thumbnail(file_path)

# Stage 5: Notify user of completion
@observable(listen=["file_processed"])
async def notify_completion():
    """Send email when processing completes"""
    print("📧 Notifying user of completion...")
    await send_email(user_email, template="file_processed")

# Error handler: Handle invalid files
@observable(listen=["file_invalid"])
async def handle_invalid_file():
    """Clean up and notify user of invalid file"""
    print("❌ Handling invalid file...")
    await delete_file(file_path)
    await send_email(user_email, template="file_invalid")
```

**Pipeline Flow:**
```
file_uploaded
    ↓
file_validated → [process_file, generate_thumbnail]
    ↓
file_processed → [notify_completion]

OR

file_invalid → [handle_invalid_file]
```

This creates a **robust, event-driven pipeline** with parallel processing and error handling.

---

### Example 6: Scheduled Tasks with Observables

Combine scheduler with observables for complex workflows:

```python
from ravyn import Ravyn
from ravyn.utils.decorators import observable
from ravyn.contrib.schedulers.asyncz.decorator import scheduler

app = Ravyn()

# Scheduled task sends event
@scheduler(name="daily_cleanup", cron="0 2 * * *")  # Runs at 2 AM daily
@observable(send=["daily_cleanup"])
async def run_daily_cleanup():
    """Trigger daily cleanup workflow"""
    print("🧹 Starting daily cleanup workflow...")
    return {"status": "cleanup_started"}

# Cleanup listeners execute in parallel
@observable(listen=["daily_cleanup"])
async def delete_old_logs():
    """Remove log files older than 30 days"""
    print("🗑️ Deleting old log files...")
    await cleanup_logs(days=30)

@observable(listen=["daily_cleanup"])
async def archive_data():
    """Move old data to cold storage"""
    print("📦 Archiving old data...")
    await move_to_archive(days=90)

@observable(listen=["daily_cleanup"])
async def clear_temp_files():
    """Clear temporary files"""
    print("🧼 Clearing temporary files...")
    await delete_temp_files()

@observable(listen=["daily_cleanup"])
async def optimize_database():
    """Run database optimization"""
    print("⚡ Optimizing database tables...")
    await run_db_optimization()

# Send notification when all cleanup tasks complete
@observable(listen=["daily_cleanup"])
async def send_cleanup_report():
    """Email admin with cleanup summary"""
    print("📧 Sending cleanup report...")
    await send_admin_email(template="cleanup_report")
```

**Scheduled workflow:**
- Scheduler triggers `daily_cleanup` event at 2 AM
- Five listeners execute **concurrently**
- Admin receives summary email
- No blocking or sequential execution

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
