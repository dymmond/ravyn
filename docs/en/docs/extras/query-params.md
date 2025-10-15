# Query Parameters

It is very common to simply want to declare some query parameters in your controllers. Sometimes those are also used
as filters for a given search or simply extra parameters in general.

## What are query parameters in Ravyn?

Query parameters are those parameters that are not part of the path parameters and therefore those are automatically
injected as `query` parameters for you.

```python
{!> ../../../docs_src/extras/query/example1.py !}
```

As you can see, the query is a key-pair value that goes after the `?` in the URL and seperated by a `&`.

Applying the previous example, it would look like this:

```shell
http://127.0.0.1/users?skip=1&limit=5
```

The previous url will be translated as the following `query_params`:

- `skip`: with a value of 1.
- `limit`: with a value of 5.

Since they are an integral part of the URL, it will automatically populate the parameters of the function that corresponds
each value.

!!! Tip
    We are will be using direct examples but Ravyn **supports** the `Annotated` declaration as well.

## Declaring defaults

Query parameters are not by design, part of a fixed URL path and that also means they can assume the following:

- They can have defaults, like `skip=1` and `limit=5`.
- They can be `optional`.

In the previous example, the URL had already defaults for `skip` and `limit` and the corresponding typing as per requirement
of Ravyn but what if we want to make them optional?

There are different ways of achieving that, using the `Optional` or `Union`.

!!! Tip
    from Python 3.10+ the `Union` can be replaced with `|` syntax.


=== "Using Optional"

    ```python
    {!> ../../../docs_src/extras/query/example_optional.py !}
    ```

=== "Using Union"

    ```python
    {!> ../../../docs_src/extras/query/example_union.py !}
    ```

!!! Check
    Ravyn is intelligent enough to understand what is a `query param` and what is a `path param`.

Now we can call the URL and ignore the `q` or call it when needed, like this:

**Without query params**

```shell
http://127.0.0.1/users/1
```

**With query params**

```shell
http://127.0.0.1/users/1?q=searchValue
```

## Query and Path parameters

Since Ravyn is intelligent enough to distinguish path parameters and query parameters automatically, that also means
you can have multiple of both combined.

!!! Warning
    You can't have a query and path parameters with the same name as in the end, it is still Python parameters being
    declared in a function.

```python
{!> ../../../docs_src/extras/query/example_combined.py !}
```

## Query parameters as list or dict

In Ravyn you can also have query parameters passed as a `list` or as a `dictionary`.

This can be particularly useful when you are building complex filters, for example.

### As a list

Let us see how it would look like if we were building a list of query params.

```python
{!> ../../../docs_src/extras/query/as_list.py !}
```

As you can see, we made the `role` optional. This will allow you to do something like this:

```shell
http://127.0.0.1/users/1?role=admin&role=user&role=other
```

The `role` value will automatically populated similar to this:

```python
[
  "admin",
  "user",
  "other"
]
```

#### Using Annotated

As mentioned before, we can use the `Annotated` syntax as well. This is how it would look like:

```python
{!> ../../../docs_src/extras/query/as_list_annotated.py !}
```

Same principle as before but now using the `Annotated` syntax approach. Its up to you to decide the best.

### As a dict

There is also the option to pass query parameters as a dictionary. The uses cases are many but in
the end, it will always be up tp you to decide.

Let us see how it would look like.

```python
{!> ../../../docs_src/extras/query/as_dict.py !}
```

Here we call it `roles` and the reason for that is to make it more readable for us, also, we made it optional.

Now you can do something like this:

```shell
http://127.0.0.1/users/1?name=Ravyn&version=2&position=awesome
```

The `roles` will be automatically populated with:

```python
{
  "name": "Ravyn",
  "version": 2,
  "position": "awesome"
}
```

Pretty cool if you want to send completely different set of query parameters.

#### Using the Annotated

Same as for the list, we can also use the `Annotated`.

```python
{!> ../../../docs_src/extras/query/as_dict_annotated.py !}
```

## Mixing parameters

What if we want to mix a lot of parameters in one go? It could happen quite often.

**There are differences when mixing lists and dicts**. if there is no mix between **dict** and **list**
in the same signature, then [list](#as-a-list) and [dict](#as-a-dict) operate as described above but
when both come into the mix, then **dict** when called in the API is **declared differently**.

Let us see an example:

```python
{!> ../../../docs_src/extras/query/mix.py !}
```

Ok, let us now call the API with all of this in mind.

```shell
http://127.0.0.1/users/1?roles=admin&roles=user&positions=senior&positions=junior&indexes=1&indexes=2&others[internal]=hr&others[company]=ACME&q=search
```

This is quite the querystring isn't it? Well, its a normal one to populate **lists* and **dicts**.

Did you notice the syntax for the dict `others`? Its not the same as [the example](#as-a-dict) and the reason for that its
because we are mixing different datastructures in one go.

When this happens **you must explicitly pass the `dict[key]=value` which here translates to `others[internal]=hr` and `others[company]=ACME`.

!!! Note
    This only happens when `list` and `dict` datastructures are mixed in the query parameters. The rest remains as is.

## Required parameters

When you declare a `query parameter` **without a default** and **without being optional** when you call the URL
it will raise an error of missing value for the corresponding.

```python
{!> ../../../docs_src/extras/query/example_mandatory.py !}
```

If you call the URL like this:

```
http://127.0.0.1/users
```

It will raise an error of missing value, something like this:

```json
{
  "detail": "Validation failed for <URL> with method GET.",
  "errors": [
    {
      "type": "int_type",
      "loc": [
        "limit"
      ],
      "msg": "Input should be a valid integer",
      "input": null,
      "url": "https://errors.pydantic.dev/2.8/v/int_type"
    }
  ]
}
```

Which means, you need to call with the declared parameter, like this, for example:

```shell
http://127.0.0.1/users?limit=10
```

## Extra with Ravyn params

Because everything in Ravyn just works you can also add restrictions and limits to your query parameters. For example.
you might want to add a limit into the size of a string `q` when searching not to exceed an X value.

```python
{!> ../../../docs_src/extras/query/example_query.py !}
```

This basically tells that a `q` query parameters must not exceed the length of `10` of an exception will be raised.
