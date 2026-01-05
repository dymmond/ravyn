# The Form

This is a special way of sending a form directly using Ravyn. The `Form` like the
[File](./upload-files.md), inherits from the [Body](./body-fields.md) and applies the special
`media_type` as `application/x-www-form-urlencoded`.

This also means that you can also use the `Body` directly to send a form with your API by simply
declaring `Body(media_type="application/x-www-form-urlencoded")`.

The Form is a simple and cleaner shortcut for it.

The simplest way is by importing the `Form` object from Ravyn.

```python hl_lines="7"
{!> ../../../docs_src/extras/form/form_object.py !}
```

You can also import via:

```python
from ravyn.params import Form
```

As [explained here](./request-data.md#request-data), the handler is expecting a `data` field declared and from there
you can pass more details about the form.

## Examples

You can send the form in many different formats, for example:

1. [A dictionary](#sending-as-dictionary) - Send as normal dictionary.
2. [A dataclass](#a-dataclass) - Send as normal dataclass.
3. [A pydantic dataclass](#pydantic-dataclass) - Send a pydantic dataclass.
4. [Pydantic model](#pydantic-model) - Send a pydantic BaseModel.

You decide the best format to send. For the following examples, we will be using `httpx` for the
requests for explanatory purposes.

### Sending as dictionary

```python hl_lines="9 20 23"
{!> ../../../docs_src/extras/form/as_dict.py !}
```

As you can see, we declared the return signature to be `Dict[str, str]` and the `data` payload to
be a dictionary also `Dict[str, str]`. This way we acn simply send the form as you would normally
do.

### A dataclass

What if you want to type as a dataclass and return it in your response?

```python hl_lines="15 26 29"
{!> ../../../docs_src/extras/form/dataclass.py !}
```

The way the payload is sent to the API will always be the same no matter what, what is important
is how you actually type it. In this example, we declared a `User` dataclass with two field
`name` and `email` and we return exactly what we sent back into the response.

### Pydantic dataclass

A Pydantic dataclass is the same as a normal python dataclass in the end but with some internal
extras from Pydantic but for Ravyn, it is the same.

```python hl_lines="14 25 28"
{!> ../../../docs_src/extras/form/pydantic_dc.py !}
```

### Pydantic model

What if we want to type and return as a Pydantic model? Well, it behaves exactly the same as the
dataclasses.

```python hl_lines="13 24 27"
{!> ../../../docs_src/extras/form/model.py !}
```

## Using form as non-data, non-payload field

When using Form as a non-data, non-payload field, the form receives only the data which matches the field-name.

If you use form-data requests make sure the field content is valid json.
When you use json requests only the portion which matches the field-name is passed through the model wrapped by the form.

## Notes

As you could see from the examples, it is very simple and direct to use the `Form` in Ravyn and
the returns are simply clean.

### Important

Since `Form` is Pydantic field (sort of), that also means you can specify for instance,
the other parameters to be evaluated.

You can check [the list of available parameters default](https://docs.pydantic.dev/latest/api/fields/#pydantic.fields.FieldInfo)
as well.
