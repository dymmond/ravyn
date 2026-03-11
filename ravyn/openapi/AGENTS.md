# OPENAPI DOMAIN KNOWLEDGE BASE

## OVERVIEW
Internal OpenAPI 3.1.0 generation stack (not external codegen), tightly coupled to Pydantic schema extraction and route transformer metadata.

## WHERE TO LOOK
| Need | Location | Notes |
|---|---|---|
| OpenAPI document assembly | `openapi.py` | `get_openapi()` entrypoint |
| Schema extraction helpers | `utils.py` | `GenerateJsonSchema`, ref template rules |
| Spec models | `models.py` | OpenAPI object models |
| Schema version package | `schemas/v3_1_0/` | Canonical schema version in repo |
| OpenAPI config wiring | `../core/config/openapi.py` | App-facing config + docs endpoints |

## CONVENTIONS (DELTA)
- Keep reference template compatibility (`#/components/schemas/{name}`).
- Preserve 3.1.0 model assumptions unless version migration is explicit and tested.
- Security scheme mapping must remain consistent with wrapper classes in `ravyn/security/*`.

## ANTI-PATTERNS
- Do not switch to external generator tooling in this subtree.
- Do not change schema naming/dedupe rules without updating `tests/openapi/uniques/*`.
- Do not alter webhook include behavior without `tests/openapi/test_webhooks*.py` updates.

## REQUIRED TEST FOCUS
```bash
hatch run test:test tests/openapi
```
