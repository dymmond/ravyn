# Example

Since [Edgy](https://edgy.dymmond.com) if from the same author of Ravyn, it gives some
extra motivation for its use and therefore an example in how to use the
[JWTAuthMiddleware](./middleware.md), even if in a very simplistic way, within your Ravyn application.

Let us build a simple integration and application where we will be creating:

- [Create user model](#create-user-model) by using the provided default from Ravyn.
- [Create user API](#create-user-api) to create a user in the system.
- [Login API](#login-api) to authenticate the user.
- [Home API](#home-api) to authenticate the user and return the logged-in user email.
- [Assemble the apis](#assemble-the-apis) where we wrap the application.
- [Bonus - Refreshing the Token](#refreshing-the-token) where we will cover how to implement a token refresh API.

We will be using SQLite for this example but feel free to integrate with your database.

We will also be assuming the following:

- Models are inside an `accounts/models.py`
- Controllers/APIs are inside an `accounts/controllers.py`
- The main application is inside an `app.py`
- The [jwt_config](../../configurations/jwt.md#jwtconfig-and-application-settings)
is inside your global [settings](../../application/settings.md).

**Lets go!**

## Create user model

First, we need to create a model that will be storing the users in the system. We will be
defaulting to the one model provided by Ravyn out-of-the-box.

```python title="accounts/models.py"
{!> ../../../docs_src/databases/edgy/example/create_model.py !}
```

## Create user API

Now that the [user model](#create-user-model) is defined and created, it is time to create an api
that allows the creation of users in the system.

This example won't cover corner cases like integrity in case of duplicates and so on as this is
something that you can easily manage.

```python title="accounts/controllers.py"
{!> ../../../docs_src/databases/edgy/example/create_user.py !}
```

## Login API

Now the [create user](#create-user-api) is available to us to be used later on, we need a view
that also allow us to login and return the JWT access token.

For this API to work, we need to guarantee the data being sent is valid, authenticate and then
return the JWT token.

```python title="accounts/controllers.py"
{!> ../../../docs_src/databases/edgy/example/login.py !}
```

Ooof! There is a lot going on here right? Well, yes but this is also intentional. The `login`
is actually very simple, it just receives a payload and throws that payload into validation
inside the `BackendAuthentication`.

For those familiar with similar objects, like Django backends, this `BackendAuthentication` does
roughly the same thing and it is quite robust since it is using pydantic when creating the instance
which takes advantage of the validations automatically for you.

The `BackendAuthentication` once created inside the `login` and validated with the given fields,
simply proceeds with the `authenticate` method where it will return the JWT for the user.

!!! Warning
    As mentioned before in the assumptions on the top of the document, it was assumed you put your
    [jwt_config](../../configurations/jwt.md#jwtconfig-and-application-settings) inside your global settings.

## Home API

Now it is time to create the api that will be returning the email of the logged in user when hit.
The API is pretty much simple and clean.

```python title="accounts/controllers.py"
{!> ../../../docs_src/databases/edgy/example/home.py !}
```

## Assemble the APIs

Now it the time where we assemble everything in one place and create our Ravyn application.

```python title="app.py"
{!> ../../../docs_src/databases/edgy/example/assemble.py !}
```

Did you notice the import of the `JWTAuthMiddleware` is inside the
[Include](../../routing/routes.md#include) and not in the main Ravyn instance?

**It is intentional!** Each include handles its own middlewares and to create a user and login
you **don't want to be logged-in** and for that reason, the `JWTAuthMiddleware` is only for those
endpoints that **require authentication**.

Now this assembling is actually very clean, right? Yes and the reason for that is because Ravyn
itself promotes clean design.

We have imported all the APIs directly in the `app.py` but this **is not mandatory**. You can
take advantage of the [Include](../../routing/routes.md#include) and clean your application
even more.

## Refreshing the token

All of these APIs are great to start with but an application using JWT usually needs something
that allows to refresh the existing token. That process can be done in many different ways.

Ravyn provides an example how to [refresh the token](../../configurations/jwt.md#the-claims) with
details that can serve and help you with your process.

The example contains ways of taking advantage of the existing tools provided by Ravyn as well
as assumptions how to structure it.

Check out [how to implement a refresh token](../../configurations/jwt.md#the-claims).

## Extra

Come on, give it a try, create your own version and then try to access the `home`.

Let us see how we could access `/` using the current setup.

For this will be using `httpx` but you are free to use whatever client you prefer.

### Steps

1. Create a user.
2. Login and get the jwt token.
3. Access the home `/`.

```python
{!> ../../../docs_src/databases/edgy/example/access.py !}
```

Did you notice the `Authorization` in the `headers`? Well that is because the default `api_key_header`
from the [JWTConfig](../../configurations/jwt.md#parameters) is called `Authorization` and the
contrib middleware from Ravyn to provide integration with Edgy uses it to validate if is passed
in the header or not.

Like everything in Ravyn, that is also configurable. If you change the `header` to something else
in that config, it will automatically reflect across the contib middlewares.

## Conclusions

This is just a simple example how you could use Edgy with the provided `JWTAuthMiddleware`
from **Ravyn** and build a quick, yet robust, login system and access protected APIs.
