# Path Parameters

Path parameters are those, as the name suggests, parameters that are part of a URL (path) definition.

You can declare the path parameters (you can think of them as variables) using the same python syntax for strings.

```python
{!> ../../../docs_src/extras/path/example.py !}
```

As you can see, the `user_id` declared in the path was also passed and provided in the function `user`. This is how
you must declare path parameters in Ravyn.

You can now access the URL:

```shell
http://127.0.0.1/users/1
```

## Declaration of the parameters

**Ravyn** being developed on top of [Lilya][lilya] also means that it allows **two** different syntaxes for the declaration
of the parameters.

=== "Default"

    ```python
    {!> ../../../docs_src/extras/path/example.py !}
    ```

=== "Less than/Greater than"

    ```python
    {!> ../../../docs_src/extras/path/example_gt.py !}
    ```

Ravyn allows the use of `{}` and `<>` syntaxes. Both work in an `equal` way and the reasoning for that is only to
allow the users to choose their own preference.

## Default parameters

When declaring a controller with path parameters, if no type is specified in the `string` declaration, Ravyn will assume
it will be of type `string`.

```python
{!> ../../../docs_src/extras/path/example.py !}
```

If you wish to specifiy exactly the type for the path parameter, you can do it by liteally specifiying the type of the
parameter.

```python
{!> ../../../docs_src/extras/path/example_type.py !}
```

This will make sure it will enforce the type `int` and throws an error if an invalid integer is provided.

When providing the path parameters with a proper typing, this will also make sure the [OpenAPI](../openapi.md) documentation
will have the right type for you to test.

## Custom typing and transformers

What if you need to create a custom typing that is not natively supported by Ravyn? Well, Ravyn has your back with
the [transformers](../routing/routes.md#custom-transformers).

This will make sure you have your own transformer for your own unique typing and Ravyn can understand it.

Since Ravyn is built on top of [Lilya][lilya], that means it also supports natively the same types.

You can [check here for more details](../routing/routes.md#path-parameters).

## Enums

Ravyn also supports `Enum` types as typing. Yes, that's right, natively Ravyn handles Enums for you. This will
trigger automatic validations of Ravyn in case a wrong value is provided.

```python
{!> ../../../docs_src/extras/path/enum.py !}
```

You can now call:

```shell
http://127.0.0.1/users/admin
```

If you, for example, provide something like this:

```shell
http://127.0.0.1/users/something
```

And since `something` is not declared in the Enum type, you will get an error similar to this:

```json
{
    "detail": "Validation failed for http://127.0.0.1/users/something with method GET.",
    "errors": [
        {
            "type": "enum",
            "loc": ["item_type"],
            "msg": "Input should be 'user' or 'admin'",
            "input": "something",
            "ctx": {"expected": "'user' or 'admin'"},
            "url": "https://errors.pydantic.dev/2.8/v/enum",
        }
    ],
}
```

[lilya]: https://lilya.dev
