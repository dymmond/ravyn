# Deployment

Think of deployment as moving day for your application. You've built something amazing on your local machine, but now it needs to live somewhere everyone can access it 24/7. Just like moving to a new home, you need to pack everything carefully, choose the right location, and set up all the utilities.

Ravyn makes deployment straightforward. It's a standard ASGI application that works with any modern deployment platform.

## What You'll Learn

- Deployment concepts and strategies
- Docker containerization for Ravyn apps
- Production best practices
- Environment configuration
- Choosing the right deployment platform

## Quick Start

The fastest way to deploy is using Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```shell
# Build and run
docker build -t myapp .
docker run -d -p 8000:8000 myapp
```

---

## Deployment Options

Ravyn is a standard ASGI application, giving you flexibility in how you deploy:

### Containerized Deployment

**Docker** - Package your app with all dependencies

- Consistent across environments
- Easy to scale
- Works everywhere
- [Docker Guide →](./docker.md)

### Cloud Platforms

**Managed Services** - Let the platform handle infrastructure

- **AWS** - Elastic Beanstalk, ECS, Lambda
- **Azure** - App Service, Container Instances
- **GCP** - Cloud Run, App Engine
- **Render** - Simple, affordable deployment
- **Heroku** - Quick deployment with git push

### Traditional Servers

**VPS/Dedicated** - Full control over your infrastructure

- **Nginx + Gunicorn** - Classic production setup
- **Caddy** - Modern web server with automatic HTTPS
- **Apache** - Traditional web server

### Serverless

**Function-as-a-Service** - Pay per request

- **AWS Lambda** - Serverless functions
- **Google Cloud Functions** - Event-driven functions
- **Azure Functions** - Serverless compute

---

## Deployment Checklist

Before deploying to production:

### Security

- Use HTTPS (SSL/TLS certificates)
- Set secure secret keys
- Configure CORS properly
- Enable CSRF protection
- Use environment variables for secrets
- Disable debug mode

### Performance

- Use a production ASGI server (Uvicorn, Hypercorn)
- Configure worker processes
- Set up caching
- Optimize database queries
- Enable gzip compression

### Reliability

- Set up health checks
- Configure logging
- Implement error tracking (Sentry)
- Set up monitoring (Datadog, New Relic)
- Plan for backups
- Test failover scenarios

### Documentation

- Disable OpenAPI docs in production (optional)
- Document deployment process
- Create runbooks for common issues

---

## Environment Configuration

Use environment variables for configuration:

```python
# settings.py
import os
from ravyn import RavynSettings

class ProductionSettings(RavynSettings):
    debug: bool = False
    secret_key: str = os.getenv("SECRET_KEY")
    database_url: str = os.getenv("DATABASE_URL")
    allowed_hosts: list[str] = ["example.com", "www.example.com"]
    
    # Disable docs in production
    enable_openapi: bool = False
```

```shell
# Set environment variables
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="postgresql://user:pass@localhost/db"
export RAVYN_SETTINGS_MODULE="myapp.settings.ProductionSettings"
```

---

## Best Practices

### 1. Use a Process Manager

```shell
# Uvicorn with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2. Set Up a Reverse Proxy

Use Nginx or Caddy in front of your ASGI server:

```nginx
server {
    listen 80;
    server_name example.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Use Docker for Consistency

Docker ensures your app runs the same everywhere:

```dockerfile
FROM python:3.11-slim

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run with multiple workers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 4. Monitor Your Application

Set up logging and monitoring:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Running in Debug Mode

**Problem:** Debug mode enabled in production.

```python
# Wrong - exposes sensitive information
app = Ravyn(debug=True)
```

**Solution:** Always disable debug in production:

```python
# Correct
app = Ravyn(debug=False)
```

### Pitfall 2: Hardcoded Secrets

**Problem:** Secrets in code.

```python
# Wrong - secrets in code
SECRET_KEY = "my-secret-key"
```

**Solution:** Use environment variables:

```python
# Correct
import os
SECRET_KEY = os.getenv("SECRET_KEY")
```

### Pitfall 3: Single Worker Process

**Problem:** Running with only one worker.

**Solution:** Use multiple workers for better performance:

```shell
# Good - multiple workers
uvicorn app.main:app --workers 4
```

---

## Learn More

- [Docker Deployment](./docker.md) - Complete Docker guide
- [Introduction](./intro.md) - Deployment concepts
- [Uvicorn Documentation](https://www.uvicorn.org/) - ASGI server
- [Docker Documentation](https://docs.docker.com/) - Container platform

---

## Next Steps

- **New to deployment?** Read the [Introduction](./intro.md)
- **Ready to deploy?** Follow the [Docker Guide](./docker.md)
- **Need help?** Check [Common Issues](./intro.md#troubleshooting)
