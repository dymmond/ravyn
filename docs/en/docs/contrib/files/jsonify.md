# `jsonify`

The `jsonify` helper in Ravyn makes it simple to return JSON responses from your endpoints,
similar to Flask’s `jsonify`.

It automatically encodes Python objects into JSON, sets the correct `Content-Type`,
and allows you to customize status codes, headers, and cookies.

---

## When to Use `jsonify`

Use `jsonify` when you want to:

* Return JSON from your endpoints without manually creating a `Response`.
* Pass dicts, lists, or keyword arguments directly.
* Control status codes, headers, or cookies in a JSON response.
* Make migration from Flask smoother.

---

## Basic Example

```python
from ravyn import Ravyn, Gateway, get
from ravyn.contrib.responses.json import jsonify

@get()
async def hello():
    return jsonify(message="Hello, World!", status="ok")

app = Ravyn(routes=[
    Gateway("/hello", hello)
])
```

Request:

```bash
curl http://localhost:8000/hello
```

Response:

```json
{"message": "Hello, World!", "status": "ok"}
```

---

## Returning Lists

If you pass a list or multiple arguments, they will be returned as JSON arrays:

```python
@get()
async def numbers():
    return jsonify([1, 2, 3])

@get()
async def multi():
    return jsonify(1, 2, 3)
```

* `/numbers` → `[1, 2, 3]`
* `/multi` → `[1, 2, 3]`

---

## Custom Status Codes

You can return custom HTTP status codes:

```python
@get()
async def created_user():
    return jsonify(id=1, name="Alice", status="created", status_code=200)
```

Response:

* Status → `200 Success`
* Body → `{"id": 1, "name": "Alice", "status": "created"}`

---

## Adding Headers

Custom headers can be added easily:

```python
@get()
async def with_headers():
    return jsonify(
        message="Hello",
        headers={"X-App-Version": "1.0"}
    )
```

Response will include:

```
X-App-Version: 1.0
```

---

## Adding Cookies

You can also set cookies directly:

```python
@get()
async def with_cookie():
    return jsonify(
        message="Hello",
        cookies={"session": "abc123"}
    )
```

Response will include:

```
Set-Cookie: session=abc123; Path=/
```

---

## Error Handling

It’s not allowed to mix both positional arguments and keyword arguments:

```python
# This raises TypeError
return jsonify({"a": 1}, b=2)
```

---

## API Reference

```python
jsonify(
    *args: Any,
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    **kwargs: Any,
) -> Response
```

### Parameters

* **`*args`** – A single dict, list, or multiple values (converted to a list).
* **`status_code`** – Custom HTTP status code (default: 200).
* **`headers`** – Optional dictionary of response headers.
* **`cookies`** – Optional dictionary of cookies to set.
* **`**kwargs`** – Treated as a dict payload if no `*args` provided.

with `jsonify`, Ravyn makes returning JSON **fast, safe, and friendly**, while adding async-native power.
