# Docker Deployment

Imagine packing for a trip. Instead of hoping your destination has everything you need, you pack your own suitcase with clothes, toiletries, and essentials. Docker works the same way. It packages your application with everything it needs to run, ensuring it works identically everywhere.

No more "it works on my machine" problems!

## What You'll Learn

- What Docker is and why use it
- Creating a Dockerfile for Ravyn
- Docker Compose for multi-container setups
- Production-ready Docker configuration
- Nginx + Supervisor setup
- Testing and deploying your container

## Quick Start

### Simple Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run

```shell
# Build the image
docker build -t myapp .

# Run the container
docker run -d -p 8000:8000 myapp

# Visit http://localhost:8000
```

---

## What is Docker?

> Docker is a platform that uses OS-level virtualization to deliver software in packages called containers.

**In simple terms:** Docker creates isolated environments (containers) that include your code and all its dependencies, ensuring your app runs the same way everywhere.

### Why Docker?

**Traditional Deployment Problems:**
- "Works on my machine" syndrome
- Different environments have different dependencies
- Manual setup on each server
- Difficult to reproduce issues

**Docker Solutions:**
- Consistent environment everywhere
- All dependencies packaged together
- Easy to scale and replicate
- Simplified deployment process

---

## Basic Dockerfile

### Minimal Setup

```dockerfile
# Start from official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### With Multiple Workers

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Run with 4 workers for better performance
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## Production-Ready Setup

For production, use Nginx as a reverse proxy and Supervisor to manage processes.

### Project Structure

```
.
├── app/
│   ├── __init__.py
│   └── main.py
├── deployment/
│   ├── nginx.conf
│   └── supervisor.conf
├── Dockerfile
└── requirements.txt
```

### Requirements

```txt
ravyn
uvicorn
nginx
supervisor
```

### Application

```python
# app/main.py
{!> ../../../docs_src/deployment/app.py !}
```

### Nginx Configuration

Nginx acts as a reverse proxy, handling SSL, static files, and load balancing:

```nginx
{!> ../../../docs_src/deployment/nginx.conf !}
```

**What this does:**
- Listens on port 80
- Proxies requests to Uvicorn (port 8000)
- Adds security headers
- Handles timeouts

### Supervisor Configuration

Supervisor manages and monitors your processes:

```ini
{!> ../../../docs_src/deployment/supervisor.conf !}
```

**What this does:**
1. Configures Supervisor daemon
2. Manages Nginx process
3. Manages Uvicorn process
4. Auto-restarts on failure

### Production Dockerfile

```dockerfile
# Start from Python base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        nginx supervisor nginx-extras && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app/app

# Copy configuration files
COPY deployment/nginx.conf /etc/nginx/
COPY deployment/nginx.conf /etc/nginx/sites-enabled/default
COPY deployment/supervisor.conf /etc/supervisor/conf.d/

# Expose port
EXPOSE 80

# Start Supervisor (which starts Nginx and Uvicorn)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
```

**Dockerfile explained:**

1. **Base image** - Start with Python 3.11
2. **System packages** - Install Nginx and Supervisor
3. **Working directory** - Set to `/app`
4. **Dependencies** - Install Python packages
5. **Application** - Copy your code
6. **Configuration** - Copy Nginx and Supervisor configs
7. **Start** - Run Supervisor (manages everything)

---

## Docker Compose

For multi-container setups (app + database):

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

```shell
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

---

## Building and Testing

### Build the Image

```shell
docker build -t myapp:latest .
```

### Test Locally

```shell
# Run the container
docker run -d --name myapp-container -p 80:80 myapp:latest

# Check if it's running
docker ps

# View logs
docker logs myapp-container

# Stop the container
docker stop myapp-container

# Remove the container
docker rm myapp-container
```

### Verify Endpoints

Test your application:

- [http://localhost/](http://localhost/)
- [http://localhost/users/5?q=test](http://localhost/users/5?q=test)

### OpenAPI Documentation

Access API docs (if enabled):

- [http://localhost/docs/swagger](http://localhost/docs/swagger)
- [http://localhost/docs/redoc](http://localhost/docs/redoc)
- [http://localhost/docs/elements](http://localhost/docs/elements)

---

## Disabling OpenAPI in Production

By default, OpenAPI docs are enabled. Disable them in production:

### Via Code

```python
{!> ../../../docs_src/deployment/flag.py !}
```

### Via Settings

```python
{!> ../../../docs_src/deployment/settings.py !}
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Large Image Size

**Problem:** Docker image is too large.

**Solution:** Use multi-stage builds:

```dockerfile
# Build stage
FROM python:3.11 as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### Pitfall 2: Not Using .dockerignore

**Problem:** Copying unnecessary files.

**Solution:** Create `.dockerignore`:

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.git
.gitignore
.env
*.log
```

### Pitfall 3: Running as Root

**Problem:** Security risk.

**Solution:** Create a non-root user:

```dockerfile
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Switch to non-root user
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

---

## Best Practices

### 1. Use Specific Image Tags

```dockerfile
# Good - specific version
FROM python:3.11.5-slim

# Avoid - can change unexpectedly
FROM python:latest
```

### 2. Leverage Build Cache

```dockerfile
# Copy requirements first (changes less often)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code last (changes more often)
COPY . .
```

### 3. Use Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1
```

### 4. Set Resource Limits

```shell
docker run -d \
  --memory="512m" \
  --cpus="1.0" \
  -p 8000:8000 \
  myapp
```

---

## Deployment to Cloud

### Docker Hub

```shell
# Tag your image
docker tag myapp:latest username/myapp:latest

# Push to Docker Hub
docker push username/myapp:latest
```

### AWS ECR

```shell
# Authenticate
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag myapp:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:latest
```

---

## Learn More

- [Docker Documentation](https://docs.docker.com/) - Official Docker docs
- [Docker Compose](https://docs.docker.com/compose/) - Multi-container apps
- [Uvicorn](https://www.uvicorn.org/) - ASGI server
- [Nginx](https://nginx.org/en/docs/) - Web server

---

## Next Steps

- [Deployment Introduction](./intro.md) - Deployment concepts
- [Settings](../application/settings.md) - Configure your app
- [Security](../security/index.md) - Secure your deployment
