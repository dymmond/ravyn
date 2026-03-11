# PROJECT KNOWLEDGE BASE

## OVERVIEW
Ravyn is a single-package Python ASGI framework (`ravyn/`) with large feature domains (routing, OpenAPI, security, directives), extensive tests (`tests/`), and a custom docs build pipeline (`scripts/docs.py` + `docs_src/`).

## STRUCTURE
```text
ravyn/
├── ravyn/                 # Framework source package
│   ├── routing/           # Router/gateway/controller core
│   ├── openapi/           # OpenAPI generation + schemas
│   ├── security/          # Security scheme wrappers + JWT token model
│   └── core/directives/   # CLI directives + scaffolding loader
├── tests/                 # Feature-clustered pytest suite
├── docs_src/              # Docs example/snippet sources
├── docs/                  # Language docs + generated outputs
├── scripts/               # Release + docs orchestration scripts
└── pyproject.toml         # Build/test/lint/type/docs source-of-truth
```

## WHERE TO LOOK
| Task | Location | Notes |
|---|---|---|
| Package config, extras, hatch scripts | `pyproject.toml` | Includes `jwt`, `schedulers`, `docs`, `testing` extras |
| CLI entry and command registration | `ravyn/__main__.py`, `ravyn/core/directives/cli.py` | `ravyn` console script dispatches here |
| Runtime app wiring | `ravyn/applications.py` | Large central bootstrap file |
| Router behavior | `ravyn/routing/` | Highest-complexity area |
| OpenAPI generation | `ravyn/openapi/openapi.py` | Uses Pydantic schema generation |
| Security + auth wrappers | `ravyn/security/`, `ravyn/middleware/authentication.py` | Includes deprecation of `BaseAuthMiddleware` |
| Test conventions + shared fixtures | `tests/conftest.py`, `tests/*/conftest.py` | Several suites override event loop/backend |
| Docs include/render pipeline | `scripts/docs.py`, `scripts/docs_pipeline.py`, `scripts/hooks.py` | Custom include + translation fallback behavior |
| CI gates | `.github/workflows/*.yml` | Test suite, docs-guard, publish, codspeed |
| Release hard checks | `scripts/release` | Enforces git tag ↔ `ravyn.__version__` match |

## CODE MAP
| Symbol/Area | Type | Location | Refs | Role |
|---|---|---|---:|---|
| `run_cli()` | function | `ravyn/__main__.py` | high | CLI entrypoint for `ravyn` script |
| `ravyn_cli` | Sayer app | `ravyn/core/directives/cli.py` | high | Native/custom directive registry |
| `Router` internals | class cluster | `ravyn/routing/router.py` | very high | Route normalization, include, lifecycle, permissions |
| `get_openapi()` | function | `ravyn/openapi/openapi.py` | high | OpenAPI document assembly |
| `RavynSettings` | class | `ravyn/conf/global_settings.py` | high | Global defaults, docs/security/runtime toggles |
| `Token` (JWT) | model | `ravyn/security/jwt/token.py` | medium | JWT encode/decode payload model |

## CONVENTIONS (project-specific)
- Python-first single package; no monorepo workspace boundaries.
- Ruff line length `99`, selected rule families: `E,W,F,C,B,I`.
- `pytest` strict flags enabled: `--strict-config`, `--strict-markers`, `xfail_strict=true`.
- Type-check command is `ty` via hatch (`hatch run test:check_types`).
- Test runs assume `RAVYN_SETTINGS_MODULE=tests.settings.AppTestSettings`.
- Docs build is custom pipeline; do not treat as plain MkDocs-only project.

## ANTI-PATTERNS (THIS PROJECT)
- Do not push release tags that do not match `ravyn/__init__.py::__version__`.
- Do not modify public package surface (`ravyn/`, CLI, scripts) without corresponding docs updates (`docs-guard` fails).
- Never use blocking I/O in middleware paths.
- Never store plaintext passwords; always hash (documented security policy).
- Do not rely on deprecated `BaseAuthMiddleware` for new code.

## UNIQUE STYLES
- Directive system supports class-based and Sayer function-based custom directives via `operations/*.py` discovery.
- Docs source is split: prose in `docs/<lang>/docs`, runnable snippets in `docs_src/`, merged into `docs/<lang>/generated`.
- OpenAPI is internally generated (Pydantic-backed), not external codegen.

## COMMANDS
```bash
hatch run lint
hatch run test:check_types
hatch run test:test
hatch run docs:build
task test
./scripts/release
```

## NOTES
- CI test matrix uses Python 3.10–3.14 with postgres/mongo/redis services.
- Publish workflow requires `PYPI_TOKEN` and `DEPLOY_DOCS` secrets.
- Favor nearest subdirectory `AGENTS.md` before editing deep modules.
