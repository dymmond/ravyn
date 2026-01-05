# CSRFConfig

Imagine you're a bank teller. Someone walks in with a withdrawal slip that looks legitimate, has the right account number, and seems properly filled out. But it's actually a forgery - the real account holder never authorized it.

CSRF (Cross-Site Request Forgery) attacks work the same way. An attacker tricks your browser into making requests that look legitimate because you're already logged in. CSRF protection is like adding a unique, time-sensitive code to each transaction that only the real user knows.

Protect your Ravyn application from CSRF attacks with built-in middleware.

## What You'll Learn

- What CSRF is and why it's dangerous
- Configuring CSRF protection
- Using CSRF tokens in forms
- Best practices for CSRF security

## Quick Start

```python
from ravyn import Ravyn
from ravyn.config import CSRFConfig

app = Ravyn(
    csrf_config=CSRFConfig(
        secret="your-secret-key-here"
    )
)
```

---

## What is CSRF?

**CSRF** (Cross-Site Request Forgery) is an attack where a malicious site tricks users into performing unwanted actions on your site.

### How CSRF Attacks Work

1. User logs into your site (`example.com`)
2. User visits malicious site (`evil.com`)
3. Malicious site sends request to `example.com` using user's session
4. Your site processes the request (delete account, transfer money, etc.)

### CSRF Protection

Ravyn's CSRF middleware generates unique tokens that must be included in state-changing requests (POST, PUT, DELETE).

---

## Basic Configuration

### Minimal Setup

```python
from ravyn import Ravyn
from ravyn.config import CSRFConfig

app = Ravyn(
    csrf_config=CSRFConfig(
        secret="your-secret-key-change-this-in-production"
    )
)
```

### With Custom Settings

```python
app = Ravyn(
    csrf_config=CSRFConfig(
        secret="your-secret-key",
        cookie_name="csrftoken",
        header_name="X-CSRF-Token",
        cookie_secure=True,  # HTTPS only
        cookie_httponly=True
    )
)
```

---

## Configuration Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `secret` | str | Secret key for token generation | **Required** |
| `cookie_name` | str | CSRF cookie name | `"csrftoken"` |
| `header_name` | str | CSRF header name | `"X-CSRF-Token"` |
| `cookie_secure` | bool | HTTPS only cookie | `False` |
| `cookie_httponly` | bool | Prevent JavaScript access | `True` |
| `cookie_samesite` | str | SameSite attribute | `"lax"` |

---

## Using CSRF Tokens

### In HTML Forms

```html
<form method="POST" action="/submit">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <input type="text" name="username">
    <button type="submit">Submit</button>
</form>
```

### In JavaScript/AJAX

```javascript
// Get CSRF token from cookie
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Include in request header
fetch('/api/data', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': getCookie('csrftoken')
    },
    body: JSON.stringify({data: 'value'})
});
```

### In Templates

```html
<!-- Jinja2 template -->
<form method="POST">
    {{ csrf_input }}
    <!-- or -->
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    
    <input type="text" name="data">
    <button>Submit</button>
</form>
```

---

## Using with Settings

```python
from ravyn import RavynSettings
from ravyn.config import CSRFConfig

class AppSettings(RavynSettings):
    csrf_config: CSRFConfig = CSRFConfig(
        secret="your-secret-key",
        cookie_secure=True,
        cookie_httponly=True
    )

app = Ravyn(settings_module=AppSettings)
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Missing Secret Key

**Problem:** No secret key configured.

```python
# Wrong - no secret
csrf_config = CSRFConfig()  # Error!
```

**Solution:** Always provide a secret:

```python
# Correct
csrf_config = CSRFConfig(secret="your-secret-key")
```

### Pitfall 2: AJAX Requests Failing

**Problem:** Forgot to include CSRF token in headers.

```javascript
// Wrong - no CSRF token
fetch('/api/data', {
    method: 'POST',
    body: JSON.stringify({data: 'value'})
});
```

**Solution:** Include CSRF token:

```javascript
// Correct
fetch('/api/data', {
    method: 'POST',
    headers: {
        'X-CSRF-Token': getCookie('csrftoken')
    },
    body: JSON.stringify({data: 'value'})
});
```

### Pitfall 3: Insecure Cookie in Production

**Problem:** Not using secure cookies over HTTPS.

```python
# Wrong - insecure in production
csrf_config = CSRFConfig(
    secret="key",
    cookie_secure=False  # Vulnerable!
)
```

**Solution:** Enable secure cookies:

```python
# Correct
csrf_config = CSRFConfig(
    secret="key",
    cookie_secure=True,  # HTTPS only
    cookie_httponly=True
)
```

---

## Best Practices

### 1. Use Strong Secret Keys

```python
# Good - strong random secret
import secrets

csrf_config = CSRFConfig(
    secret=secrets.token_urlsafe(32)
)
```

### 2. Enable Secure Cookies in Production

```python
# Good - secure settings
import os

csrf_config = CSRFConfig(
    secret=os.getenv("CSRF_SECRET"),
    cookie_secure=True,  # HTTPS only
    cookie_httponly=True,
    cookie_samesite="strict"
)
```

### 3. Use Environment Variables

```python
# Good - configurable
import os

csrf_config = CSRFConfig(
    secret=os.getenv("CSRF_SECRET", "dev-secret-change-in-prod")
)
```

---

## Exempting Routes

Some routes (like webhooks) may need to bypass CSRF:

```python
from ravyn import post

@post("/webhook", csrf_exempt=True)
async def webhook(data: dict) -> dict:
    # Process webhook (no CSRF check)
    return {"received": True}
```

---

## Learn More

- [OWASP CSRF Guide](https://owasp.org/www-community/attacks/csrf)
- [CSRFConfig Reference](../references/configurations/csrf.md)
- [Security Best Practices](../security/index.md)

---

## Next Steps

- [CORSConfig](./cors.md) - CORS configuration
- [SessionConfig](./session.md) - Session management
- [JWTConfig](./jwt.md) - JWT authentication
