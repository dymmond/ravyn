# Handling Cookie Fields in Ravyn

Cookies are small pieces of data stored on the client's browser, commonly used for session management, user preferences, and tracking. Ravyn provides intuitive mechanisms to handle both incoming cookie data and to set cookies in responses.

## Accessing Cookie Parameters in Requests

Ravyn allows you to access cookies sent with incoming requests seamlessly by utilizing the `Cookie` class.

**Example: Accessing Cookies from Requests**

```python
from pydantic import BaseModel
from ravyn import Ravyn, Gateway, Cookie, JSONResponse, post

class User(BaseModel):
    name: str
    email: str

@post("/create")
async def create_user(
        data: User,
        ads_id: str | None = Cookie(value=None)
) -> JSONResponse:
    """
    Creates a user and retrieves the 'ads_id' cookie if present.
    """
    return JSONResponse({
        "message": "User created",
        "user": data.model_dump(),
        "ads_id": ads_id
    })

app = Ravyn(routes=[Gateway(handler=create_user)])
```

**Explanation:**

- The `ads_id` cookie is accessed using the `Cookie` class.
- If the `ads_id` cookie is not present in the request, its value defaults to `None`.
- The endpoint processes the user data and includes the `ads_id` in the response.

**Note:** Ravyn's `Cookie` class is designed for extracting cookie values from incoming requests.
To set cookies in responses, Ravyn provides a distinct `Cookie` data structure.

## Setting Cookies in Responses

To set cookies in HTTP responses, Ravyn offers a `Cookie` data structure that allows you to define
various cookie attributes such as `key`, `value`, `max_age`, and `httponly`.

**Example: Setting Cookies in Responses**

```python
from pydantic import BaseModel, EmailStr
from ravyn import Ravyn, Gateway, Response, post
from ravyn.core.datastructures import Cookie

class User(BaseModel):
    name: str
    email: EmailStr

@post(
    path="/create",
    response_cookies=[
        Cookie(
            key="csrf",
            value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
            max_age=3000,
            httponly=True,
        )
    ],
)
async def create_user(data: User) -> Response:
    """
    Creates a user and sets a CSRF token cookie in the response.
    """
    # Your logic to create the user
    return Response(content={"message": "User created"})

app = Ravyn(routes=[Gateway(handler=create_user)])
```

**Explanation:**

- The `response_cookies` parameter in the `@post` decorator is used to specify cookies to be included in the response.
- A `Cookie` is instantiated with attributes such as `key`, `value`, `max_age`, and `httponly`.
- When a response is returned from this endpoint, it will include the specified cookie.

**Caution:** Ravyn distinguishes between the `Cookie` used for request parameters and the `Cookie` used for response cookies. Ensure you import and use the appropriate `Cookie` class based on your context:

- For request cookies:
  ```python
  from ravyn import Cookie
  ```
- For response cookies:
  ```python
  from ravyn.datastructures import Cookie
  ```

## Combining Cookie Parameters with Other Request Data

Ravyn allows you to combine cookie parameters with other types of request data, such as JSON bodies or
form data, providing flexibility in handling various input formats.

**Example: Combining Cookies with JSON Body Data**

```python
from pydantic import BaseModel
from ravyn import Ravyn, Gateway, Cookie, JSONResponse, post

class User(BaseModel):
    name: str
    email: str

@post("/create")
async def create_user(
        data: User,
        ads_id: str | None = Cookie(value=None)
) -> JSONResponse:
    """
    Creates a user and retrieves the 'ads_id' cookie if present.
    """
    return JSONResponse({
        "message": "User created",
        "user": data.model_dump(),
        "ads_id": ads_id
    })

app = Ravyn(routes=[Gateway(handler=create_user)])
```

**Explanation:**

- The `ads_id` cookie is accessed alongside JSON body data parsed into the `User` model.
- This approach allows handling multiple data sources within a single endpoint function.

## Summary

- **Accessing Request Cookies:** Use Ravyn's `Cookie` class to extract cookie values from incoming requests.
- **Setting Response Cookies:** Utilize Ravyn's `Cookie` data structure to define and include cookies in HTTP responses.
- **Combining Data Sources:** Ravyn allows combining cookie parameters with other request data types, such as JSON bodies, within endpoint functions.

By leveraging Ravyn's cookie handling capabilities, you can effectively manage session data, user preferences, and other stateful information in your web applications.
