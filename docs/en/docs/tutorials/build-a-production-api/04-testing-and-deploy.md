# Step 4: Testing and Deployment

Validate behavior with tests and package the app for production.

## Add a basic integration test

```python
from ravyn.testclient import RavynTestClient
from app.main import app


def test_list_users():
    client = RavynTestClient(app=app)
    response = client.get("/users/")
    assert response.status_code == 200
```

## Run tests

```shell
hatch run test:test
```

## Add a production Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

CMD ["palfrey", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## Validate container locally

```shell
docker build -t myapp .
docker run --rm -p 8000:8000 myapp
```

## Completion checklist

- tests pass
- docs load (`/docs/swagger`)
- container starts with production server settings

## Continue

- [Deployment](../../deployment/index.md)
- [Workflows](../../workflows/index.md)
