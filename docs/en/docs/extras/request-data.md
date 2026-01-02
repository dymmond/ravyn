# Request Data

In every application there will be times where sending a payload to the server will be needed.

Ravyn is prepared to handle those with ease and that is thanks to Pydantic.

There are two **default ways** of doing this, using the [data](#the-data-field) and using the [payload](#the-payload-field)
but there are also [custom ways](#complex-request-data) of creating the payload.

!!! Warning
    You can only declare `data` or `payload` in the handler **but not both** or an `ImproperlyConfigured`
    exception is raised.

## The `data` field

When sending a payload to the backend to be validated, the handler needs to have a `data` field declared. Without it,
it will not be possible to process the information and/or will not be recognised.

```python hl_lines="12"
{!> ../../../docs_src/extras/request_data/data_field.py !}
```

Fundamentally the `data` field is what holds the information about the sent payload data into the server.

The data can also be simple types such as `list`, `dict`, `str`. It does not necessarily mean you need to always use
pydantic models.

## The `payload` field

Fundamentally is an alternative to `data` but does exactly the same. If you are more familiar with
the concept of `payload` then this is for you.

```python hl_lines="12"
{!> ../../../docs_src/extras/request_payload/data_field.py !}
```

## Nested models

You can also do nested models for the `data` or `payload` to be processed.

=== "data"

    ```python hl_lines="6 16 20"
    {!> ../../../docs_src/extras/request_data/nested_models.py !}
    ```

=== "payload"

    ```python hl_lines="6 16 20"
    {!> ../../../docs_src/extras/request_payload/nested_models.py !}
    ```

The data expected to be sent to be validated is all required and expected with the following format:

```json
{
    "name": "John",
    "email": "john.doe@example.com",
    "address": {
        "zip_code": "90210",
        "country": "United States",
        "street": "Orange county street",
        "region": "California"
    }
}
```

You can nest as many models as you wish to nest as long as it is send in the right format.

## Mandatory fields

There are many ways to process and validate a field and also the option to make it non mandatory.

That can be achieved by using the typing `Optional` to make it not mandatory.

=== "data"

    ```python hl_lines="9-10 16"
    {!> ../../../docs_src/extras/request_data/not_mandatory.py !}
    ```

=== "payload"

    ```python hl_lines="9-10 16"
    {!> ../../../docs_src/extras/request_payload/not_mandatory.py !}
    ```

The `address` is not mandatory to be send in the payload and therefore it can be done like this:

```json
{
    "name": "John",
    "email": "john.doe@example.com"
}
```

But you can also send the address and inside without the mandatory fields:

```json
{
    "name": "John",
    "email": "john.doe@example.com",
    "address": {
        "zip_code": "90210",
        "country": "United States"
    }
}
```

## Field validation

What about the field validation? What if you need to validate some of the data being sent to the backend?

Since Ravyn uses pydantic, you can take advantage of it.

=== "data"

    ```python hl_lines="9 11-12"
    {!> ../../../docs_src/extras/request_data/validation.py !}
    ```

=== "payload"

    ```python hl_lines="9 11-12"
    {!> ../../../docs_src/extras/request_payload/validation.py !}
    ```

Since pydantic runs the validations internally, you will have the errors thrown if something is missing.

The expected payload would be:

```json
{
    "name": "John",
    "email": "john.doe@example.com",
    "hobbies": [
        "running",
        "swimming",
        "Netflix bing watching"
    ],
    "age": 18
}
```

## Custom field validation

You don't necessarily need to use the pydantic default validation for your fields. You can always apply one of your
own.

=== "data"

    ```python
    {!> ../../../docs_src/extras/request_data/custom_validation.py !}
    ```

=== "payload"

    ```python
    {!> ../../../docs_src/extras/request_payload/custom_validation.py !}
    ```

## Complex request data

Since the release 3.4+, Ravyn allows you to have multiple payloads declared and allows you to customize the way
you want to send it.

The [data](#the-data-field) and [payload](#the-payload-field) will always continue to do what they are supposed to do
which means the following is **valid**.

=== "data"

    ```python
    {!> ../../../docs_src/extras/request_data/custom_validation.py !}
    ```

=== "payload"

    ```python
    {!> ../../../docs_src/extras/request_payload/custom_validation.py !}
    ```

But what if you want to actually have a different payload split by responsabilities or simply because you just want for
organisation purposes guarantee a more complex request?

Let us imagine we want to register a **user** and at the same time we want to provide extra details for that user such
as an **address**.

Well, you can use the `data` or `payload` to do it and send all in one go but you can also do something like this:

```python
{!> ../../../docs_src/extras/request_data/complex_example1.py !}
```

This makes the declaration of the body a bit more oriented to the type of data you want to send. So, how it would the request data
would look like now?

```json
{
    "user": {
        "name": "John",
        "email": "john.doe@example.com",
    },
    "address": {
        "street_name": "123 Queens Park",
        "post_code": "90241"
    }
}
```

Ravyn automatically will understand where to map the request data and assign them to the proper declaration of
the `keys` sent.

### Non mandatory fields in the payload

The same principle applied to everything in Ravyn is also applied here in the same fashion. You can also make the
fields also not mandatory, something like this:

```python
{!> ../../../docs_src/extras/request_data/complex_example_union.py !}
```

!!! Note
    We use `Union` but `Optional` can also be used.

As you can see, now the `address` is a non mandatory field and that means you can simply do:

```json
{
    "user": {
        "name": "John",
        "email": "john.doe@example.com",
    }
}
```

Ravyn will know and understand what to do. Pretty simple, right?

### Using different `Encoders`

Well, Ravyn is also known for being able to mix and match multiple [Encoders](../encoders.md). If you are not familiar
with those, now its a great time to go [read and catch-up with those](../encoders.md).

Now, this is very unlikely to happen where you mix encoders such as `Pydantic` with `Msgspec` or `attrs` but it could
happen if you want, after all you are in charge of your own destiny!

Since Ravyn understands those, that means you can also have a complex payload using different encoders and it would
still work as it is supposed to.

Let us see the use of two encoders at the same time and how you could do it here.

!!! Note
    We will be assuming the [encoders](../encoders.md) section was read and understood and you are comfortable with
    the concept.

We will be using the two **default supported encoders**, Pydantic and MsgSpec.

Using the example from before, now the `Address` won't be a Pydantic model but a Msgspec `Struct`.

```python
{!> ../../../docs_src/extras/request_data/complex_encoders.py !}
```

As you can see, nothing really changed besides the type of object, since Ravyn understands the encoder type, it
will automatically parse them to the proper object and run the declared validations but in terms of the way you send
the request data **remains exactly the same**.

**Sending the whole data**

```json
{
    "user": {
        "name": "John",
        "email": "john.doe@example.com",
    },
    "address": {
        "street_name": "123 Queens Park",
        "post_code": "90241"
    }
}
```

**Sending only the mandatory one**

```json
{
    "user": {
        "name": "John",
        "email": "john.doe@example.com",
    }
}
```

### Important note

From the moment you add an *extra body* to the signasture of your handler, you must declare them explicitly in your request,
**even if you want to call it data or payload, it must be there**.

```python
{!> ../../../docs_src/extras/request_data/complex.py !}
```

Even if you used the `data` reserved word and because the body is now in a complex form, the request must be explicitly
declared, like this:

**Sending the whole data**

```json
{
    "data": {
        "name": "John",
        "email": "john.doe@example.com",
    },
    "address": {
        "street_name": "123 Queens Park",
        "post_code": "90241"
    }
}
```

**Sending only the mandatory one**

```json
{
    "data": {
        "name": "John",
        "email": "john.doe@example.com",
    }
}
```
