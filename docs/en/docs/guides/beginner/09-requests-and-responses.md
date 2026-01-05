# Requests and Responses

In this section, you'll learn how to handle input and output data using request and response models in Ravyn.

---

## Using Pydantic Models for Requests

Ravyn uses Pydantic to define and validate incoming request bodies:

```python
from pydantic import BaseModel
from ravyn import post

class Item(BaseModel):
    name: str
    price: float

@post("/items")
def create_item(data: Item) -> dict:
    return {"name": data.name, "price": data.price}
```

Sending invalid data returns:

```json
{
  "detail": [
    {
      "loc": ["body", "price"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Query Parameters and Path Parameters

You can use type annotations to declare query and path parameters:

```python
from ravyn import get

@get("/items/{item_id}")
def get_item(item_id: int, q: str = "") -> dict:
    return {"item_id": item_id, "query": q}
```

---

## Response Models

You can also define a response model:

```python
class ResponseModel(BaseModel):
    name: str
    price: float

@post("/items")
def create_item(data: Item) -> ResponseModel:
    return ResponseModel(name=data.name, price=data.price)
```

---

## Custom JSONResponse

You can return your own response:

```python
from ravyn.responses import JSONResponse

@get("/custom")
def custom() -> JSONResponse:
    return JSONResponse({"message": "Custom"}, status_code=201)
```

---

## Extra: Headers, Cookies, Files

You can also extract headers, cookies, and file uploads via parameters:

```python
from ravyn import Header, Cookie, UploadFile, post, File

@post("/upload")
async def upload(
        file: UploadFile = File(),
        token: str = Header(value="X-API-TOKEN"),
        session: str = Cookie(value="session")
):
    return {"filename": file.filename, "token": token, "session": session}
```

---

## What's Next?

You've now learned how to use request and response models with validation.

👉 Continue to [routing](./10-routing.md) to organize routes and build modular applications.
