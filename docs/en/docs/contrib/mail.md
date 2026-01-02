# Mail

The `ravyn.contrib.mail` module provides a **powerful, async-native email system** built for modern applications.

It’s designed to be lightweight yet as powerful as other’s email framework — but without blocking your event loop.

Ravyn leverages the [Lilya mail system](https://www.lilya.dev/contrib/mail/) and applied
**it's own dependency injection but the rest, you can even see in the Lilya documentation**.

## What is the Mail System?

The mail system in Ravyn is a **pluggable email sending framework**.
It abstracts common tasks like:

* Composing messages with **text, HTML, attachments, headers**.
* Sending via different **backends** (SMTP, Console, File, InMemory).
* Rendering **templates with Jinja2** for transactional emails.
* Supporting **multipart/alternative** emails (plain-text + HTML).
* Allowing custom backends for services like Mailgun, Brevo, or Mailchimp.

---

## Why Use Ravyn Mail System?

1. **Async-first**: Unlike Django’s sync system, Ravyn integrates natively with asyncio/anyio.
2. **Flexible backends**: Choose SMTP, debugging backends, or third-party APIs.
3. **Production-ready**: Connection pooling, batch sending, lifecycle hooks.
4. **Customizable**: Write your own backend for any provider.
5. **Lightweight**: You only import what you need, it’s not tied to ORM or heavy dependencies.

---

## Quick Start

### Configure backend

```python
# configs/development/settings.py
from lilya.contrib.mail.backends.smtp import SMTPBackend

MAIL_BACKEND = SMTPBackend(
    host="smtp.gmail.com",
    port=587,
    username="me@gmail.com",
    password="secret",
    use_tls=True,
    default_from_email="noreply@myapp.com",
)

MAIL_TEMPLATES = "myapp/templates/emails"
```

### Setup in app

```python
from ravyn import Ravyn, Gateway, get
from lilya.contrib.mail.startup import setup_mail
from configs.development import settings

app = Ravyn()
setup_mail(app, backend=settings.MAIL_BACKEND, template_dir=settings.MAIL_TEMPLATES)
```

### Send a message

```python
from lilya.contrib.mail import EmailMessage

@get()
async def signup_handler() -> None:
    mailer = request.app.state.mailer
    msg = EmailMessage(
        subject="Welcome!",
        to=["john@example.com"],
        body_text="Hello John, thanks for signing up!",
        body_html="<h1>Hello John 👋</h1><p>Thanks for signing up!</p>",
    )
    await mailer.send(msg)
```

---

## Sending Templated Emails

```python
from ravyn import Ravyn

app = Ravyn()

@app.get("/welcome")
async def send_welcome() -> dict[str, str]:
    mailer = request.app.state.mailer
    await mailer.send_template(
        template_html="welcome.html",
        context={"name": "John", "product": "Ravyn"},
        subject="Welcome to Ravyn",
        to=["john@example.com"],
    )
    return {"status": "sent"}
```

### `welcome.html`

```html
<html>
  <body>
    <h1>Hello {{ name }} 👋</h1>
    <p>Welcome to {{ product }}.</p>
  </body>
</html>
```

If no plain-text template is provided, Ravyn auto-generates one from the HTML.

---

## Available Backends

### SMTP

The standard backend for production use.

Supports **connection reuse/pooling** for efficiency.

```python
from lilya.contrib.mail.backends.smtp import SMTPBackend

backend = SMTPBackend(
    host="smtp.sendgrid.net",
    port=587,
    username="apikey",
    password="SENDGRID_API_KEY",
    use_tls=True,
)
```

---

### Console

Prints emails to stdout, perfect for development.

```python
from lilya.contrib.mail import Mailer
from lilya.contrib.mail.backends.console import ConsoleBackend

mailer = Mailer(backend=ConsoleBackend())
```

---

### File

Stores emails as `.eml` files.

```python
from lilya.contrib.mail.backends.file import FileBackend

backend = FileBackend(directory="tmp/emails")
```

---

### In-Memory

Stores emails in `backend.outbox`, great for testing.

```python
from lilya.contrib.mail.backends.inmemory import InMemoryBackend

backend = InMemoryBackend()
```

---

## Batch Sending

```python
from lilya.contrib.mail import EmailMessage, Mailer
from lilya.contrib.mail.backends.console import ConsoleBackend

msgs = [
    EmailMessage(subject="One", to=["a@example.com"], body_text="Message one"),
    EmailMessage(subject="Two", to=["b@example.com"], body_text="Message two"),
]

mailer = Mailer(backend=ConsoleBackend())
await mailer.send_many(msgs)
```

---

## Custom Backends

You can integrate **any third-party service** (Mailgun, Brevo, Mailchimp, etc.) by extending `BaseMailBackend`.

### Example: Mailgun Backend

```python
import httpx
from lilya.contrib.mail.backends.base import BaseMailBackend
from lilya.contrib.mail.message import EmailMessage

class MailgunBackend(BaseMailBackend):
    def __init__(self, api_key: str, domain: str) -> None:
        self.api_key = api_key
        self.domain = domain

    async def send(self, message: EmailMessage) -> None:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.mailgun.net/v3/{self.domain}/messages",
                auth=("api", self.api_key),
                data={
                    "from": message.from_email or f"noreply@{self.domain}",
                    "to": message.to,
                    "subject": message.subject,
                    "text": message.body_text,
                    "html": message.body_html,
                },
            )
```

### Example: Brevo Backend

```python
import httpx
from lilya.contrib.mail.backends.base import BaseMailBackend
from lilya.contrib.mail.message import EmailMessage

class BrevoBackend(BaseMailBackend):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def send(self, message: EmailMessage) -> None:
        async with httpx.AsyncClient() as client:
            await client.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={"api-key": self.api_key},
                json={
                    "sender": {"email": message.from_email or "noreply@myapp.com"},
                    "to": [{"email": r} for r in message.to],
                    "subject": message.subject,
                    "textContent": message.body_text,
                    "htmlContent": message.body_html,
                },
            )
```

### Example: Mailchimp Transactional (Mandrill)

```python
import httpx
from lilya.contrib.mail.backends.base import BaseMailBackend
from lilya.contrib.mail.message import EmailMessage

class MailchimpBackend(BaseMailBackend):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def send(self, message: EmailMessage) -> None:
        async with httpx.AsyncClient() as client:
            await client.post(
                "https://mandrillapp.com/api/1.0/messages/send.json",
                json={
                    "key": self.api_key,
                    "message": {
                        "from_email": message.from_email,
                        "subject": message.subject,
                        "text": message.body_text,
                        "html": message.body_html,
                        "to": [{"email": r, "type": "to"} for r in message.to],
                    },
                },
            )
```

## A "Real World" Example: Sending emails via Ravyn

Email is often needed for user signups, password resets, or notifications.
With `lilya.contrib.mail`, you can attach a mailer to your app and send messages anywhere.

---

### 1. Configure the Mailer

First, set up the mail backend when creating your app:

```python
from ravyn import Ravyn
from lilya.contrib.mail import setup_mail
from lilya.contrib.mail.backends.smtp import SMTPBackend

app = Ravyn()

# Attach mailer with SMTP backend
setup_mail(
    app,
    backend=SMTPBackend(
        host="smtp.gmail.com",
        port=587,
        username="myapp@gmail.com",
        password="super-secret",
        use_tls=True,
        default_from_email="noreply@myapp.com",
    ),
    template_dir="templates/emails",
)
```

This makes `app.state.mailer` available anywhere in your app.

---

### 2. Create Email Templates

In `templates/emails/welcome.html`:

```html
<h1>Welcome, {{ name }}!</h1>
<p>Thanks for joining our platform.</p>
```

In `templates/emails/welcome.txt`:

```
Welcome, {{ name }}!
Thanks for joining our platform.
```

---

### 3. Send an Email from an Endpoint

With your `app` from Ravyn you can do now this:

```python
from ravyn import Ravyn, JSONResponse, Request

app = Ravyn()

@app.post("/signup")
async def signup(request: Request) -> JSONResponse:
    data = await request.json()
    user_email = data["email"]

    # Send a welcome email
    await request.app.state.mailer.send_template(
        subject="Welcome to MyApp",
        to=[user_email],
        template_html="welcome.html",
        template_text="welcome.txt",
        context={"name": user_email.split("@")[0]},
    )

    return JSONResponse({"message": "User created and welcome email sent"})
```

!!! Note
    Ravyn also has the `Gateway`, this is just an alternative for example purposes.

---

### 4. Switching Backends per Environment

* **Development:**

  ```python
  from lilya.contrib.mail.backends.console import ConsoleBackend
  setup_mail(app, backend=ConsoleBackend())
  ```

* **Testing:**

  ```python
  from lilya.contrib.mail.backends.inmemory import InMemoryBackend
  setup_mail(app, backend=InMemoryBackend())
  ```

* **Production:**

  Use `SMTPBackend` or implement a custom backend (e.g. Mailgun, Brevo).

With this setup:

* Startup/shutdown hooks automatically open/close the SMTP connection.
* You can freely swap backends depending on environment.
* Templated emails keep code clean and consistent.

## Using `Mail` as a Dependency

In addition to accessing `app.state.mailer` directly, Ravyn provides an out-of-the-box dependency
you can inject into any handler: `Mail`.

This is powered by Lilya’s dependency injection system and resolves to the configured global
`Mailer` instance (the one you set up via `setup_mail`).

---

### 1. Configure Mail

```python
from ravyn import Ravyn
from lilya.contrib.mail.startup import setup_mail
from lilya.contrib.mail.backends.smtp import SMTPBackend

app = Ravyn()

setup_mail(
    app,
    backend=SMTPBackend(
        host="smtp.gmail.com",
        port=587,
        username="me@gmail.com",
        password="secret",
        use_tls=True,
        default_from_email="noreply@myapp.com",
    ),
    template_dir="templates/emails",
)
```

---

### 2. Inject Mail with `dependencies`

!!! Warning
    Here is where Ravyn differs from Lilya. Ravyn has its own dependency injection system
    and already ready to be used as per example.

Make sure **you use Any as type for the `Mailer`** to avoid dependency issues.

The `Mail` in Ravyn is already wrapped in a `Inject` object and ready for use.

```python
from typing import Any

from ravyn import Ravyn, Gateway, Inject, Injects, JSONResponse, get
from ravyn.contrib.mail.dependencies import Mail

from lilya.contrib.mail import EmailMessage
from lilya.routing import Path

@get(dependencies={"mailer": Mail})
async def send_welcome(mailer: Any = Injects()) -> JSONResponse:
    msg = EmailMessage(
        subject="Welcome!",
        to=["user@example.com"],
        body_text="Thanks for signing up!",
    )
    await mailer.send(msg)
    return JSONResponse({"status": "sent"})

app = Ravyn(routes=[
    Gateway("/welcome", send_welcome)
])

```

!!! Check
    Here, `mailer: Mail` resolves to the configured global `Mailer` instance.

---

### 3. Failure Modes

* If you forget to call `setup_mail`, injection will raise:

```
RuntimeError: No Mailer configured. Did you forget to call setup_mail(app, backend=...)?
```

* If you override `app.state.mailer` with something invalid, you’ll see the same error.

---

### 4. Overriding in Tests

You can easily replace the `Mail` dependency in tests:

```python
from typing import Any

from ravyn import Ravyn, Inject, Injects
from ravyn.contrib.mail.dependencies import Mail
from lilya.dependencies import Provide

class FakeMailer:
    def __init__(self) -> None:
        self.sent = []

    async def send(self, message: str) -> None:
        self.sent.append(message)

app = Ravyn()
fake = FakeMailer()

@app.post("/test", dependencies={"mailer": Inject(lambda request: fake)})
async def test_handler(mailer: Any = Injects()) -> dict[str, bool]:
    await mailer.send("hello")
    return {"ok": True}
```

Now your handler uses the fake mailer, perfect for asserting email logic in unit tests without hitting a real SMTP server.

---

### 5. Background Tasks & Beyond

Because `Mail` is a normal dependency, you can also use it inside background tasks or WebSocket endpoints:

```python
from typing import Any

from ravyn.background import BackgroundTask

@app.post("/signup", dependencies={"mailer": Mail})
async def signup(user: dict, mailer: Mail) -> dict[str, Any]:
    async def send_welcome():
        await mailer.send_template(
            subject="Welcome!",
            to=[user["email"]],
            template_html="welcome.html",
            context={"name": user["name"]},
        )

    return {"ok": True, "background": BackgroundTask(send_welcome)}
```

### Notes

* Use `setup_mail` once in `main.py` (or whatever file you have your application instance).
* Inject the configured `Mailer` anywhere with `dependencies={"mailer": Mail}`.
* Clean error messages if it isn’t configured.
* Easy to override in tests.

---

## Best Practices

* Always configure a **default from email** (`noreply@...`) in production.
* Use **HTML + text multipart** to avoid spam filters.
* In dev, prefer **ConsoleBackend** or **FileBackend**.
* For tests, use **InMemoryBackend** and assert on `.outbox`.
* For production, use **SMTPBackend** or a **custom API backend**.
* Keep **transactional templates** in a dedicated directory (`templates/emails/`).

---

## Summary

* `EmailMessage`: Describes what to send.
* `Mailer`: Coordinates sending, templating, batching and comes from `ravyn.contrib.mail.dependencies`.
* `BaseMailBackend`: Pluggable backends (SMTP, Console, File, InMemory).
* **Custom backends**: Easy integration with services like Mailgun, Brevo, Mailchimp, etc.

With these tools, Ravyn's mail system is **powerful**, but async-native, lighter, and more flexible.
