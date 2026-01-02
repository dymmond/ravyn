---
hide:

  - navigation
---

# Migration from Esmerald to Ravyn

Esmerald is now Ravyn with a fresh new look! The migration process is simple and straightforward—mostly just updating import statements.

## What You'll Learn

- How to migrate from Esmerald to Ravyn
- Import changes required
- Exception class updates
- Settings class changes
- CLI command updates

## Quick Migration Checklist

- [ ] Update imports from `esmerald` to `ravyn`
- [ ] Change `Esmerald` class to `Ravyn`
- [ ] Update `EsmeraldSettings` to `RavynSettings`
- [ ] Update `EsmeraldException` to `RavynException`
- [ ] Change CLI commands from `esmerald` to `ravyn`
- [ ] Update dependencies in `requirements.txt` or `pyproject.toml`

---

## Why Migrate?

- **Same Great Framework** - All Esmerald features are in Ravyn

- **Active Development** - Ravyn is the actively maintained version

- **Easy Migration** - 99% of code remains the same

- **Better Branding** - Fresh new identity

---

## Migration Steps

### 1. Update Dependencies

**requirements.txt:**
```diff
- esmerald>=2.0.0
+ ravyn>=3.0.0
```

**pyproject.toml:**
```diff
[project]
dependencies = [
-    "esmerald>=2.0.0",
+    "ravyn>=3.0.0",
]
```

Then reinstall:
```bash
pip install -r requirements.txt
# or
pip install -e .
```

---

### 2. Update Imports

Replace all `esmerald` imports with `ravyn`:

**Before:**
```python
from esmerald import Esmerald, Gateway, get, post
from esmerald.conf import settings
from esmerald.middleware import CORSMiddleware
```

**After:**
```python
from ravyn import Ravyn, Gateway, get, post
from ravyn.conf import settings
from ravyn.middleware import CORSMiddleware
```

---

### 3. Update Application Class

**Before:**
```python
from esmerald import Esmerald

app = Esmerald(
    routes=[...],
    debug=True
)
```

**After:**
```python
from ravyn import Ravyn

app = Ravyn(
    routes=[...],
    debug=True
)
```

> [!INFO]
> All parameters remain exactly the same!

---

### 4. Update Exceptions

**Before:**
```python
from esmerald.exceptions import (
    EsmeraldAPIException,
    NotFound,
    ValidationError
)

raise EsmeraldAPIException(detail="Custom error")
```

**After:**
```python
from ravyn.exceptions import (
    RavynAPIException,
    NotFound,
    ValidationError
)

raise RavynAPIException(detail="Custom error")
```

!!! tip
    Built-in exceptions like `NotFound` and `ValidationError` remain the same.

---

### 5. Update Settings

**Before:**
```python
from esmerald import EsmeraldSettings

class AppSettings(EsmeraldSettings):
    app_name: str = "My App"
    debug: bool = True
```

**After:**
```python
from ravyn import RavynSettings

class AppSettings(RavynSettings):
    app_name: str = "My App"
    debug: bool = True
```

---

### 6. Update CLI Commands

**Before:**
```bash
# Run development server
esmerald run

# Create directive
esmerald createapp myapp

# Show routes
esmerald show_routes
```

**After:**
```bash
# Run development server
ravyn run

# Create directive
ravyn createapp myapp

# Show routes
ravyn show_routes
```

---

## Automated Migration

### Using Find and Replace

You can use your editor's find and replace feature:

**Find:** `esmerald`  
**Replace:** `ravyn`

**Find:** `Esmerald`  
**Replace:** `Ravyn`

**Find:** `EsmeraldSettings`  
**Replace:** `RavynSettings`

**Find:** `EsmeraldException`  
**Replace:** `RavynException`

**Find:** `EsmeraldAPIException`  
**Replace:** `RavynAPIException`

### Using sed (Linux/Mac)

```bash
# Backup your files first!
find . -type f -name "*.py" -exec sed -i.bak 's/esmerald/ravyn/g' {} +
find . -type f -name "*.py" -exec sed -i.bak 's/Esmerald/Ravyn/g' {} +
```

### Using PowerShell (Windows)

```powershell
# Backup your files first!
Get-ChildItem -Recurse -Filter *.py | ForEach-Object {
    (Get-Content $_.FullName) -replace 'esmerald', 'ravyn' | Set-Content $_.FullName
}
```

---

## Common Migration Scenarios

### Scenario 1: Basic Application

**Before:**
```python
from esmerald import Esmerald, Gateway, get

@get("/")
def homepage() -> dict:
    return {"message": "Hello"}

app = Esmerald(routes=[Gateway(handler=homepage)])
```

**After:**
```python
from ravyn import Ravyn, Gateway, get

@get("/")
def homepage() -> dict:
    return {"message": "Hello"}

app = Ravyn(routes=[Gateway(handler=homepage)])
```

### Scenario 2: With Settings

**Before:**
```python
from esmerald import Esmerald, EsmeraldSettings

class Settings(EsmeraldSettings):
    debug: bool = True

app = Esmerald(settings_module=Settings)
```

**After:**
```python
from ravyn import Ravyn, RavynSettings

class Settings(RavynSettings):
    debug: bool = True

app = Ravyn(settings_module=Settings)
```

### Scenario 3: With Custom Exceptions

**Before:**
```python
from esmerald.exceptions import EsmeraldAPIException

class CustomError(EsmeraldAPIException):
    status_code = 400
```

**After:**
```python
from ravyn.exceptions import RavynAPIException

class CustomError(RavynAPIException):
    status_code = 400
```

---

## What Stays the Same?

- **All routing patterns** - Gateway, Include, WebSocketGateway

- **All decorators** - @get, @post, @put, @delete, etc.

- **Dependency injection** - Inject, Injects, Factory

- **Middleware** - All middleware works the same

- **Database integrations** - Edgy, Mongoz, etc.

- **Testing** - RavynTestClient (was EsmeraldTestClient)

- **Configuration** - All settings properties

- **Extensions** - Extension system unchanged

---

## Testing Your Migration

### 1. Run Your Tests

```bash
# With hatch
hatch run test:test

# Or with pytest
pytest
```

### 2. Check Imports

```bash
# Search for any remaining esmerald imports
grep -r "from esmerald" .
grep -r "import esmerald" .
```

### 3. Start Development Server

```bash
ravyn run
```

### 4. Verify Functionality

- Test all endpoints
- Check error handling
- Verify middleware
- Test database connections

---

## Common Pitfalls & Fixes

### Pitfall 1: Missed Import

**Problem:** Forgot to update an import.

```python
# Wrong - mixed imports
from ravyn import Ravyn
from esmerald import get  # Old import!
```

**Solution:** Update all imports:

```python
# Correct
from ravyn import Ravyn, get
```

### Pitfall 2: Old CLI Commands

**Problem:** Using old `esmerald` CLI commands.

```bash
# Wrong
esmerald run
```

**Solution:** Use `ravyn` commands:

```bash
# Correct
ravyn run
```

### Pitfall 3: Exception Class Names

**Problem:** Using old exception names.

```python
# Wrong
from ravyn.exceptions import EsmeraldAPIException
```

**Solution:** Use new exception names:

```python
# Correct
from ravyn.exceptions import RavynAPIException
```

---

## Need Help?

If you encounter issues during migration:

- [Open a Discussion](https://github.com/dymmond/ravyn/discussions)
- [Report an Issue](https://github.com/dymmond/ravyn/issues)
- [Check the Documentation](https://ravyn.dev)

---

## Summary

Migration from Esmerald to Ravyn is straightforward:

1. Update dependencies
2. Change imports from `esmerald` to `ravyn`
3. Update class names (`Esmerald` → `Ravyn`)
4. Update settings (`EsmeraldSettings` → `RavynSettings`)
5. Update exceptions (`EsmeraldException` → `RavynException`)
6. Update CLI commands
7. Test thoroughly

**99% of your code remains the same!** ---

## Next Steps

- [Read the Documentation](https://ravyn.dev)
- [Explore New Features](./release-notes.md)
- [Join the Community](https://github.com/dymmond/ravyn/discussions)
