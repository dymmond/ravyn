# SCRIPTS DOMAIN KNOWLEDGE BASE

## OVERVIEW
Operational scripts for docs pipeline, release validation, and local cleanup/install workflows.

## WHERE TO LOOK
| Need | Location | Notes |
|---|---|---|
| Docs orchestration CLI | `docs.py` | prepare/build/serve language workflows |
| Docs include/render internals | `docs_pipeline.py` | include expansion + zensical invocation |
| MkDocs hooks | `hooks.py` | missing-translation + fallback behavior |
| Release guard | `release` | tag/version check + publish |
| Local install helper | `install` | editable install + extras |
| Cleanup helpers | `clean`, `clean.ps1` | artifact/cache cleanup |

## CONVENTIONS (DELTA)
- Release script is authoritative for tag/version safety in CI.
- Docs scripts assume source split (`docs/<lang>/docs` + `docs_src/`) and generate into `docs/<lang>/generated`.
- Hook behavior is part of docs correctness; treat hooks as pipeline code, not optional extras.

## ANTI-PATTERNS
- Do not bypass `scripts/release` checks in publish workflow.
- Do not treat docs build as plain mkdocs build; use scripted pipeline entrypoints.
- Do not modify docs hook fallback logic without multi-language build verification.

## COMMANDS
```bash
python scripts/docs.py build --clean
python scripts/docs.py serve --lang en
./scripts/release
```
