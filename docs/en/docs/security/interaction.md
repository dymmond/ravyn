# Interaction & Next Steps

In the [previous chapter](./introduction.md), the security system. based on **Ravyn's** dependency injection system was providing the `path operation function` with a `token` as a `str`.

This token was extracted from the `Authorization` header of the incoming request. The security system automatically handled this, so the function didn't need to worry about how the token was retrieved. The function simply received the token as a string, which it could then use for further processing, such as verifying the token's validity or checking user permissions.

```python hl_lines="9-10"
{!> ../../../docs_src/security/app.py !}
```

That’s still not very useful as it is.

Let’s enhance it by returning the current user instead.

## Create a user model

By creating a `user` model you can use `Pydantic`, msgspec or whatever you want since Ravyn supports the [encoders](../encoders.md)
making it versatile enough for your needs.

For ths example, let us use the native Pydantic support.

```python
{!> ../../../docs_src/security/enhance.py !}
```

## The `get_current_user` dependency

Let's create a dependency called `get_current_user`.

And remember, dependencies can have sub-dependencies, right?

```python hl_lines="17"
{!> ../../../docs_src/security/enhance.py !}
```

The `get_current_user` dependency will depend on the same `oauth2_scheme` we created earlier.

Just like we did before in the *path operation* itself, our new `get_current_user` dependency will receive a `token` as a `str` from the `oauth2_scheme` sub-dependency.

!!! Warning
    You can see a `Security` object there in the sub-dependency, right? Well, yes, that `Security` object that depends
    of the `scheme` can only be called using this object.

    In other words, when a sub-dependency is a `oauth2_scheme` type of thing or any security related, **you must** use the `Security` object.

    This special object once its declared, **Ravyn** will know what to do with it and make sure it can be executed
    properly.

    Ravyn dependency system is extremely powerful and extremely versatile and therefore some special objects dedicated
    to this security approach were added to make our lives simples.

## Get the user

The `get_current_user` dependency will use a (fake) utility function we created. This function takes the token as a `str` and returns our Pydantic `User` model.

```python hl_lines="13-14"
{!> ../../../docs_src/security/enhance.py !}
```

## Inject the current user

Now, we can use the `Inject` and `Injects` with our `get_current_user` dependency in the *path operation*. This is part
of the special Esmerlad dependency inject system that is also multi layered. You can read again about the
[dependency injection with Ravyn](../dependencies.md).

```python hl_lines="27"
{!> ../../../docs_src/security/enhance.py !}
```

Notice that we declare the type of `current_user` as the Pydantic model `User`.

This ensures that we get type checking and auto-completion support inside the function, making development smoother and more error-free.

Now, you can directly access the current user in the *path operation functions* and handle the security mechanisms at the **Dependency Injection** level, using `Depends`.

You can use any model or data for your security requirements (in this case, a Pydantic model `User`), but you're not limited to a specific data model, class, or type.

For example:

- Want to use an `id` and `email` instead of a `username` in your model? No problem, just use the same tools.
- Prefer a `str` or a `dict`? Or perhaps a database class model instance directly? It all works seamlessly.
- If you have bots, robots, or other systems logging in instead of users, and they only need an access token, that's fine too.

You can use any model, class, or database structure that fits your application's needs. **Ravyn**'s dependency injection system makes it easy and flexible for all cases.

## Code size so far

This example might seem a bit verbose, but remember, we're combining security, data models, utility functions, and *path operations* in the same file.

Here’s the key takeaway:

The security and dependency injection setup is written **once**.

You can make it as complex as you need, but it only needs to be defined in one place. The beauty of **Ravyn** is its flexibility. whether simple or complex, you only write this logic once.

And once it's set up, you can reuse it across **thousands of endpoints** (*path operations*).

All of these endpoints (or any portion of them) can take advantage of the same dependencies or any others you create.

Even with thousands of *path operations*, many of them can be as simple as just a few lines of code.

```python hl_lines="27"
{!> ../../../docs_src/security/enhance.py !}
```

Remember that Ravyn has a flexible dependency injection system and the lines can be cut by a lot avoiding repetition.

You can now access the current user directly in your *path operation function*.

We're already halfway there.

Next, we just need to add a *path operation* that allows the user/client to send their `username` and `password` to get the token. That will be our next step.
