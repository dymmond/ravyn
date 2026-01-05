# OAuth2 with Password, Bearer with JWT tokens

Now that we’ve outlined the security flow, let’s secure the application using JWT tokens and secure password hashing.

The following code is production-ready. You can store hashed passwords in your database and integrate it into your application.

We’ll build on the foundation from the previous chapter and enhance it further.

## What is the JWT

JWT extends for *JSON Web Token* and it is widely adopted and used to secure systems around the world.

JWT is also a standard and quite lengthy.

```json
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

!!! Info
    The previous example was extracted from [https://jwt.io/](https://jwt.io) if you decide to play around
    and see what you can do with it.

JWT tokens are not encrypted, meaning their contents can be read if intercepted. However, they are signed, ensuring you can verify that the token was issued by you and hasn't been tampered with.

This allows you to issue a token with a set expiration, for example, one week. If the user returns the next day with the token, you can verify they are still logged into your system. After the token expires, the user will no longer be authorized and must log in again to obtain a new one.

If someone attempts to modify the token, such as changing the expiration date, the signature validation will fail, exposing the tampering attempt.

## Installing `PyJWT`

The following examples will be assuming that you don't know about anything although,
**Ravyn also comes with [JWT integration](../configurations/jwt.md)** and there are details how to leverage it.

You will be required to install some additional libraries when using the following examples but summarizing it, you
can also achieve the same results by running:

```shell
$ pip install ravyn[jwt]
```

!!! Warning
    It is strongly advised to use virtual environments to isolate your packages from the core system ones and avoiding to break them by accident.

To use digital signature algorithms like RSA or ECDSA, make sure to install the `cryptography` library by adding the `pyjwt[crypto]` dependency.

For more details, refer to the [PyJWT Installation Documentation](https://pyjwt.readthedocs.io/en/stable/installation.html).

Now it is time to install `PyJWT`.

```shell
$ pip install pyjwt
```

## Password Hashing

Hashing involves transforming content (such as a password) into a seemingly random sequence of bytes (a string) that resembles gibberish.

The same input (e.g., the same password) will always produce the same hashed output. However, the process is one-way, meaning you cannot reverse the hash to recover the original content.

### Why hashing is important

If your database is compromised, the attacker will only have access to hashed passwords, not the plaintext ones.

This prevents the thief from directly using the passwords on other systems, which is critical since many users reuse the same password across multiple platforms.

An example of hashing is what Django (and **Ravyn**) offer, the **PBKDF2** (Password-Based Key Derivation Function 1 and 2).

To help us with this, we will be using `passlib`.

## Installing `passlib`

PassLib is an excellent Python library for managing password hashing.

It supports a variety of secure hashing algorithms and provides utilities for working with them.

The recommended algorithm is **Bcrypt**, known for its robust security features.

```shell
$ pip install passlib[bcrypt]
```

!!! Tip
    PassLib allows you to configure it to read passwords hashed by frameworks like Django, Flask security plugins, and others.

    This enables scenarios such as sharing a database between a Django application and a Ravyn application or gradually migrating a Django
    application to Ravyn.

    Users can seamlessly log in from either application, ensuring compatibility and a smooth transition.

## Hashing and verification of the passwords

This can be achived by importing everything that is needed from `passlib` package.

Create a PassLib "context" to handle password hashing and verification.

!!! Tip
    The PassLib context supports multiple hashing algorithms, including deprecated ones, enabling you to verify old hashes while using a secure algorithm like Bcrypt for new passwords.

    This allows compatibility with existing systems (e.g., verifying Django-generated passwords) while ensuring stronger security for newly hashed passwords. all within the same application.

Create a utility function to hash a user's password, another to check if a given password matches the stored hash, and a third to authenticate the user and return their details.

```python hl_lines="6 29 64-65 68-69 77-81"
{!> ../../../docs_src/security/hash/app.py !}
```

!!! Check
    In the new (fake) database, `fake_users_db`, the hashed password will appear as a string like this: `"$2a$12$KplebFTPwFcgGQosJgI4De0PyB2AoRCSxasxHpFoYZPp6uQV/xLzm"`. You can test the username `janedoe` and the
    password `hashsecret` against this value and confirm it is correct using any online platform dedicated to this.

## Handling JWT Tokens

Import the necessary modules.

Generate a random secret key to sign the JWT tokens.

Use the following command to generate a secure random secret key:

```shell
$ openssl rand -hex 32
```

Here’s a clearer and more concise version of the instructions:

1. Copy the output of the random secret key generation into the `SECRET_KEY` variable (do not use the example key).
2. Create a variable `ALGORITHM` and set it to `"HS256"`, the algorithm used for signing the JWT token.
3. Define a variable for the token’s expiration time.
4. Define a Pydantic model to use for the response in the token endpoint.
5. Create a utility function to generate a new access token.

```python hl_lines="4 5 24-26 44-46 84-88"
{!> ../../../docs_src/security/hash/app.py !}
```

## Dependencies Update

Update `get_current_user` to accept the same token as before, but now use JWT tokens.

Decode the received token, verify its validity, and return the current user. If the token is invalid or a user is disabled, immediately raise an HTTP error.

```python hl_lines="91-108"
{!> ../../../docs_src/security/hash/app.py !}
```

## Update the `/token` handler

Create a `timedelta` object for the token's expiration time.

Generate a valid JWT access token and return it.

```python hl_lines="111-128"
{!> ../../../docs_src/security/hash/app.py !}
```

### The technicalities of the subject `sub`

The JWT specification includes a `sub` key, which represents the subject of the token. Although optional, it is often used to store the user's unique identifier.

JWTs can be used for more than just identifying users. For example, you might use them to represent entities like a "car" or a "blog post." You can then assign specific permissions to these entities, such as "drive" for the car or "edit" for the blog post. By issuing a JWT to a user or bot, they can perform actions (e.g., drive the car or edit the blog post) without needing an account, relying solely on the JWT generated by your API.

In more complex scenarios, multiple entities might share the same identifier, such as "foo" representing a user, a car, and a blog post. To prevent ID collisions, you can prefix the `sub` value. For instance, to distinguish a user named "johndoe," the `sub` value could be `username:johndoe`.

The key point is that the `sub` key should contain a unique identifier across the entire application and must be a string.

## Time to verify it

Start the server and navigate to the documentation at [http://127.0.0.1:8000/docs/swagger](http://127.0.0.1:8000/docs).

You should see a similar interface like the following:

<img src="https://res.cloudinary.com/dymmond/image/upload/v1733833628/esmerald/security/jwt_n0ddmm.png" alt="Interface">

Click the **Authorize** button and use the following credentials:

* **User**: `janedoe`
* **Password**: `hashsecret`.

<img src="https://res.cloudinary.com/dymmond/image/upload/v1733833768/esmerald/security/hash_sxv9nh.png" alt="Hash">

Now it time to call the endpoint `/users/me` and you should get a response like the following:

```json
{
  "username": "janedoe",
  "email": "janedoe@example.com",
  "full_name": "Jane Doe",
  "disabled": false
}
```

<img src="https://res.cloudinary.com/dymmond/image/upload/v1733833977/esmerald/security/me_l7bci2.png" alt="Me">

When you open the developer tools, you’ll notice that the data sent includes only the JWT token. The password is sent only in the initial request to authenticate the user and obtain the access token. After that, the password is not transmitted in subsequent requests.

## Advanced usage with `scopes`

OAuth2 defines "scopes" to specify permissions.

These scopes can be included in a JWT token to restrict access.

You can provide this token to a user or a third party to interact with your API under these restrictions.

Advanced usage of JWT tokens often involves scopes, which define specific permissions or actions that the token holder is authorized to perform. Scopes allow more fine-grained control over what users or entities can do within your application.

### Example of Using Scopes in JWT:

1. **Define Scopes**: Scopes are typically added to the payload of the JWT token. For instance, a user might have the scope `read:posts` for viewing posts or `write:posts` for creating new posts.

2. **Include Scopes in JWT**: When generating a token, include the relevant scopes in the payload. For example:

   ```python
   jwt_payload = {
       "sub": "username:johndoe",
       "scopes": ["read:posts", "write:posts"]
   }
   ```

3. **Check Scopes During Authorization**: In your API, when processing requests, you can check if the JWT token includes the necessary scopes for the requested action.

   Example of checking the `write:posts` scope:

   ```python
   def has_scope(required_scope: str, token_scopes: list) -> bool:
       return required_scope in token_scopes

   token_scopes = decoded_token.get("scopes", [])
   if not has_scope("write:posts", token_scopes):
       raise HTTPException(status_code=403, detail="Permission denied")
   ```

4. **Scope-Based Authorization**: You can use scopes to authorize access to specific resources. For example, only users with the `admin` scope might be allowed to delete posts, while users with `read:posts` can only view them.

5. **Scope Granularity**: Scopes can be used to manage access on different levels, such as at the API, user, or resource level, giving you fine-grained control over who can do what within your application.

By using scopes in JWT, you can enhance security and implement role-based access control (RBAC) or permission-based access control for more complex use cases.

## Notes

These step by step guides were inspired by **FastAPI** great work of providing simple and yet effective examples for everyone to understand.

Ravyn adopts a different implementation internally but with the same purposes as any other framework to achieve that.
