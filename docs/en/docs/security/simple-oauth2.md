# OAuth2 with Password and Bearer

Now, let's build upon the [previous chapter](./interaction.md) and add the missing parts to complete the security flow.

The following examples were inspired by the same examples of FastAPI so it is normal if you feel familiar. The reson for
that its to make sure you don't need to have a new learning curve in terms of understanding and flow.

## The `username` and `password`

We’re going to use **Ravyn** security utilities to handle the `username` and `password`.

According to the OAuth2 specification, when using the "password flow" (which we are using), the client/user must send `username` and `password` fields as form data.

The specification requires these fields to be named exactly as `username` and `password` so names like `user-name` or `email` won’t work in this case.

However, don’t worry, you can display these fields however you like in the frontend, and your database models can use different names if needed.

But for the login *path operation*, we need to follow these names to stay compliant with the specification (and to ensure compatibility with tools like the integrated API documentation).

Additionally, the spec specifies that the `username` and `password` should be sent as form data, so **no JSON** here.

### The `scope`

The specification also allows the client to send another form field, `scope`.

The field name must be `scope` (in singular), but it is actually a string containing "scopes" separated by spaces.

Each "scope" is a single string without spaces, and they are typically used to define specific security permissions. For example:

- `users:read` or `users:write` are common scopes.
- `instagram_basic` is used by Facebook/Instagram.
- `https://www.googleapis.com/auth/drive` is used by Google.

These scopes help specify the level of access or permissions the user or client is requesting.

!!! Info
    In OAuth2, a "scope" is simply a string that declares a specific permission required.

    It doesn't matter if the string includes other characters like `:` or if it's a URL.

    These details are implementation-specific, but for OAuth2, scopes are just strings.

## The operation to get the `username` and `password`

Let us use the Ravyn built-ins to perform this operation.

### OAuth2PasswordRequestForm

First, import `OAuth2PasswordRequestForm`, and use it as a dependency with `Security`, `Inject` and `Injects` in the *path operation* for `/token`:

```python hl_lines="5"
{!> ../../../docs_src/security/post.py !}
```

!!! Note
    The `Inject` and `Injects()` are what makes Ravyn dependency injection quite unique and layer based.

The `OAuth2PasswordRequestForm` is a class dependency that defines a form body containing the following fields:

- The `username`.
- The `password`.
- An optional `scope` field, which is a single string made up of multiple strings separated by spaces.
- An optional `grant_type`.

!!! Tip
    According to the OAuth2 specification, the `grant_type` field is *required* and must have a fixed value of `password`. However, `OAuth2PasswordRequestForm` does not enforce this requirement.

    If you need to strictly enforce the `grant_type` field, you can use `OAuth2PasswordRequestFormStrict` instead of `OAuth2PasswordRequestForm`.

- An optional `client_id` (not needed for our example).
- An optional `client_secret` (also not needed for our example).

!!! Info
    The `OAuth2PasswordRequestForm` is not a special class in **Ravyn**, unlike `OAuth2PasswordBearer`.

    `OAuth2PasswordBearer` informs **Ravyn** that it represents a security scheme, which is why it gets added as such to the OpenAPI schema.

    In contrast, `OAuth2PasswordRequestForm` is simply a convenience class dependency. You could have written it yourself or declared the `Form` parameters directly.

    Since it's a common use case, **Ravyn** provides this class out of the box to make your work easier.

## The form data

!!! Tip
    The instance of the `OAuth2PasswordRequestForm` dependency class won’t have a `scope` attribute containing the long string separated by spaces. Instead, it will have a `scopes` attribute, which is a list of individual strings representing each scope sent.

    Although we’re not using `scopes` in this example, the functionality is available if you need it.

Retrieve the user data from the (fake) database using the `username` from the form field.

If no user is found, raise an `HTTPException` with the message: **"Incorrect username or password"**.

```python hl_lines="4 79-81"
{!> ../../../docs_src/security/post.py !}
```

### Checking the Password

Now that we have the user data from our database, we need to verify the password.

First, we will place the user data into the Pydantic `UserDB` model.

Since storing plaintext passwords is unsafe, we'll use a (fake) password hashing system for verification.

If the passwords don’t match, we'll return the same error as before.

#### What is Password Hashing?

Hashing transforms a value (like a password) into a seemingly random sequence of bytes (a string) that looks like gibberish.

- Providing the same input (password) always produces the same hash.
- However, it is a one-way process. You cannot reverse a hash back to the original password.

##### Why Use Password Hashing?

If your database is compromised, the attacker won't have access to the user's plaintext passwords—only the hashes.

This protects users because the attacker cannot reuse their passwords on other systems (a common risk since many people reuse passwords).

```python hl_lines="82-85"
{!> ../../../docs_src/security/post.py !}
```

#### About the `**user_dict`

`UserDB(**user_dict)` means:

It takes the keys and values from the `user_dict` and passes them directly as key-value arguments to the `UserDB` constructor. This is equivalent to:

```python
UserDB(
    username=user_dict["username"],
    email=user_dict["email"],
    full_name=user_dict["full_name"],
    disabled=user_dict["disabled"],
    hashed_password=user_dict["hashed_password"],
)
```

## Returning the Token

The response from the `token` endpoint should be a JSON object containing:

- A `token_type`. Since we're using "Bearer" tokens, it should be set to `"bearer"`.
- An `access_token`, which is a string containing the actual token.

In this simplified example, we'll just return the `username` as the token (though this is insecure).

!!! Tip
    In the next chapter, we'll implement a secure version using password hashing and JSON Web Tokens (JWT).
    But for now, let's focus on the key details.

```python hl_lines="87"
{!> ../../../docs_src/security/post.py !}
```

!!! Info
    According to the spec, the response should include a JSON with an `access_token` and a `token_type`, as shown in this example.

    This is something you must implement in your code, ensuring the correct use of these JSON keys.

    It's almost the only part you need to manage manually to comply with the specifications. For everything else, **Ravyn** takes care of it for you.

## Updating the Dependencies

Now, let's update our dependencies.

We want to retrieve the `current_user` **only** if the user is active. To do this, we will create a new dependency, `get_current_active_user`, which will rely on `get_current_user` as a sub-dependency.

Both dependencies will raise an HTTP error if the user doesn't exist or if the user is inactive.

With this update, the endpoint will only return a user if the user exists, is authenticated correctly, and is active.

```python hl_lines="54-65"
{!> ../../../docs_src/security/post.py !}
```

!!! Info
    The additional `WWW-Authenticate` header with the value `Bearer` is part of the OAuth2 specification.

    Any HTTP error with a status code 401 "UNAUTHORIZED" should include this header. For bearer tokens (like in our case), the header's value should be `Bearer`.

    While you can technically omit this header and it will still function, including it ensures compliance with the specification. Additionally, some tools may expect and use this header, either now or in the future, which could be helpful for you or your users.

    That's the advantage of following standards.

## Go ahead and test it

Open the OpenAPI documentation and check it out: [http://localhost:8000/docs/swagger](http://localhost:8000/docs/swagger).

### Authenticate

Click the **Authorize** button and use the following credentials:

* **User**: `janedoe`
* **Password**: `secret`.

<img src="https://res.cloudinary.com/dymmond/image/upload/v1733758942/esmerald/security/authorize_jimv3t.png" alt="Authorize">

After pressing the authenticate, you should be able to see something like this:

<img src="https://res.cloudinary.com/dymmond/image/upload/v1733759042/esmerald/security/done_mgpwvt.png" alt="Done">

### Get the data

Now it is time to test and get the data using the `GET` method provided in the examples `/users/me`.

You will get a payload similar to this:

```json
{
    "username": "johndoe",
  "email": "johndoe@example.com",
  "full_name": "John Doe",
  "disabled": false,
  "hashed_password": "fakehashedsecret"
}
```

<img src="https://res.cloudinary.com/dymmond/image/upload/v1733759233/esmerald/security/payload_eaxlaf.png" alt="Payload">

Now, if you logout by clicking in the logout icon, you should receive a 401.

<img src="https://res.cloudinary.com/dymmond/image/upload/v1733759352/esmerald/security/not_auth_nwd72q.png" alt="Not authenticated">

## Inactive users

Now you can try with an inactive user and see what happens.

* **User**: `peter`
* **Password**: `secret2`.

You should have an error like this:

```json
{
  "detail": "Inactive user"
}
```

As you can see, we have now implemented a simple and yet effective authentication.
