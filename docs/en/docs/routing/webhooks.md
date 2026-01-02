# Webhooks

Create webhook endpoints to receive and process events from external services.

## What You'll Learn

- What webhooks are
- Creating webhook endpoints
- Validating webhook signatures
- Best practices for webhooks

## Quick Start

```python
from ravyn import Ravyn, post

@post("/webhooks/stripe")
async def stripe_webhook(data: dict) -> dict:
    event_type = data.get("type")
    
    if event_type == "payment.succeeded":
        # Process payment
        pass
    
    return {"received": True}

app = Ravyn(routes=[Gateway(handler=stripe_webhook)])
```

---

## What are Webhooks?

**Webhooks** are HTTP callbacks that external services use to notify your application about events. Instead of polling for updates, services push data to your endpoint.

### Common Use Cases

- **Payment Processing** - Stripe, PayPal notifications

- **Git Events** - GitHub, GitLab push events

- **Communication** - Slack, Discord messages

- **CRM Updates** - Salesforce, HubSpot changes

- **Monitoring** - Alert notifications

---

## Creating Webhook Endpoints

### Basic Webhook

```python
from ravyn import post

@post("/webhooks/github")
async def github_webhook(data: dict) -> dict:
    event = data.get("action")
    repository = data.get("repository", {}).get("name")
    
    print(f"GitHub event: {event} on {repository}")
    
    return {"status": "received"}
```

### With Request Headers

```python
from ravyn import post, Request

@post("/webhooks/stripe")
async def stripe_webhook(request: Request) -> dict:
    # Get signature from headers
    signature = request.headers.get("stripe-signature")
    
    # Get raw body
    body = await request.body()
    
    # Verify signature
    if not verify_stripe_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Process webhook
    data = await request.json()
    return {"received": True}
```

---

## Webhook Signature Verification

### Stripe Example

```python
import hmac
import hashlib
from ravyn import post, Request, HTTPException

STRIPE_WEBHOOK_SECRET = "whsec_..."

@post("/webhooks/stripe")
async def stripe_webhook(request: Request) -> dict:
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        # Verify signature
        expected_sig = hmac.new(
            STRIPE_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(sig_header, expected_sig):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Process event
        event = await request.json()
        handle_stripe_event(event)
        
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### GitHub Example

```python
import hmac
import hashlib
from ravyn import post, Request, HTTPException

GITHUB_WEBHOOK_SECRET = "your-secret"

@post("/webhooks/github")
async def github_webhook(request: Request) -> dict:
    payload = await request.body()
    signature = request.headers.get("x-hub-signature-256")
    
    # Verify signature
    expected = "sha256=" + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Process event
    event = await request.json()
    event_type = request.headers.get("x-github-event")
    
    if event_type == "push":
        handle_push_event(event)
    
    return {"status": "received"}
```

---

## Event Handling Patterns

### Pattern 1: Event Router

```python
from ravyn import post, Request

@post("/webhooks/stripe")
async def stripe_webhook(request: Request) -> dict:
    event = await request.json()
    event_type = event.get("type")
    
    handlers = {
        "payment_intent.succeeded": handle_payment_success,
        "payment_intent.failed": handle_payment_failure,
        "customer.created": handle_customer_created,
    }
    
    handler = handlers.get(event_type)
    if handler:
        await handler(event)
    
    return {"received": True}

async def handle_payment_success(event: dict):
    payment_id = event["data"]["object"]["id"]
    # Process successful payment
    
async def handle_payment_failure(event: dict):
    # Handle failed payment
    pass
```

### Pattern 2: Background Processing

```python
from ravyn import post, BackgroundTask

@post("/webhooks/github")
async def github_webhook(data: dict, background_tasks: BackgroundTask) -> dict:
    # Queue for background processing
    background_tasks.add_task(process_github_event, data)
    
    # Return immediately
    return {"status": "queued"}

async def process_github_event(data: dict):
    # Heavy processing here
    event_type = data.get("action")
    # ... process event
```

### Pattern 3: Database Logging

```python
from ravyn import post

@post("/webhooks/stripe")
async def stripe_webhook(data: dict) -> dict:
    # Log webhook to database
    await WebhookLog.create(
        source="stripe",
        event_type=data.get("type"),
        payload=data,
        received_at=datetime.utcnow()
    )
    
    # Process event
    await process_stripe_event(data)
    
    return {"received": True}
```

---

## Security Best Practices

### 1. Always Verify Signatures

```python
# Good - signature verification
@post("/webhooks/service")
async def webhook(request: Request) -> dict:
    if not verify_signature(request):
        raise HTTPException(status_code=401)
    
    data = await request.json()
    return {"received": True}
```

### 2. Use HTTPS Only

```python
# Good - enforce HTTPS
from ravyn import post, Request, HTTPException

@post("/webhooks/stripe")
async def stripe_webhook(request: Request) -> dict:
    if request.url.scheme != "https":
        raise HTTPException(status_code=403, detail="HTTPS required")
    
    # Process webhook
    return {"received": True}
```

### 3. Rate Limiting

```python
# Good - rate limiting
from ravyn import post
from ravyn.middleware import RateLimitMiddleware

@post(
    "/webhooks/github",
    middleware=[RateLimitMiddleware(max_requests=100, window=60)]
)
async def github_webhook(data: dict) -> dict:
    return {"received": True}
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Not Returning Quickly

**Problem:** Long processing blocks webhook response.

```python
# Wrong - slow processing
@post("/webhooks/stripe")
async def stripe_webhook(data: dict) -> dict:
    await process_payment(data)  # Takes 30 seconds!
    return {"received": True}
```

**Solution:** Use background tasks:

```python
# Correct - background processing
@post("/webhooks/stripe")
async def stripe_webhook(data: dict, background_tasks: BackgroundTask) -> dict:
    background_tasks.add_task(process_payment, data)
    return {"received": True}  # Returns immediately
```

### Pitfall 2: Missing Signature Verification

**Problem:** Anyone can send fake webhooks.

```python
# Wrong - no verification
@post("/webhooks/stripe")
async def stripe_webhook(data: dict) -> dict:
    process_payment(data)  # Vulnerable!
    return {"received": True}
```

**Solution:** Always verify signatures:

```python
# Correct - verified
@post("/webhooks/stripe")
async def stripe_webhook(request: Request) -> dict:
    if not verify_stripe_signature(request):
        raise HTTPException(status_code=401)
    
    data = await request.json()
    return {"received": True}
```

### Pitfall 3: Not Handling Retries

**Problem:** Service retries on any error.

```python
# Wrong - crashes on duplicate
@post("/webhooks/stripe")
async def stripe_webhook(data: dict) -> dict:
    await Payment.create(id=data["id"])  # Fails on retry!
    return {"received": True}
```

**Solution:** Make idempotent:

```python
# Correct - idempotent
@post("/webhooks/stripe")
async def stripe_webhook(data: dict) -> dict:
    payment_id = data["id"]
    
    # Check if already processed
    existing = await Payment.get_or_none(id=payment_id)
    if existing:
        return {"received": True, "duplicate": True}
    
    # Process new webhook
    await Payment.create(id=payment_id)
    return {"received": True}
```

---

## Testing Webhooks

### Local Testing with ngrok

```bash
# Install ngrok
npm install -g ngrok

# Start your Ravyn app
ravyn run

# Expose local server
ngrok http 8000

# Use ngrok URL in webhook settings
# https://abc123.ngrok.io/webhooks/stripe
```

### Mock Webhooks

```python
from ravyn import RavynTestClient

def test_stripe_webhook():
    with RavynTestClient(app) as client:
        payload = {
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_123"}}
        }
        
        response = client.post("/webhooks/stripe", json=payload)
        assert response.status_code == 200
        assert response.json() == {"received": True}
```

---

## Complete Example

```python
from ravyn import Ravyn, post, Request, HTTPException, BackgroundTask
import hmac
import hashlib

WEBHOOK_SECRET = "your-secret-key"

def verify_signature(request: Request, secret: str) -> bool:
    """Verify webhook signature."""
    signature = request.headers.get("x-webhook-signature")
    if not signature:
        return False
    
    payload = request.body()
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)

@post("/webhooks/payment")
async def payment_webhook(
    request: Request,
    background_tasks: BackgroundTask
) -> dict:
    # Verify signature
    if not verify_signature(request, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse event
    event = await request.json()
    event_type = event.get("type")
    
    # Log webhook
    await WebhookLog.create(
        event_type=event_type,
        payload=event
    )
    
    # Process in background
    background_tasks.add_task(process_payment_event, event)
    
    return {"status": "received", "event_type": event_type}

async def process_payment_event(event: dict):
    """Process payment event in background."""
    event_type = event.get("type")
    
    if event_type == "payment.succeeded":
        await handle_payment_success(event)
    elif event_type == "payment.failed":
        await handle_payment_failure(event)

app = Ravyn(routes=[Gateway(handler=payment_webhook)])
```

---

## Next Steps

- [Handlers](./handlers.md) - HTTP method decorators
- [Background Tasks](../background-tasks.md) - Async task processing
- [Security](../security/index.md) - Authentication & authorization
- [Testing](../testclient.md) - Test your webhooks
