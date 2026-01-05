# Encoders

Encoders let you serialize and deserialize custom data types in Ravyn. Want to use attrs, msgspec, or your own data classes? Encoders make it possible without framework limitations.

## What You'll Learn

- What encoders are and why they're useful
- Creating custom encoders
- Registering encoders in your app
- Using encoders with Pydantic and MsgSpec
- Building encoders for attrs and other libraries

## Quick Start

```python
from ravyn import Ravyn
from ravyn.encoders import Encoder
from pydantic import BaseModel

# Pydantic works out of the box
class User(BaseModel):
    name: str
    email: str

@app.get("/user")
def get_user() -> User:
    return User(name="Alice", email="alice@example.com")
    # Automatically serialized to JSON!

app = Ravyn()
app.add_route(get_user)
```

Ravyn automatically handles Pydantic models and MsgSpec structs. For other types, create custom encoders.

---

## Why Use Encoders?

### Benefits:

- **Framework Independence** - Use any serialization library

- **Future Proof** - Add support for new libraries anytime

- **Type Safety** - Automatic validation and serialization

- **Flexibility** - Full control over encoding/decoding

### Built-In Support:

- Pydantic models
- MsgSpec structs
- Python dataclasses
- Standard Python types

---

## How Encoders Work

An encoder has three responsibilities:

1. **`is_type()`** - Check if an object is the right type
2. **`serialize()`** - Convert object to JSON-serializable format
3. **`encode()`** - Convert JSON data to object

```python
from ravyn.encoders import Encoder

class MyEncoder(Encoder):
    def is_type(self, value):
        # Check if value is the right type
        pass
    
    def serialize(self, obj):
        # Convert obj to dict/JSON
        pass
    
    def encode(self, data, target_type):
        # Convert dict/JSON to obj
        pass
```

---

## Creating Custom Encoders

### Example: attrs Library

```python
from ravyn.encoders import Encoder
import attrs

class AttrsEncoder(Encoder):
    def is_type(self, value):
        # attrs uses decorators, check with has()
        return attrs.has(value)
    
    def serialize(self, obj):
        # Convert attrs instance to dict
        return attrs.asdict(obj)
    
    def encode(self, data, target_type):
        # Convert dict to attrs instance
        if self.is_type(target_type):
            return target_type(**data)
        return data
```

### Using the Custom Encoder

```python
from ravyn import Ravyn, get
import attrs

@attrs.define
class Product:
    name: str
    price: float

# Register encoder
app = Ravyn(encoders=[AttrsEncoder])

@get("/product")
def get_product() -> Product:
    return Product(name="Laptop", price=999.99)
    # Automatically serialized!
```

---

## Built-In Encoders

### Pydantic Encoder

Ravyn includes Pydantic support by default:

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

@app.get("/user")
def get_user() -> User:
    return User(name="Alice", age=30)
    # Works automatically!
```

**How it works:**

```python
# Simplified version of Pydantic encoder
class PydanticEncoder(Encoder):
    def is_type(self, value):
        from pydantic import BaseModel
        return isinstance(value, type) and issubclass(value, BaseModel)
    
    def serialize(self, obj):
        return obj.model_dump()
    
    def encode(self, data, target_type):
        return target_type(**data)
```

### MsgSpec Encoder

Also built-in:

```python
from msgspec import Struct

class Product(Struct):
    name: str
    price: float

@app.get("/product")
def get_product() -> Product:
    return Product(name="Phone", price=699.99)
    # Works automatically!
```

---

## Registering Encoders

### Via Application Instance

```python
from ravyn import Ravyn

app = Ravyn(encoders=[AttrsEncoder, MyCustomEncoder])
```

### Via Settings

```python
from ravyn import RavynSettings

class Settings(RavynSettings):
    @property
    def encoders(self):
        return [
            "myapp.encoders.AttrsEncoder",
            "myapp.encoders.CustomEncoder"
        ]

app = Ravyn()  # Encoders loaded from settings
```

### Via add_encoder() Method

```python
from ravyn import Ravyn

app = Ravyn()
app.add_encoder(AttrsEncoder)
```

!!! warning
    Use `add_encoder()` carefully. Encoders should be registered before defining routes that use them.

---

## Complete Custom Encoder Example

### Dataclass Encoder

```python
from ravyn.encoders import Encoder
from dataclasses import is_dataclass, asdict

class DataclassEncoder(Encoder):
    def is_type(self, value):
        """Check if value is a dataclass"""
        return is_dataclass(value)
    
    def serialize(self, obj):
        """Convert dataclass to dict"""
        return asdict(obj)
    
    def encode(self, data, target_type):
        """Convert dict to dataclass"""
        if self.is_type(target_type):
            return target_type(**data)
        return data
```

### Using It

```python
from ravyn import Ravyn, get
from dataclasses import dataclass

@dataclass
class Book:
    title: str
    author: str
    pages: int

app = Ravyn(encoders=[DataclassEncoder])

@get("/book")
def get_book() -> Book:
    return Book(
        title="Python Guide",
        author="Alice",
        pages=350
    )

# GET /book
# Returns: {"title": "Python Guide", "author": "Alice", "pages": 350}
```

---

## Advanced Encoder Example

### JSON Encoder with Custom Types

```python
from ravyn.encoders import Encoder
from datetime import datetime
from decimal import Decimal

class CustomJSONEncoder(Encoder):
    def is_type(self, value):
        # Support datetime and Decimal
        return isinstance(value, (datetime, Decimal))
    
    def serialize(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return obj
    
    def encode(self, data, target_type):
        if target_type == datetime:
            return datetime.fromisoformat(data)
        elif target_type == Decimal:
            return Decimal(str(data))
        return data
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Not Implementing All Methods

**Problem:** Missing required methods.

```python
# Wrong - missing serialize and encode
class BadEncoder(Encoder):
    def is_type(self, value):
        return isinstance(value, MyType)
```

**Solution:** Implement all three methods:

```python
# Correct
class GoodEncoder(Encoder):
    def is_type(self, value):
        return isinstance(value, MyType)
    
    def serialize(self, obj):
        return obj.to_dict()
    
    def encode(self, data, target_type):
        return target_type.from_dict(data)
```

### Pitfall 2: Registering Encoder Too Late

**Problem:** Routes defined before encoder registered.

```python
# Wrong - route defined before encoder
@app.get("/data")
def get_data() -> MyType:
    return MyType()

app.add_encoder(MyTypeEncoder)  # Too late!
```

**Solution:** Register encoders before defining routes:

```python
# Correct
app = Ravyn(encoders=[MyTypeEncoder])

@app.get("/data")
def get_data() -> MyType:
    return MyType()
```

### Pitfall 3: Incorrect is_type() Check

**Problem:** is_type() doesn't properly identify the type.

```python
# Wrong - checks instance instead of type
class BadEncoder(Encoder):
    def is_type(self, value):
        return isinstance(value, MyClass)  # Wrong for type checking
```

**Solution:** Check if it's a class and subclass:

```python
# Correct
class GoodEncoder(Encoder):
    def is_type(self, value):
        return isinstance(value, type) and issubclass(value, MyClass)
```

### Pitfall 4: Not Handling Nested Objects

**Problem:** Encoder doesn't serialize nested objects.

```python
# Wrong - nested objects not handled
class BadEncoder(Encoder):
    def serialize(self, obj):
        return {"name": obj.name}  # Ignores nested objects
```

**Solution:** Recursively serialize nested objects:

```python
# Correct
class GoodEncoder(Encoder):
    def serialize(self, obj):
        return {
            "name": obj.name,
            "nested": obj.nested.to_dict() if obj.nested else None
        }
```

---

## Encoder Patterns

### Pattern 1: Library-Specific Encoder

```python
# For attrs
class AttrsEncoder(Encoder):
    def is_type(self, value):
        import attrs
        return attrs.has(value)
    
    def serialize(self, obj):
        import attrs
        return attrs.asdict(obj)
    
    def encode(self, data, target_type):
        if self.is_type(target_type):
            return target_type(**data)
        return data
```

### Pattern 2: Multiple Type Support

```python
class MultiTypeEncoder(Encoder):
    def is_type(self, value):
        return isinstance(value, (TypeA, TypeB, TypeC))
    
    def serialize(self, obj):
        if isinstance(obj, TypeA):
            return obj.to_dict_a()
        elif isinstance(obj, TypeB):
            return obj.to_dict_b()
        else:
            return obj.to_dict_c()
    
    def encode(self, data, target_type):
        if target_type == TypeA:
            return TypeA.from_dict(data)
        elif target_type == TypeB:
            return TypeB.from_dict(data)
        else:
            return TypeC.from_dict(data)
```

---

## Best Practices

### 1. Test Your Encoders

```python
def test_encoder():
    encoder = MyEncoder()
    
    # Test is_type
    assert encoder.is_type(MyClass)
    
    # Test serialize
    obj = MyClass(name="test")
    data = encoder.serialize(obj)
    assert data == {"name": "test"}
    
    # Test encode
    new_obj = encoder.encode(data, MyClass)
    assert new_obj.name == "test"
```

### 2. Handle Edge Cases

```python
class RobustEncoder(Encoder):
    def serialize(self, obj):
        try:
            return obj.to_dict()
        except AttributeError:
            # Fallback for objects without to_dict()
            return {"value": str(obj)}
```

### 3. Document Your Encoders

```python
class MyEncoder(Encoder):
    """
    Encoder for MyCustomType.
    
    Supports:

    - Serialization to JSON
    - Deserialization from JSON
    - Nested object handling
    """
    pass
```

---

## Next Steps

Now that you understand encoders, explore:

- [Responses](./responses.md) - Return data to clients
- [Requests](./requests.md) - Parse incoming data
- [Dependencies](./dependencies.md) - Inject dependencies
- [Application Settings](./application/settings.md) - Configure encoders
