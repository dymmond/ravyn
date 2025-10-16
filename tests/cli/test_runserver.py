import builtins
import os
import shutil
import sys
import types

import click
import pytest

from ravyn import Ravyn
from ravyn.core.directives.operations import runserver as runserver_module
from tests.cli.utils import run_cmd

app = Ravyn(routes=[])


@pytest.fixture(scope="module")
def create_folders():
    os.chdir(os.path.split(os.path.abspath(__file__))[0])
    try:
        os.remove("app.db")
    except OSError:
        pass
    try:
        shutil.rmtree("myproject")

    except OSError:
        pass
    try:
        shutil.rmtree("temp_folder")
    except OSError:
        pass

    yield

    try:
        os.remove("app.db")
    except OSError:
        pass
    try:
        shutil.rmtree("myproject")

    except OSError:
        pass
    try:
        shutil.rmtree("temp_folder")
    except OSError:
        pass


@pytest.mark.anyio
async def test_runserver_uses_cli_path(monkeypatch):
    """
    Ensures that runserver uses the CLI `path` argument when provided
    and calls uvicorn.run() with correct parameters.
    """
    (o, e, ss) = run_cmd("tests.cli.main:app", "ravyn createproject myproject")
    assert ss == 0

    called = {}

    def fake_run(**kwargs):
        called.update(kwargs)
        return None  # don't block

    monkeypatch.setenv("RAVYN_DEFAULT_APP", "")

    fake_uvicorn = types.SimpleNamespace(run=fake_run)
    sys.modules["uvicorn"] = fake_uvicorn

    os.environ.pop("RAVYN_DEFAULT_APP", None)

    env = runserver_module.DirectiveEnv()
    env.app = app
    env.path = "tests.cli.main:app"
    env.ravyn_app = app
    env.command_path = "tests.cli.main:app"
    env.module_info = type(
        "M",
        (),
        {
            "module_paths": [],
            "discovery_file": "serve.py",
            "module_import": ("tests.cli.main", "app"),
        },
    )()

    ctx = click.Context(runserver_module.runserver)
    ctx.obj = env
    click.globals._local.stack = [ctx]

    # Directly invoke the command
    runserver_module.runserver.callback(
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
    assert called["app"] == app
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
        runserver_module.runserver.callback(path=None)
    assert exc.value.code == 1


def test_runserver_sets_custom_settings(monkeypatch):
    called = {}

    def fake_run(**kwargs):
        called.update(kwargs)
        return None

    sys.modules["uvicorn"] = types.SimpleNamespace(run=fake_run)
    monkeypatch.delenv("RAVYN_SETTINGS_MODULE", raising=False)

    env = runserver_module.DirectiveEnv()
    env.app = app
    env.path = "tests.cli.main:app"
    env.ravyn_app = app
    env.command_path = "tests.cli.main:app"
    env.module_info = type(
        "M",
        (),
        {
            "module_paths": [],
            "discovery_file": "serve.py",
            "module_import": ("tests.cli.main", "app"),
        },
    )()

    ctx = click.Context(runserver_module.runserver)
    ctx.obj = env
    click.globals._local.stack = [ctx]

    runserver_module.runserver.callback(
        path="tests.cli.main:app", settings="tests.settings.CustomSettings"
    )

    assert os.environ["RAVYN_SETTINGS_MODULE"] == "tests.settings.CustomSettings"
    assert called


def test_runserver_uses_default_settings(monkeypatch):
    def fake_run(**_):
        return None

    sys.modules["uvicorn"] = types.SimpleNamespace(run=fake_run)

    class FakeSettings:
        __class__ = type("Settings", (), {"__module__": "ravyn.conf.default"})

    monkeypatch.setitem(sys.modules, "ravyn.conf", types.SimpleNamespace(settings=FakeSettings()))

    env = runserver_module.DirectiveEnv()
    env.app = app
    env.path = "tests.cli.main:app"
    env.ravyn_app = app
    env.command_path = "tests.cli.main:app"
    env.module_info = type(
        "M",
        (),
        {
            "module_paths": [],
            "discovery_file": "serve.py",
            "module_import": ("tests.cli.main", "app"),
        },
    )()

    ctx = click.Context(runserver_module.runserver)
    ctx.obj = env
    click.globals._local.stack = [ctx]

    runserver_module.runserver.callback(path="tests.cli.main:app")


def test_runserver_raises_directive_error_if_uvicorn_missing(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, *a, **kw):
        if name == "uvicorn":
            raise ImportError()
        return original_import(name, *a, **kw)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    env = runserver_module.DirectiveEnv()
    env.app = app
    env.path = "tests.cli.main:app"
    env.ravyn_app = app
    env.command_path = "tests.cli.main:app"
    env.module_info = type(
        "M",
        (),
        {
            "module_paths": [],
            "discovery_file": "serve.py",
            "module_import": ("tests.cli.main", "app"),
        },
    )()

    ctx = click.Context(runserver_module.runserver)
    ctx.obj = env
    click.globals._local.stack = [ctx]

    with pytest.raises(runserver_module.DirectiveError):
        runserver_module.runserver.callback(path="tests.cli.main:app")


def test_runserver_uses_env_path(monkeypatch):
    called = {}

    def fake_run(**kwargs):
        called.update(kwargs)
        return None

    sys.modules["uvicorn"] = types.SimpleNamespace(run=fake_run)

    env = runserver_module.DirectiveEnv()
    env.app = app
    env.path = "tests.cli.main:app"
    env.ravyn_app = app
    env.module_info = type(
        "M",
        (),
        {
            "module_paths": [],
            "discovery_file": "serve.py",
            "module_import": ("tests.cli.main", "app"),
        },
    )()
    ctx = click.Context(runserver_module.runserver)
    ctx.obj = env
    click.globals._local.stack = [ctx]

    runserver_module.runserver.callback(path=None)

    assert called["app"] == app


def test_runserver_exits_if_no_path(monkeypatch):
    env = runserver_module.DirectiveEnv()
    env.app = app
    env.path = None

    env.module_info = type(
        "M",
        (),
        {
            "module_paths": [],
            "discovery_file": "serve.py",
            "module_import": ("tests.cli.main", "app"),
        },
    )()

    ctx = click.Context(runserver_module.runserver)
    ctx.obj = env
    click.globals._local.stack = [ctx]

    monkeypatch.setattr(runserver_module, "error", lambda *a, **kw: None)
    monkeypatch.setattr(sys, "exit", lambda code: (_ for _ in ()).throw(SystemExit(code)))

    with pytest.raises(SystemExit):
        runserver_module.runserver.callback(path=None)


def test_runserver_with_reload_or_workers(monkeypatch):
    called = {}
    sys.modules["uvicorn"] = types.SimpleNamespace(run=lambda **kw: called.update(kw))

    env = runserver_module.DirectiveEnv()
    env.app = app
    env.path = "tests.cli.main:app"
    env.module_info = type(
        "M",
        (),
        {
            "module_paths": [],
            "discovery_file": "serve.py",
            "module_import": ("tests.cli.main", "app"),
        },
    )()
    env.ravyn_app = app
    ctx = click.Context(runserver_module.runserver)
    ctx.obj = env
    click.globals._local.stack = [ctx]

    runserver_module.runserver.callback(path="tests.cli.main:app", reload=True)

    # When reload=True, it should use string path, not app object
    assert called["app"] == "tests.cli.main:app"
