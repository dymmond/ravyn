# TEST SUITE KNOWLEDGE BASE

## OVERVIEW
Feature-clustered pytest suite with mixed unit/integration tests, multiple local `conftest.py` files, and async backend/event-loop variations.

## WHERE TO LOOK
| Need | Location | Notes |
|---|---|---|
| Global fixtures | `conftest.py` | `test_client_factory`, fake DAO, template fixtures |
| CLI test fixtures | `cli/conftest.py` | tmp project scaffolds + subprocess helpers |
| Cache integration fixtures | `caches/conftest.py` | redis async fixture + cleanup |
| DB-heavy fixtures | `databases/*/conftest.py` | event loop + destructive DB cleanup |
| OpenAPI test cluster | `openapi/` | schema/detection/webhook/msgspec coverage |
| Security/auth tests | `security/`, `authentication/` | auth wrappers + middleware behavior |

## CONVENTIONS (DELTA)
- Prefer nearest `conftest.py` for local fixture additions.
- Keep async backend assumptions explicit when adding async tests.
- Use `RAVYN_SETTINGS_MODULE=tests.settings.AppTestSettings` for direct pytest runs.

## ANTI-PATTERNS
- Do not mix DB-destructive tests with unrelated shards without isolation.
- Do not introduce event-loop fixture variants that conflict with existing session-level loop fixtures.
- Do not add integration tests that require external services without clear fixture setup/teardown.

## COMMANDS
```bash
task test
hatch run test:test tests/openapi
hatch run test:test tests/security tests/authentication
hatch run test:test tests/cli
```
