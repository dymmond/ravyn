# DOCS SOURCE KNOWLEDGE BASE

## OVERVIEW
`docs_src/` stores runnable/snippet-style example code consumed by the docs pipeline include renderer. It is source content, not generated output.

## WHERE TO LOOK
| Need | Location | Notes |
|---|---|---|
| Routing examples | `routing/` | handlers/routes/controller snippets |
| Response examples | `responses/` | json/orjson/ujson/template/stream examples |
| Security/auth examples | `security/`, `authentication/` | API key/JWT/auth snippets |
| Scheduler examples | `scheduler/` | asyncz/tasks/trigger examples |
| Extras examples | `extras/` | query/path/body/cookies/forms uploads |
| Integration with docs pipeline | `../scripts/docs_pipeline.py` | include expansion + fencing rules |

## CONVENTIONS (DELTA)
- Keep examples minimal and importable; they are inlined into docs pages.
- Match directory domain to docs chapter (avoid cross-domain random placement).
- Treat this tree as canonical snippets for docs includes.

## ANTI-PATTERNS
- Do not place generated artifacts here.
- Do not reference missing include paths from docs markdown (prepare/build will fail).
- Do not add heavyweight runtime dependencies in snippets without docs extra context.

## COMMANDS
```bash
hatch run docs:prepare
hatch run docs:build
```
