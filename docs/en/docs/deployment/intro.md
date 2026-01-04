# Deployment Introduction

Deployment is the process of taking your application from your development environment and making it accessible to users worldwide. Just like moving a house to a new location where people can visit, deployment moves your application to a server where users can access it.

The good news? Ravyn is a standard ASGI application, which means you have countless deployment options.

## What You'll Learn

- What deployment means
- Different deployment strategies
- Choosing the right platform
- Environment configuration best practices
- Production readiness checklist

---

## What is Deployment?

**Deployment** is the process of making your application available to users outside your local development environment.

This involves:

- **Hosting** - Finding a server or platform to run your code
- **Configuration** - Setting up environment variables and secrets
- **Infrastructure** - Ensuring adequate CPU, memory, and storage
- **Networking** - Making your app accessible via the internet
- **Monitoring** - Tracking performance and errors

---

## Deployment Strategies

There's no one-size-fits-all approach. Your deployment strategy depends on:

### Budget

**Self-Hosted (Lower Cost)**
- VPS providers (DigitalOcean, Linode, Vultr)
- Requires more maintenance
- Full control over infrastructure

**Cloud Managed (Higher Cost, Less Maintenance)**
- AWS, Azure, GCP
- Render, Heroku, Railway
- Automated scaling and management

### Scale

**Small Applications**
- Single server deployment
- Shared hosting
- Serverless functions

**Large Applications**
- Multiple servers with load balancing
- Container orchestration (Kubernetes)
- Auto-scaling infrastructure

### Technical Expertise

**Beginner-Friendly**
- Render, Heroku, Railway
- One-click deployments
- Managed databases

**Advanced**
- AWS, GCP, Azure
- Docker + Kubernetes
- Custom infrastructure

---

## Deployment Options

### 1. Docker (Recommended)

**Best for:** Consistency across environments

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Advantages:**
- Same environment everywhere
- Easy to scale
- Works on any platform

[Complete Docker Guide →](./docker.md)

### 2. Cloud Platforms

**Render** (Easiest)
```yaml
# render.yaml
services:
  - type: web
    name: myapp
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Heroku**
```
# Procfile
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**AWS, Azure, GCP**
- More complex setup
- Greater flexibility
- Better for large-scale apps

### 3. Traditional VPS

**Setup:**
1. Rent a VPS (DigitalOcean, Linode)
2. Install Python and dependencies
3. Set up Nginx as reverse proxy
4. Use systemd or supervisor for process management

**Example systemd service:**
```ini
[Unit]
Description=Ravyn Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/myapp
ExecStart=/usr/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Serverless

**AWS Lambda, Google Cloud Functions**

Best for:
- Event-driven applications
- Infrequent traffic
- Pay-per-request pricing

**Limitations:**
- Cold start latency
- Execution time limits
- Stateless only

---

## Environment Configuration

### Using Pydantic Settings

Ravyn uses Pydantic for settings, making environment configuration clean:

```python
# settings.py
from ravyn import RavynSettings
from pydantic import Field

class ProductionSettings(RavynSettings):
    debug: bool = False
    secret_key: str = Field(..., env='SECRET_KEY')
    database_url: str = Field(..., env='DATABASE_URL')
    allowed_hosts: list[str] = Field(default_factory=list)
    
    class Config:
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            # Parse comma-separated lists
            if field_name == "allowed_hosts":
                return [host.strip() for host in raw_val.split(",")]
            return cls.json_loads(raw_val)
```

### Environment Variables

```shell
# .env file (never commit this!)
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/db
ALLOWED_HOSTS=example.com,www.example.com
```

### Loading Complex Types

For lists, dicts, and complex types:

```python
from typing import List, Any
from ravyn import RavynSettings
from pydantic import Field

class AppSettings(RavynSettings):
    allowed_hosts: List[str] = Field(..., env='ALLOWED_HOSTS')
    
    class Config:
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            if field_name == "allowed_hosts":
                return [value.strip() for value in raw_val.split(",")]
            return cls.json_loads(raw_val)
```

See [Pydantic's environment variable parsing](https://github.com/pydantic/pydantic/pull/4406/files) for more details.

---

## Production Checklist

### Security ✅

- [ ] Disable debug mode
- [ ] Use HTTPS/SSL
- [ ] Set strong secret keys
- [ ] Configure CORS properly
- [ ] Enable CSRF protection
- [ ] Use environment variables for secrets
- [ ] Disable OpenAPI docs (optional)

### Performance ✅

- [ ] Use production ASGI server (Uvicorn/Hypercorn)
- [ ] Configure multiple workers
- [ ] Set up caching
- [ ] Optimize database queries
- [ ] Enable gzip compression
- [ ] Use a CDN for static files

### Reliability ✅

- [ ] Set up health checks
- [ ] Configure logging
- [ ] Implement error tracking (Sentry)
- [ ] Set up monitoring (Datadog, New Relic)
- [ ] Plan for backups
- [ ] Test failover scenarios
- [ ] Document deployment process

---

## Common Pitfalls & Fixes

### Pitfall 1: Debug Mode in Production

**Problem:** Sensitive information exposed.

```python
# Wrong
app = Ravyn(debug=True)
```

**Solution:**
```python
# Correct
import os
app = Ravyn(debug=os.getenv("DEBUG", "false").lower() == "true")
```

### Pitfall 2: Hardcoded Configuration

**Problem:** Can't change settings without code changes.

**Solution:** Use environment variables:
```python
# settings.py
import os

class Settings(RavynSettings):
    database_url: str = os.getenv("DATABASE_URL")
    secret_key: str = os.getenv("SECRET_KEY")
```

### Pitfall 3: Single Worker

**Problem:** Poor performance under load.

**Solution:** Use multiple workers:
```shell
uvicorn app.main:app --workers 4
```

---

## Best Practices

### 1. Use Docker

Ensures consistency across all environments:

```dockerfile
FROM python:3.11-slim
# ... setup ...
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--workers", "4"]
```

### 2. Separate Settings by Environment

```python
# settings/development.py
class DevelopmentSettings(RavynSettings):
    debug: bool = True
    
# settings/production.py
class ProductionSettings(RavynSettings):
    debug: bool = False
    enable_openapi: bool = False
```

### 3. Use a Reverse Proxy

Nginx or Caddy in front of your ASGI server:

```nginx
server {
    listen 80;
    server_name example.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

### 4. Monitor Everything

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

---

## Learn More

- [Docker Deployment](./docker.md) - Complete containerization guide
- [Uvicorn Documentation](https://www.uvicorn.org/) - ASGI server
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Environment configuration

---

## Next Steps

- [Docker Guide](./docker.md) - Containerize your application
- [Settings](../application/settings.md) - Configure your app
- [Security](../security/index.md) - Secure your deployment
