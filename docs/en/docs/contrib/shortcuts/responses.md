# Responses

Ravyn provides several lightweight response helpers under
`ravyn.contrib.responses.shortcuts` to make endpoint development faster and cleaner.

These shortcuts let you quickly send JSON, streaming, or empty responses
without explicitly importing or instantiating `Response` classes.

### `send_json()`

```python
from ravyn.contrib.responses.shortcuts import send_json
```

#### Description

Returns a `JSONResponse` object directly, allowing you to respond with structured data
in one line.

#### Example

```python
from ravyn import JSONResponse, get
from ravyn.contrib.responses.shortcuts import send_json

@get()
async def get_user() -> JSONResponse:
    user = {"id": 1, "name": "Alice"}
    return send_json(user)
```

#### Parameters

| Name          | Type            | Description                        |                                   |
| ------------- | --------------- | ---------------------------------- | --------------------------------- |
| `data`        | `dict           | list`                              | The JSON-serializable payload.    |
| `status_code` | `int`           | HTTP status code (default: `200`). |                                   |
| `headers`     | `dict[str, str] | None`                              | Optional HTTP headers to include. |

#### Behavior

- Serializes `data` into JSON.
- Automatically sets `Content-Type: application/json`.
- Returns a ready-to-send `JSONResponse` instance.

#### Returns

`JSONResponse`: the response containing the serialized JSON payload.

### `json_error()`

```python
from ravyn.contrib.responses.shortcuts import json_error
```

#### Description

Returns a structured JSON error payload without raising an exception.
This is ideal for explicit, graceful error responses inside your logic
(whereas `abort()` should be used to immediately stop request processing).

#### Example

```python
from ravyn import JSONResponse, Request, get
from ravyn.contrib.responses.shortcuts import json_error

@get()
async def validate_user(request: Request) -> JSONResponse:
    data = await request.json()
    if "email" not in data:
        return json_error("Missing email field", status_code=422)
```

#### Parameters

| Name          | Type            | Description                        |                                         |
| ------------- | --------------- | ---------------------------------- | --------------------------------------- |
| `message`     | `str            | dict`                              | The error message or full JSON payload. |
| `status_code` | `int`           | HTTP status code (default: `400`). |                                         |
| `headers`     | `dict[str, str] | None`                              | Optional custom headers.                |

#### Behavior

* If `message` is a string, wraps it as `{"error": message}`.
* If `message` is a dict, uses it directly.
* Produces a `JSONResponse` without interrupting execution.

#### Returns

`JSONResponse`: the structured error payload.

### `stream()`

```python
from ravyn.contrib.responses.shortcuts import stream
```

#### Description

Creates a `StreamingResponse` from any iterable or async generator.
Useful for large or continuous data streams such as logs, progress updates,
or server-sent events.

#### Example – Async Generator

```python
from ravyn import get
from ravyn.responses import StreamingResponse
from ravyn.contrib.responses.shortcuts import stream

import anyio

@get()
async def numbers() -> StreamingResponse:
    async def generator():
        for i in range(5):
            yield f"Number: {i}\\n"
            await anyio.sleep(1)

    return stream(generator(), mimetype="text/plain")
```

#### Example – Sync Generator

```python
from ravyn import get
from ravyn.responses import StreamingResponse
from ravyn.contrib.responses.shortcuts import stream

@get()
def stream_lines() -> StreamingResponse:
    def generate():
        for i in range(3):
            yield f"Line {i}\\n"
    return stream(generate())
```

#### Parameters

| Name       | Type            | Description                                           |                   |
| ---------- | --------------- | ----------------------------------------------------- | ----------------- |
| `content`  | `Any`           | Iterable or async iterable yielding `bytes` or `str`. |                   |
| `mimetype` | `str`           | MIME type of the stream (default: `"text/plain"`).    |                   |
| `headers`  | `dict[str, str] | None`                                                 | Optional headers. |

#### Behavior

- Works with both sync and async generators.
- Sends incremental chunks as they are yielded.
- Uses AnyIO to support `asyncio` and `trio` transparently.

#### Returns

`StreamingResponse`: the active streaming response.

### `empty()`

```python
from ravyn.contrib.responses.shortcuts import empty
```

#### Description

Returns an empty `Response` object, typically for actions that don’t need to return content
(such as `DELETE`, `PUT`, or successful `POST` endpoints that redirect elsewhere).

#### Example

```python
from ravyn import Response, delete
from ravyn.contrib.responses.shortcuts import empty

@delete()
async def delete_user() -> Response:
    # Perform deletion...
    return empty()  # 204 No Content
```

#### Parameters

| Name          | Type            | Description                        |                   |
| ------------- | --------------- | ---------------------------------- | ----------------- |
| `status_code` | `int`           | HTTP status code (default: `204`). |                   |
| `headers`     | `dict[str, str] | None`                              | Optional headers. |

#### Behavior

- Creates a minimal response with no body.
- Sets `Content-Length: 0` automatically.

#### Returns

`Response`: an empty HTTP response.

### `redirect()`

```python
from ravyn.contrib.responses.shortcuts import redirect
```

#### Description

Creates a `RedirectResponse` that instructs the client to load a different URL.
Ideal for POST-redirect-GET patterns, login flows, or temporary route changes.

#### Example

```python
from ravyn.responses import RedirectResponse, get
from ravyn.contrib.responses.shortcuts import redirect

@get()
async def login_success() -> RedirectResponse:
    return redirect("/dashboard")
```

#### Parameters

| Name          | Type                                 | Description                                                 |
| ------------- | ------------------------------------ | ----------------------------------------------------------- |
| `url`         | `str` | `URL`                        | The target URL to redirect to.                              |
| `status_code` | `int`                                | Redirect status code (default: `307`).                      |
| `headers`     | `Mapping[str, str]` | `None`         | Optional extra headers.                                     |
| `background`  | `Task` | `None`                      | Optional background task to execute alongside the response. |
| `encoders`    | `Sequence[Encoder \| type[Encoder]]` | Optional sequence of encoders for response serialization.   |

#### Behavior

* Returns a standard HTTP redirect.
* Sets `Location` header to the target URL automatically.
* Supports background tasks and custom encoders.

#### Returns

`RedirectResponse`: a response object that redirects to the given URL.

### `unauthorized()`

```python
from ravyn.contrib.responses.shortcuts import unauthorized
```

#### Description

Returns a `401 Unauthorized` JSON response, typically used when authentication
credentials are missing or invalid.

#### Example

```python
from ravyn import JSONResponse, Request, get
from ravyn.contrib.responses.shortcuts import unauthorized

@get()
async def protected_route(request: Request) -> JSONResponse:
    token = request.headers.get("Authorization")
    if not token:
        return unauthorized("Authentication token required")
```

#### Parameters

| Name      | Type            | Description                                           |                        |
| --------- | --------------- | ----------------------------------------------------- | ---------------------- |
| `message` | `str`           | Error message to include (default: `"Unauthorized"`). |                        |
| `headers` | `dict[str, str] | None`                                                 | Optional HTTP headers. |

#### Behavior

* Returns a JSON payload in the form `{"error": message}`.
* Sets HTTP status code to `401`.
* Does **not** raise an exception — it simply returns a `JSONResponse`.

#### Returns

`JSONResponse`: the 401 response containing the structured error payload.

### `forbidden()`

```python
from ravyn.contrib.responses.shortcuts import forbidden
```

#### Description

Returns a `403 Forbidden` JSON response, typically used when a user is authenticated
but not authorized to perform the requested action.

#### Example

```python
from ravyn import JSONResponse, Request, get
from ravyn.contrib.responses.shortcuts import forbidden

@get()
async def admin_dashboard(request: Request) -> JSONResponse:
    if not request.user.is_admin:
        return forbidden("You do not have permission to access this page.")
```

#### Parameters

| Name      | Type            | Description                             |                        |
| --------- | --------------- | --------------------------------------- | ---------------------- |
| `message` | `str`           | Error message (default: `"Forbidden"`). |                        |
| `headers` | `dict[str, str] | None`                                   | Optional HTTP headers. |

#### Behavior

* Returns a JSON response like `{"error": message}`.
* Sets HTTP status code to `403`.
* Meant for permission-denied scenarios.

#### Returns

`JSONResponse`: the 403 response containing the structured error payload.

### `not_found()`

```python
from ravyn.contrib.responses.shortcuts import not_found
```

#### Description

Returns a `404 Not Found` JSON response, used when a requested resource
cannot be located.

#### Example

```python
from ravyn import JSONResponse, get
from ravyn.contrib.responses.shortcuts import not_found

@get()
async def get_user() -> JSONResponse:
    user = await db.users.get(id=42)
    if not user:
        return not_found("User not found")
```

#### Parameters

| Name      | Type            | Description                             |                        |
| --------- | --------------- | --------------------------------------- | ---------------------- |
| `message` | `str`           | Error message (default: `"Not Found"`). |                        |
| `headers` | `dict[str, str] | None`                                   | Optional HTTP headers. |

#### Behavior

* Returns a structured JSON payload like `{"error": message}`.
* Sets HTTP status code to `404`.
* Commonly used in RESTful APIs for missing resources.

#### Returns

`JSONResponse`: the 404 response with the given error message.

### When to Use These Shortcuts

| Use Case                            | Shortcut       |
| ----------------------------------- | -------------- |
| Returning structured data           | `send_json()`  |
| Returning an error payload          | `json_error()` |
| Sending live or large output        | `stream()`     |
| Returning no content (e.g., DELETE) | `empty()`      |
| Redirecting to another URL          | `redirect()`   |
| Missing authentication credentials  | `unauthorized()` |
| Authenticated but lacks permission  | `forbidden()`    |
| Requested resource not found        | `not_found()`    |

### Comparison with [`abort()`](./abort.md)

| Shortcut       | Purpose                                                    | Raises Exception? |
| -------------- | ---------------------------------------------------------- | ----------------- |
| `abort()`      | Immediately stops execution with an `HTTPException`.       | Yes             |
| `json_error()` | Returns an error payload explicitly (execution continues). | No              |
| `send_json()`  | Normal JSON response for successful operations.            | No              |
| `stream()`     | Streams chunks of data incrementally.                      | No              |
| `empty()`      | Indicates success with no body.                            | No              |
| `redirect()`   | Redirects the client to a different URL.                   | No              |
| `unauthorized()` | Returns a `401 Unauthorized` JSON error payload.           | No              |
| `forbidden()`    | Returns a `403 Forbidden` JSON error payload.              | No              |
| `not_found()`    | Returns a `404 Not Found` JSON error payload.              | No              |
