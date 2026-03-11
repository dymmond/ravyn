# OPENAPI TEST DOMAIN KNOWLEDGE BASE

## OVERVIEW
Focused verification for internal OpenAPI generation semantics: response/model detection, schema dedupe, webhook docs, and UI config.

## WHERE TO LOOK
| Need | Location | Notes |
|---|---|---|
| Core OpenAPI tests | `test_config.py`, `test_docs.py`, `test_utils.py` | config + docs endpoints + utilities |
| Response/model detection | `detection/` | automatic response/openapi override behavior |
| Schema uniqueness checks | `uniques/` | primitive/union/list/dict dedupe cases |
| Msgspec integration | `msgspec/` | msgspec model/schema behaviors |
| Webhook docs behavior | `test_webhooks.py`, `test_webhooks_payload.py` | webhook OpenAPI generation |

## CONVENTIONS (DELTA)
- Keep expected OpenAPI snapshots/structures aligned with 3.1.0 assumptions.
- Add tests in the matching subcluster (`detection`, `uniques`, `msgspec`) instead of flat piling.

## ANTI-PATTERNS
- Do not assert incidental dict ordering unless behavior requires it.
- Do not add brittle assertions tied to unrelated docs UI HTML details.

## COMMANDS
```bash
hatch run test:test tests/openapi
```
