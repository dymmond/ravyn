import os
import shlex
from pathlib import Path

import pytest  # type: ignore[import-not-found]

from ravyn import Ravyn

app = Ravyn(routes=[])


def _run_cmd(
    cli_tmp_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
    safe_run_cmd,
    app_ref: str,
    cmd: str,
    is_app: bool = True,
):
    if is_app:
        monkeypatch.setenv("RAVYN_DEFAULT_APP", app_ref)
    cmd_list = shlex.split(cmd)
    process = safe_run_cmd(cmd_list, cwd=cli_tmp_dir)
    stdout = process.stdout
    stderr = process.stderr
    print("\n$ " + cmd)
    print(stdout)
    print(stderr)
    return stdout, stderr, process.returncode


def test_create_project(cli_tmp_dir: Path, safe_run_cmd, monkeypatch: pytest.MonkeyPatch):
    (o, e, ss) = _run_cmd(
        cli_tmp_dir,
        monkeypatch,
        safe_run_cmd,
        "tests.cli.main:app",
        "ravyn createproject myproject --edgy",
    )
    assert ss == 0

    with open("myproject/.gitignore") as f:
        assert f.readline().strip() == "# Byte-compiled / optimized / DLL files"
    with open("myproject/myproject/urls.py") as f:
        assert f.readline().strip() == '"""myproject Routes Configuration'


def _run_asserts():
    assert os.path.isfile("myproject/Taskfile.yaml") is True
    assert os.path.isfile("myproject/README.md") is True
    assert os.path.isfile("myproject/.gitignore") is True
    assert os.path.isfile("myproject/myproject/__init__.py") is True
    assert os.path.isfile("myproject/myproject/main.py") is True
    assert os.path.isfile("myproject/myproject/urls.py") is True
    assert os.path.isfile("myproject/myproject/tests/__init__.py") is True
    assert os.path.isfile("myproject/myproject/tests/test_app.py") is True
    assert os.path.isfile("myproject/myproject/configs/__init__.py") is True
    assert os.path.isfile("myproject/myproject/configs/settings.py") is True
    assert os.path.isfile("myproject/myproject/configs/development/__init__.py") is True
    assert os.path.isfile("myproject/myproject/configs/development/settings.py") is True
    assert os.path.isfile("myproject/myproject/configs/testing/__init__.py") is True
    assert os.path.isfile("myproject/myproject/configs/testing/settings.py") is True
    assert os.path.isfile("myproject/myproject/apps/__init__.py") is True
    assert os.path.isfile("myproject/myproject/core/__init__.py") is True
    assert os.path.isfile("myproject/myproject/core/models.py") is True
    assert os.path.isfile("myproject/pyproject.toml") is True


def test_create_project_files_with_env_var(
    cli_tmp_dir: Path, safe_run_cmd, monkeypatch: pytest.MonkeyPatch
):
    (o, e, ss) = _run_cmd(
        cli_tmp_dir,
        monkeypatch,
        safe_run_cmd,
        "tests.cli.main:app",
        "ravyn createproject myproject -e",
    )
    assert ss == 0

    _run_asserts()


def test_create_project_files_without_env_var(
    cli_tmp_dir: Path, safe_run_cmd, monkeypatch: pytest.MonkeyPatch
):
    (o, e, ss) = _run_cmd(
        cli_tmp_dir,
        monkeypatch,
        safe_run_cmd,
        "tests.cli.main:app",
        "ravyn createproject myproject --edgy",
        is_app=False,
    )
    assert ss == 0

    _run_asserts()


def test_create_project_files_without_env_var_and_with_app_flag(
    cli_tmp_dir: Path, safe_run_cmd, monkeypatch: pytest.MonkeyPatch
):
    (o, e, ss) = _run_cmd(
        cli_tmp_dir,
        monkeypatch,
        safe_run_cmd,
        "tests.cli.main:app",
        "ravyn --app tests.cli.main:app createproject myproject -e",
        is_app=False,
    )
    assert ss == 0

    _run_asserts()
