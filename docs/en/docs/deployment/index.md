# Deployment

Deploy your Ravyn application to production with confidence.

## In This Section

- [Introduction](./intro.md) - Deployment concepts and strategies
- [Docker Deployment](./docker.md) - Containerized deployment guide

## Quick Links

### Getting Started

- [What is deployment?](./intro.md#what-is-deployment)
- [Deployment strategies](./intro.md#strategies)
- [Docker example](./docker.md#quick-start)

### Common Deployments

- [Docker + Nginx](./docker.md#ravyn-and-docker-example)
- [Cloud platforms](./intro.md#cloud-deployment)
- [Environment variables](./intro.md#environment-configuration)

---

## Deployment Overview

Deploying a Ravyn application is straightforward since it's a standard ASGI application. You have many options:

- **Docker** - Containerized deployment

- **Cloud Platforms** - AWS, Azure, GCP, Render, Heroku

- **Traditional Servers** - VPS with Nginx/Gunicorn

- **Serverless** - AWS Lambda, Google Cloud Functions

---

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

See the [Docker guide](./docker.md) for complete examples.

---

## Choose Your Path

- **New to deployment?** Start with [Introduction](./intro.md)
- **Ready to deploy?** Jump to [Docker guide](./docker.md)
- **Production checklist?** See [Best practices](./intro.md#best-practices)
