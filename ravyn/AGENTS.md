# RAVYN PACKAGE KNOWLEDGE BASE

## OVERVIEW
Core runtime package. Most behavior fans out from `applications.py`, `routing/`, `openapi/`, `security/`, and `core/directives/`.

## WHERE TO LOOK
| Task | Location | Notes |
|---|---|---|
| App bootstrap/lifecycle | `applications.py` | Largest runtime orchestration file |
| Routing internals | `routing/router.py`, `routing/gateways.py` | Highest complexity and most coupling |
| OpenAPI generation | `openapi/openapi.py`, `openapi/utils.py` | Pydantic schema plumbing |
| Security wrappers | `security/http/`, `security/oauth2/`, `security/jwt/` | Mostly wrappers over Lilya primitives |
| Middleware behavior | `middleware/` | `BaseAuthMiddleware` deprecated |
| CLI directives | `core/directives/` | Sayer-based command system |
| Dependency injection | `injector.py`, `params.py`, `utils/dependencies.py` | DI + parameter model interaction |

## CONVENTIONS (DELTA)
- Preserve public import surface in `__init__.py`; avoid silent symbol removals.
- Prefer existing utility helpers (`utils/*`) before adding new duplicate helpers.
- Keep runtime path async-safe; avoid blocking operations in request/middleware code.
- Follow existing Pydantic + type-annotated style; no untyped public APIs.

## HOTSPOTS
- `routing/router.py` (~4k+ LOC): route normalization, include semantics, permission wiring.
- `applications.py` (~3k+ LOC): app-level defaults and integration glue.
- `openapi/openapi.py` + `openapi/schemas/v3_1_0/*`: schema generation and compatibility.

## ANTI-PATTERNS
- Do not introduce new code on deprecated auth middleware path (`BaseAuthMiddleware`).
- Do not bypass include/schema guards in router/openapi to “fix” edge cases quickly.
- Do not add alternate runtime entry paths when existing bootstrap hooks already exist.

## COMMANDS
```bash
hatch run test:check_types
hatch run test:test tests/routing tests/openapi tests/security
```
