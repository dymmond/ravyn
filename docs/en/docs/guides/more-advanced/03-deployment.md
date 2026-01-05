# Deployment

This section covers how to deploy your Ravyn application in a production-ready environment.

Ravyn apps are ASGI applications, which means they can be served using any ASGI-compatible server like `uvicorn`,
`hypercorn`, or `daphne`.

---

## Using Uvicorn

One way to run Ravyn in production is with `uvicorn`, an ASGI server:

### Install:

```bash
pip install uvicorn
```

### Run your app:

```bash
uvicorn myapp:app --host 0.0.0.0 --port 8000 --workers 4 --lifespan on
```

Options:

- `--workers`: Number of worker processes.
- `--lifespan on`: Ensures startup and shutdown events are handled.
- `--reload`: (Only for development) enables auto-reload on file changes.

---

## Using Gunicorn + Uvicorn Workers

For more robust setups (especially when using Docker), run Uvicorn inside Gunicorn:

```bash
pip install gunicorn uvicorn
```

```bash
gunicorn myapp:app \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 \
  --workers 4
```

This setup provides better process management, logging, and signal handling in production environments.

---

## Docker Deployment

Here's a simple Dockerfile for Ravyn:

```Dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["uvicorn", "myapp:app", "--host", "0.0.0.0", "--port", "8000"]
```

Then build and run:

```bash
docker build -t my-ravyn-app .
docker run -p 8000:8000 my-ravyn-app
```

---

## Behind a Reverse Proxy (e.g. Nginx)

In production, it’s common to put Ravyn behind a reverse proxy like Nginx:

### Example Nginx config:

```nginx
server {
    listen 80;
    server_name myapp.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Use SSL termination with Certbot + Let's Encrypt for HTTPS.

---

## Environment Variables

Use environment variables and `.env` files to manage secrets, database connections, etc. Ravyn supports loading
`.env` via Pydantic or your custom configuration setup.

---

## Deployment Checklist

- [x] Run behind a secure reverse proxy (e.g., Nginx)
- [x] Use process managers (e.g., Gunicorn, systemd, Docker)
- [x] Set `debug=False` in production
- [x] Handle startup/shutdown events properly
- [x] Monitor logs and health checks
- [x] Secure secrets via environment variables

---

## What's Next?

Your app is ready for the real world. Next step?

👉 Continue to [scaling](./04-scaling.md) to explore strategies for performance, load balancing, and horizontal scaling.
