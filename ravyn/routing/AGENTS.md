# ROUTING DOMAIN KNOWLEDGE BASE

## OVERVIEW
Routing is the highest-complexity domain: path normalization, includes, lifecycle hooks, permissions, controllers, and websocket/webhook paths.

## WHERE TO LOOK
| Need | Location | Notes |
|---|---|---|
| Router core behavior | `router.py` | Main include/route coercion logic |
| Gateway types | `gateways.py`, `webhooks.py` | HTTP/WebSocket/Webhook wrappers |
| Decorator wiring | `_decorator_factory.py` | Decorator -> handler transformation |
| Controller adaptation | `controllers/base.py` | Class-based handler conversion |
| Route matching support | `core/base.py` | Shared route core structures |

## CONVENTIONS (DELTA)
- Preserve backwards route semantics unless tests are intentionally updated.
- Includes and lifecycle hooks are order-sensitive; keep top-down traversal behavior.
- Keep permission/interceptor conversion consistent with existing `wrap_permission` flow.

## ANTI-PATTERNS
- Do not special-case a single route shape without tests in `tests/routing/`.
- Do not alter path leading/trailing slash assertions casually.
- Do not mix Ravyn and Lilya permission styles in same path (assertion exists for this).

## REQUIRED TEST FOCUS
```bash
hatch run test:test tests/routing tests/test_router.py tests/test_urls_include.py
```
