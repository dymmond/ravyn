# DIRECTIVES DOMAIN KNOWLEDGE BASE

## OVERVIEW
Sayer-based CLI subsystem. Supports native directives plus project-local custom directives discovered from `operations/*.py`.

## WHERE TO LOOK
| Need | Location | Notes |
|---|---|---|
| CLI registration | `cli.py` | Native commands + custom command injection |
| CLI group runtime | `groups.py` | Environment injection + invocation flow |
| App discovery/runtime env | `env.py` | App/module discovery and loading |
| Directive discovery utils | `utils.py` | File scanning + custom directive loading |
| Directive decorator | `decorator.py` | Marks callable custom directives |
| Built-in operations | `operations/` | run/runserver/create*/shell/list/show_urls |

## CONVENTIONS (DELTA)
- Custom directives live in project `operations/` and must be discoverable as `.py` modules.
- Function-style custom directives must be marked for discovery (`@directive(...)`).
- Runtime behavior depends on app context (`--app` / env-based discovery) for custom runs.

## ANTI-PATTERNS
- Do not break directive discovery fallback chain (`app.py`, `main.py`, etc.) casually.
- Do not change argv position logic in `operations/run.py` without CLI integration tests.
- Do not silently swallow custom directive load errors in new code paths.

## REQUIRED TEST FOCUS
```bash
hatch run test:test tests/cli
```
