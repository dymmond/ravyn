# Query Parameters

Query parameters in Ravyn allow you to pass dynamic values through the URL's query string, enabling flexible
and customizable API endpoints. This advanced guide provides a comprehensive overview of handling query
parameters in Ravyn, including their declaration, default values, optional parameters,
and the interplay between query and path parameters.

## What Are Query Parameters?

Query parameters are key-value pairs appended to the URL after a `?`, separated by `&`.
They are commonly used for filtering, pagination, or passing additional data to endpoints.

In Ravyn, these parameters are automatically recognized and injected into your handler functions.

**Example:**

```python
from ravyn import Ravyn, Gateway, JSONResponse, get

fake_users = [{"last_name": "Doe", "email": "john.doe@example.com"}]

@get("/users")
async def read_users(skip: int = 1, limit: int = 5) -> JSONResponse:
    return JSONResponse(fake_users[skip: skip + limit])

app = Ravyn(routes=[Gateway(handler=read_users)])
```

**Explanation:**

- The `read_users` function accepts two query parameters: `skip` and `limit`, both with default values.
- Accessing `http://127.0.0.1/users?skip=1&limit=5` would call `read_users` with `skip=1` and `limit=5`.
- Ravyn automatically parses these parameters from the URL and passes them to the function.

## Declaring Default and Optional Parameters

In Ravyn, query parameters can have default values, making them optional in requests. You can declare them
using standard Python syntax.

**Example:**

```python
from ravyn import Ravyn, Gateway, JSONResponse, get

@get("/items")
async def read_items(category: str = "all", page: int = 1) -> JSONResponse:
    return JSONResponse({"category": category, "page": page})

app = Ravyn(routes=[Gateway(handler=read_items)])
```

**Explanation:**

- `category` and `page` have default values of `"all"` and `1`, respectively.
- A request to `/items` without query parameters will use these default values.
- Providing `/items?category=books&page=2` will override the defaults with `category="books"` and `page=2`.

### Optional Parameters

To make a query parameter optional without a default value, you can use `Optional` from Python's `typing` module.

**Example:**

```python
from typing import Optional
from ravyn import Ravyn, Gateway, JSONResponse, get

@get("/search")
async def search_items(query: Optional[str] = None) -> JSONResponse:
    if query:
        # Perform search with query
        results = {"results": f"Results for {query}"}
    else:
        # Return default results
        results = {"results": "Default results"}
    return JSONResponse(results)

app = Ravyn(routes=[Gateway(handler=search_items)])
```

**Explanation:**

- The `query` parameter is optional.
- If `query` is provided in the URL (e.g., `/search?query=python`), it will be used in the function.
- If not provided, the function will execute the else block, returning default results.

## Combining Query and Path Parameters

Ravyn allows the combination of path and query parameters in a single endpoint.
It's important to ensure that parameter names are unique to avoid conflicts.

**Example:**

```python
from ravyn import Ravyn, Gateway, JSONResponse, get

@get("/users/{user_id}")
async def get_user(user_id: int, detailed: bool = False) -> JSONResponse:
    user = {"user_id": user_id, "name": "John Doe"}
    if detailed:
        user.update({"email": "john.doe@example.com", "address": "123 Main St"})
    return JSONResponse(user)

app = Ravyn(routes=[Gateway(handler=get_user)])
```

**Explanation:**

- `user_id` is a path parameter, directly part of the URL path.
- `detailed` is a query parameter, appended to the URL as a key-value pair.
- Accessing `/users/1?detailed=true` sets `user_id=1` and `detailed=True`.

**Important Note:** Avoid using the same name for path and query parameters to prevent conflicts and
unexpected behavior.

## Required Query Parameters

To enforce that a query parameter is required, omit the default value in the function signature.
Ravyn will raise a validation error if the parameter is missing in the request.

**Example:**

```python
from ravyn import Ravyn, Gateway, JSONResponse, get

@get("/reports")
async def generate_report(date: str) -> JSONResponse:
    return JSONResponse({"report_date": date})

app = Ravyn(routes=[Gateway(handler=generate_report)])
```

**Explanation:**

- The `date` parameter is required.
- A request to `/reports?date=2023-04-01` will succeed.
- A request to `/reports` without the `date` parameter will result in a validation error.

By understanding and utilizing query parameters effectively, you can create flexible and robust API endpoints in
Ravyn that cater to a wide range of client requirements.
