import builtins
import os
import shlex
import sys
import types
from pathlib import Path
from typing import Any

import click  # type: ignore[import-not-found]
import pytest  # type: ignore[import-not-found]

from ravyn import Ravyn
from ravyn.core.directives.operations import runserver as runserver_module

app = Ravyn(routes=[])


def _run_cmd(monkeypatch: pytest.MonkeyPatch, safe_run_cmd, app_ref: str, cmd: str):
    monkeypatch.setenv("RAVYN_DEFAULT_APP", app_ref)
    process = safe_run_cmd(shlex.split(cmd))
    return process.stdout, process.stderr, process.returncode


def _module_info() -> Any:
    return type(
        "M",
        (),
        {
            "module_paths": [],
            "discovery_file": "serve.py",
            "module_import": ("tests.cli.main", "app"),
        },
    )()


def _install_fake_palfrey(fake_run) -> None:
    fake_module = types.ModuleType("palfrey")
    fake_module.run = fake_run  # type: ignore[attr-defined]
    sys.modules["palfrey"] = fake_module


def _runserver_callback(**kwargs: Any) -> None:
    callback: Any = runserver_module.runserver.callback
    callback(**kwargs)


@pytest.mark.anyio
async def test_runserver_uses_cli_path(
    monkeypatch: pytest.MonkeyPatch, cli_tmp_dir: Path, safe_run_cmd
):
    """
    Ensures that runserver uses the CLI `path` argument when provided
    and calls palfrey.run() with correct parameters.
    """
    (cli_tmp_dir / "main.py").write_text(
        "from ravyn import Ravyn\n\napp = Ravyn(routes=[])\n",
        encoding="utf-8",
    )
    (o, e, ss) = _run_cmd(monkeypatch, safe_run_cmd, "main:app", "ravyn createproject myproject")
    assert ss == 0

    called = {}

    def fake_run(**kwargs):
        called.update(kwargs)
        return None  # don't block

    monkeypatch.setenv("RAVYN_DEFAULT_APP", "")

    _install_fake_palfrey(fake_run)

    os.environ.pop("RAVYN_DEFAULT_APP", None)

    env = runserver_module.DirectiveEnv()
    env.app = app
    env.path = "tests.cli.main:app"
    env.ravyn_app = app
    env.command_path = "tests.cli.main:app"
    env.module_info = _module_info()

    ctx = click.Context(runserver_module.runserver)
    ctx.obj = env
    click.globals._local.stack = [ctx]

    # Directly invoke the command
    _runserver_callback(
        path="tests.cli.main:app",
        port=9000,
        reload=False,
        host="127.0.0.1",
        debug=True,
        log_level="info",
        lifespan="on",
        settings=None,
        proxy_headers=True,
        workers=None,
    )

    assert called
    assert called["config_or_app"] == app
    assert called["port"] == 9000
    assert called["host"] == "127.0.0.1"
    assert called["reload"] is False
    assert called["workers"] is None
    assert "log_config" in called


def test_runserver_exits_if_no_app(monkeypatch):
    ctx = click.Context(runserver_module.runserver)
    env = runserver_module.DirectiveEnv()
    ctx.obj = env
    click.globals._local.stack = [ctx]

    monkeypatch.setattr(runserver_module, "error", lambda *a, **kw: None)
    monkeypatch.setattr(sys, "exit", lambda code: (_ for _ in ()).throw(SystemExit(code)))

    with pytest.raises(SystemExit) as exc:
        _runserver_callback(path=None)
    assert exc.value.code == 1


def test_runserver_sets_custom_settings(monkeypatch):
    called = {}

    def fake_run(**kwargs):
        called.update(kwargs)
        return None

    _install_fake_palfrey(fake_run)
    monkeypatch.delenv("RAVYN_SETTINGS_MODULE", raising=False)

    env = runserver_module.DirectiveEnv()
    env.app = app
    env.path = "tests.cli.main:app"
    env.ravyn_app = app
    env.command_path = "tests.cli.main:app"
    env.module_info = _module_info()

    ctx = click.Context(runserver_module.runserver)
    ctx.obj = env
    click.globals._local.stack = [ctx]

    _runserver_callback(path="tests.cli.main:app", settings="tests.settings.CustomSettings")

    assert os.environ["RAVYN_SETTINGS_MODULE"] == "tests.settings.CustomSettings"
    assert called


def test_runserver_uses_default_settings(monkeypatch):
    def fake_run(**_):
        return None

    _install_fake_palfrey(fake_run)

    class FakeSettings:
        pass

    FakeSettings.__module__ = "ravyn.conf.default"

    fake_conf = types.ModuleType("ravyn.conf")
    fake_conf.settings = FakeSettings()  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "ravyn.conf", fake_conf)

    env = runserver_module.DirectiveEnv()
    env.app = app
    env.path = "tests.cli.main:app"
    env.ravyn_app = app
    env.command_path = "tests.cli.main:app"
    env.module_info = _module_info()

    ctx = click.Context(runserver_module.runserver)
    ctx.obj = env
    click.globals._local.stack = [ctx]

    _runserver_callback(path="tests.cli.main:app")


def test_runserver_raises_directive_error_if_uvicorn_missing(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, *a, **kw):
        if name == "palfrey":
            raise ImportError()
        return original_import(name, *a, **kw)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    env = runserver_module.DirectiveEnv()
    env.app = app
    env.path = "tests.cli.main:app"
    env.ravyn_app = app
    env.command_path = "tests.cli.main:app"
    env.module_info = _module_info()

    ctx = click.Context(runserver_module.runserver)
    ctx.obj = env
    click.globals._local.stack = [ctx]

    with pytest.raises(runserver_module.DirectiveError):
        _runserver_callback(path="tests.cli.main:app")


def test_runserver_uses_env_path(monkeypatch):
    called = {}

    def fake_run(**kwargs):
        called.update(kwargs)
        return None

    _install_fake_palfrey(fake_run)

    env = runserver_module.DirectiveEnv()
    env.app = app
    env.path = "tests.cli.main:app"
    env.ravyn_app = app
    env.module_info = _module_info()
    ctx = click.Context(runserver_module.runserver)
    ctx.obj = env
    click.globals._local.stack = [ctx]

    _runserver_callback(path=None)

    assert called["config_or_app"] == app


def test_runserver_exits_if_no_path(monkeypatch):
    env = runserver_module.DirectiveEnv()
    env.app = app
    env.path = None

    env.module_info = _module_info()

    ctx = click.Context(runserver_module.runserver)
    ctx.obj = env
    click.globals._local.stack = [ctx]

    monkeypatch.setattr(runserver_module, "error", lambda *a, **kw: None)
    monkeypatch.setattr(sys, "exit", lambda code: (_ for _ in ()).throw(SystemExit(code)))

    with pytest.raises(SystemExit):
        _runserver_callback(path=None)


def test_runserver_with_reload_or_workers(monkeypatch):
    called = {}
    _install_fake_palfrey(lambda **kw: called.update(kw))

    env = runserver_module.DirectiveEnv()
    env.app = app
    env.path = "tests.cli.main:app"
    env.module_info = _module_info()
    env.ravyn_app = app
    ctx = click.Context(runserver_module.runserver)
    ctx.obj = env
    click.globals._local.stack = [ctx]

    _runserver_callback(path="tests.cli.main:app", reload=True)

    # When reload=True, it should use string path, not app object
    assert called["config_or_app"] == "tests.cli.main:app"
