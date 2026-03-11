# SECURITY DOMAIN KNOWLEDGE BASE

## OVERVIEW
Security layer wraps Lilya security primitives (HTTP/API key/OAuth2/OpenID/JWT) and feeds OpenAPI security metadata and auth dependencies.

## WHERE TO LOOK
| Need | Location | Notes |
|---|---|---|
| JWT token model | `jwt/token.py` | Encode/decode + expiration behavior |
| HTTP auth wrappers | `http/http.py` | Basic/Bearer/Digest wrappers |
| API key wrappers | `api_key/api_key.py` | Header/query/cookie API key flows |
| OAuth2 flows | `oauth2/oauth.py` | Password/code/bearer scheme variants |
| OpenID connect | `open_id/openid_connect.py` | OpenID security scheme wrapper |

## CONVENTIONS (DELTA)
- Keep wrapper behavior aligned with upstream Lilya contracts.
- Preserve dependency-injection usage patterns expected by tests (Inject/Injects).
- Keep docs/examples synchronized for auth flows, especially JWT and middleware examples.

## ANTI-PATTERNS
- Do not change credential return types without updating security/http tests.
- Do not weaken expiration/signing assumptions in token paths.
- Do not add non-HTTPS-friendly security examples in docs.

## REQUIRED TEST FOCUS
```bash
hatch run test:test tests/security tests/authentication tests/databases/edgy tests/databases/mongoz
```
