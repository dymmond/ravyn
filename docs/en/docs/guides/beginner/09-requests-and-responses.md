# Requests and Responses

In this section, you'll connect all core input/output pieces: path params, query params, body data, headers, cookies, file uploads, and response objects.

## Request data sources at a glance

```text
URL path      -> /items/{item_id}
Query string  -> ?limit=10
Headers       -> X-API-TOKEN: ...
Cookies       -> session=...
Body          -> JSON or form payload
Files         -> multipart/form-data
```

---

## Path + query in one handler

```python
from ravyn import Query, get


@get("/items/{item_id}")
def get_item(item_id: int, q: str = Query("")) -> dict:
    return {"item_id": item_id, "query": q}
```

---

## JSON request body with Pydantic

```python
from pydantic import BaseModel
from ravyn import post


class ItemIn(BaseModel):
    name: str
    price: float


@post("/items")
def create_item(data: ItemIn) -> dict:
    return {"name": data.name, "price": data.price}
```

---

## Headers and cookies

```python
from ravyn import Cookie, Header, get


@get("/session")
def read_session(
    token: str = Header(value="X-API-TOKEN"),
    session_id: str = Cookie(value="session"),
) -> dict:
    return {"token": token, "session": session_id}
```

---

## File uploads

```python
from ravyn import File, UploadFile, post


@post("/upload")
async def upload(file: UploadFile = File()) -> dict:
    return {"filename": file.filename, "content_type": file.content_type}
```

---

## Choosing a response style

### Return Python types directly

```python
from ravyn import get


@get("/simple")
def simple() -> dict:
    return {"message": "ok"}
```

### Return an explicit response object

```python
from ravyn import get
from ravyn.responses import JSONResponse


@get("/custom")
def custom() -> JSONResponse:
    return JSONResponse({"message": "created"}, status_code=201)
```

Use explicit response classes when you need fine-grained control (status, headers, media type).

---

## End-to-end request/response flow

```text
Incoming request
   -> parse inputs (path/query/body/header/cookie/file)
   -> validate types/models
   -> execute handler
   -> serialize output
   -> send response
```

---

## Related pages

- [Request and Response Models](./03-request-and-response-models.md)
- [A bit more about Routing](./10-routing.md)
- [Requests](../../requests.md)
- [Responses](../../responses.md)
- [Upload Files](../../extras/upload-files.md)

## What's Next?

Continue to [A bit more about Routing](./10-routing.md) to organize larger route trees cleanly.
