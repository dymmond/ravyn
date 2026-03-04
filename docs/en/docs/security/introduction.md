# First Introduction

Let's imagine that you have your backend API in some domain.

And you have a frontend in another domain or in a different path of the same domain (or in a mobile application).

And you want to have a way for the frontend to authenticate with the backend, using a username and password.

We can use OAuth2 to build that with **Ravyn**.

But let's save you the time of reading the full long specification just to find those little pieces of information you need.

Let's use the tools provided by **Ravyn** to handle security.

## Let us dig in

We will be doing and explaining at the same time what is what.

## Create an `app.py`

You can copy the following code into an `app.py` or any file at your choice.

```python
{!> ../../../docs_src/security/app.py !}
```

## Run it

You can now run the file using, for example, `palfrey` and it can be like this:

```shell
$ palfrey app:app
```

## Verify it

To check if the endpoint is properly configured and working, you can access the OpenAPI documentation at
[http://127.0.0.1:8000/docs/swagger](http://127.0.0.1:8000/docs/swagger).

You should be able to see something like this:

<img src="https://res.cloudinary.com/dymmond/image/upload/v1732010613/esmerald/security/txef6swlznhtjkshevfr.png"/>

!!! Tip
    As you can see, you already have a brand new shiny **Authorize** button at the top of the page.
    The same is applied to the path operation that contains a lock icon as well.

If you click the **Authorize** button, you will be able to see the type of login to type a `username`, `password` and
other fields as well.

Lets check and click it!

<img src="https://res.cloudinary.com/dymmond/image/upload/v1732011171/esmerald/security/autorize_wqh6lu.png" />

!!! Note
    Typing anything in the form won't make it work, yet. Step by step we will get there, no worries.

This isn't the frontend interface intended for end users. Instead, it serves as a powerful, interactive tool for documenting your API.

It’s useful for the frontend team (which might also be you), for third-party applications and systems, and even for your own use.
You can rely on it to debug, review, and test your application efficiently.

## The `password` flow

Now, let’s take a step back and clarify what this all means.

The `password` "flow" is one of the methods (or "flows") defined in OAuth2 for managing security and authentication.

OAuth2 was originally designed to separate the backend or API from the server responsible for user authentication.

However, in this scenario, the same Ravyn application will handle both the API and the authentication process.

Let’s examine it from this simplified perspective:

Here’s how the password "flow" works step by step:

1. **User Login**: The user enters their `username` and `password` in the frontend and submits the form by hitting `Enter`.

2. **Frontend Request**: The frontend (running in the user’s browser) sends the `username` and `password` to a specific URL on the API, typically defined with `tokenUrl="token"`.

3. **API Validation**:
   - The API verifies the provided `username` and `password`.
   - If valid, it responds with a "token."
     - A **token** is essentially a string containing information that can later be used to authenticate the user.
     - Tokens usually have an expiration time:
       - After expiration, the user must log in again.
       - This limits the risk if the token is stolen since it won’t work indefinitely (in most cases).

4. **Token Storage**: The frontend temporarily stores the token securely.

5. **Navigating the App**: When the user navigates to another section of the web app, the frontend may need to fetch additional data from the API.

6. **Authenticated API Requests**:
   - To access protected endpoints, the frontend includes an `Authorization` header in its request.
   - The header’s value is `Bearer ` followed by the token.
   - For example, if the token is `foobar`, the `Authorization` header would look like this:

     ```plaintext
     Authorization: Bearer foobar
     ```

## **Ravyn** `OAuth2PasswordBearer`

**Ravyn** offers various tools, at different levels of abstraction, to implement security features.

In this example, we’ll use **OAuth2** with the **Password** flow, utilizing a **Bearer** token. To do this, we’ll use the `OAuth2PasswordBearer` class.

!!! info

    A "bearer" token isn’t the only option for authentication. However, it’s the most suitable for our use case and often the best choice for most scenarios.

    Unless you’re an OAuth2 expert and know of another option that better fits your needs, **Ravyn** gives you the flexibility to implement other options as well.

    When creating an instance of the `OAuth2PasswordBearer` class, we provide the `tokenUrl` parameter. This specifies the URL that the frontend (running in the user's browser) will use to send the `username` and `password` in order to obtain the token.

When we create an instance of the `OAuth2PasswordBearer` class, we provide the `tokenUrl` parameter. This URL is where the client (the frontend running in the user's browser) will send the `username` and `password` in order to obtain a token.

```python hl_lines="6"
{!> ../../../docs_src/security/app.py !}
```

!!! Tip
    Here, `tokenUrl="token"` refers to a relative URL, `token`, which we haven’t created yet. Since it’s a relative URL, it’s equivalent to `./token`.

    This means that if your API is hosted at `https://example.com/`, the full URL would be `https://example.com/token`. If your API is at `https://example.com/api/v1/`, then the full URL would be `https://example.com/api/v1/token`.

    Using a relative URL is important, as it ensures your application continues to function correctly, even in more advanced scenarios, like when running **Behind a Proxy**.

This parameter doesn’t automatically create the `/token` endpoint or path operation. Instead, it simply declares that the URL `/token` will be the endpoint that the client should use to obtain the token.

This information is then used in OpenAPI and displayed in the interactive API documentation, guiding the client on where to send the request for the token.

We will create the actual path operation for this endpoint shortly.

The `oauth2_scheme` variable is an instance of the `OAuth2PasswordBearer` class, but it is also a "callable" object.

This means that you can use it as a function, like this:

```Python
oauth2_scheme(some, parameters)
```

When called, it will handle the extraction of the token from the request, typically from the `Authorization` header.

So, it can be used with `Inject()` and `Injects()`.

### Use it

Now you can pass that `oauth2_scheme` in a dependency with `Inject` and `Injects` natively from Ravyn.

```python hl_lines="9-10"
{!> ../../../docs_src/security/app.py !}
```

The `security` in the handler is what allows the OpenAPI specification to understand what needs to go in the **Authorize**.

This dependency will provide a `str` that gets assigned to the `token` parameter of the *path operation function*.

**Ravyn** will automatically recognize this dependency and use it to define a "security scheme" in the OpenAPI schema. This also makes the security scheme visible in the automatic API documentation, helping both developers and users understand how authentication works for the API.

!!! info
    **Ravyn** knows it can use the `OAuth2PasswordBearer` class (declared as a dependency) to define the security scheme in OpenAPI because `OAuth2PasswordBearer` inherits from `ravyn.security.oauth2.OAuth2`, which, in turn, inherits from `ravyn.security.base.SecurityBase`.

    All security utilities that integrate with OpenAPI and the automatic API documentation inherit from `SecurityBase`. This inheritance structure allows **Ravyn** to automatically recognize and integrate these security features into the OpenAPI schema, ensuring they are properly displayed in the API docs.

## What does it do

**Ravyn** will automatically look for the `Authorization` header in the request, check if it contains a value starting with `Bearer ` followed by a token, and return that token as a `str`.

If it doesn't find an `Authorization` header or if the value doesn't contain a valid `Bearer` token, **Ravyn** will immediately respond with a `401 Unauthorized` error.

You don't need to manually check for the token or handle the error yourself, **Ravyn** ensures that if your function is executed, the `token` parameter will always contain a valid `str`.

You can even test this behavior in the interactive documentation to see how it works in action.

<img src="https://res.cloudinary.com/dymmond/image/upload/v1732014010/esmerald/security/try_g20hqn.png" />

That's correct! At this stage, we're not verifying the validity of the token yet. We're simply extracting it from the `Authorization` header and passing it as a string to the path operation function.

This is an important first step, as it lays the groundwork for authentication. Later, you can implement the logic to validate the token (e.g., checking its signature, expiration, etc.). But for now, this setup ensures that the token is correctly extracted and available for further use.
