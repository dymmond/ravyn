# Models

In simple terms, models are a representation of a database table in the format of an object declared by the language
implementing.

## User models

Integrating with Edgy, Ravyn already provides some of the models that helps you with the
initial configuration.

1. `AbstractUser` - The base user class containing all the fields required a user.
2. `User` - A subsclass of `AbstractUser`

## User

Extenting the existing `User` model is as simple as this:

```python hl_lines="18 33"
{!> ../../../docs_src/databases/edgy/models.py !}
```

This is a clean way of declaring the models and using the Edgy docs, you can easily understand
why this is like the way it is.

### Meta class

There are way of making the models and the registry cleaner, after all, you might want to use the
same registry in different models across multiple applications in your codebase.

One way and a way Ravyn always recommend, is by leveraging the [settings](../../application/settings.md).

### Leveraging the settings for your models

Let us use the same example but this time, we will be using the settings.
Since **you can access the settings anywhere in the codebase**.

Check it out the example below and how by using the settings, you can literally leverage Ravyn
with Edgy.

=== "settings.py"

    ```python hl_lines="15-17"
    {!> ../../../docs_src/databases/edgy/settings/settings.py !}
    ```
=== "models.py"

    ```python hl_lines="18 33"
    {!> ../../../docs_src/databases/edgy/settings/models.py !}
    ```

=== "app.py"

    ```python
    {!> ../../../docs_src/databases/edgy/settings/app.py !}
    ```

You simply isolated your common database connection and registry inside the globally accessible
settings and with that you can import in any Ravyn application, ChildRavyn or whatever you
prefer without the need of repeating yourself.

### User model fields

If you are familiar with Django then you are also aware of the way they have their users table and the way they
have the fields declared. Ravyn has a similar approach and provides the following.

* `first_name`
* `last_name`
* `username`
* `email`
* `password`
* `last_login`
* `is_active`
* `is_staff`
* `is_superuser`

### The functions available

Using simply this model it does not bring too much benefits as it is something you can do easily and fast but the
functionality applied to it is already something that would require some extra time to assemble.

!!! Warning
    The following examples assume that you are taking advantage of the settings as
    [decribed before](#leveraging-the-settings-for-your-models).

**create_user**

```python
{!> ../../../docs_src/databases/edgy/create_user.py !}
```

**create_superuser**

```python
{!> ../../../docs_src/databases/edgy/create_superuser.py !}
```

**check_password**

```python hl_lines="28"
{!> ../../../docs_src/databases/edgy/check_password.py !}
```

Because you are using the `User` provided by Ravyn, the same object is also prepared to validate
the password against the system. If you are familiar with Django, this was based on it and has the
same principle.

**set_password**

```python hl_lines="28"
{!> ../../../docs_src/databases/edgy/set_password.py !}
```

The same for setting passwords. The `User` already contains the functionality to set a password of
a given `User` instance.

### What happened

Although the way of using the `User` table was intentionally designed to be simple there is in fact a lot going
on behind the scenes.

When using the `create_user` and `create_superuser` behind the scenes it is not only creating that same record and
storing in the database but is also <a href='https://nordpass.com/blog/password-hash/' target='_blank'>hashing</a>
the password for you, using the built-in Ravyn [password hashers](#password-hashers) and this is a life saving
time and implementation.

Ravyn also provides the `set_password` and `check_password` functions to make it easier to
validate and change a user's password using the `User` instance.

## Password Hashers

Ravyn already brings some pre-defined password hashers that are available in the
[Ravyn settings](../../application/settings.md) and ready to be used.

```python

@property
def password_hashers(self) -> list[str]:
    return [
        "ravyn.contrib.auth.hashers.BcryptPasswordHasher",
    ]

```

Ravyn uses <a href='https://passlib.readthedocs.io/en/stable/' target='_blank'>passlib</a> under the hood
in order to facilitate the process of hashing passwords.

You can always override the property `password_hashers` in your
[custom settings](../../application/settings.md#custom-settings) and use your own.

```python
{!> ../../../docs_src/databases/edgy/hashers.py !}
```

## Migrations

You can use any migration tool as you see fit. It is recommended
<a href='https://alembic.sqlalchemy.org/en/latest/' target='_blank'>Alembic</a>.

Edgy also provides some insights in
[how to migrate using alembic](https://edgy.dymmond.com/migrations/migrations).

## General example

More examples and more thorough explanations how to use [Edgy](https://edgy.dymmond.com)
can be consulted in its own [documentation](https://edgy.dymmond.com).
