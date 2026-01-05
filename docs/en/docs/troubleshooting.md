# Troubleshooting

Common issues and solutions when working with Ravyn.

## Routing Issues

### Routes Not Found (404 Errors)

**Problem:** You defined a route but get 404 errors.

**Solution:** Check that:

1. Your route path matches exactly (including leading `/`)
2. If using `Include`, ensure the namespace path is correct
3. Route paths are registered in order. more specific routes should come first

```python
# Wrong - generic route first
app = Ravyn(routes=[
    Gateway("/{id}", handler=get_item),
    Gateway("/special", handler=special_item),  # Never reached!
])

# Correct - specific route first
app = Ravyn(routes=[
    Gateway("/special", handler=special_item),
    Gateway("/{id}", handler=get_item),
])
```

## Configuration Issues

### Settings Not Loading

**Problem:** Custom settings aren't being used.

**Solution:** Ensure `RAVYN_SETTINGS_MODULE` is set **before** running the app:

```shell
# Set it in the same command
RAVYN_SETTINGS_MODULE='myapp.settings.Development' uvicorn app:app
```

## Dependency Injection

### Injection Not Working

**Problem:** Injected dependencies are `None` or cause errors.

**Solution:** Use `Injects()` (with an 's') in the handler signature:

```python
# Wrong
def handler(db = Inject(get_db)):  # Wrong object

# Correct
def handler(db = Injects()):  # Correct - receives injected value
```
