import os
import shlex
from pathlib import Path

from ravyn import Ravyn

app = Ravyn(routes=[])


def _run_cmd(safe_run_cmd, cmd: str, is_app: bool = True, **kwargs):
    if is_app:
        os.environ["RAVYN_DEFAULT_APP"] = "tests.cli.main:app"
    process = safe_run_cmd(shlex.split(cmd), **kwargs)
    return process.stdout, process.stderr, process.returncode


def _run_asserts(base_dir: Path, names: list[str] | None = None):
    if names is None:
        assert (base_dir / "myapp/__init__.py").is_file() is True
        assert (base_dir / "myapp/tests.py").is_file() is True
        assert (base_dir / "myapp/v1/__init__.py").is_file() is True
        assert (base_dir / "myapp/v1/schemas.py").is_file() is True
        assert (base_dir / "myapp/v1/urls.py").is_file() is True
        assert (base_dir / "myapp/v1/controllers.py").is_file() is True
        assert (base_dir / "myapp/directives/__init__.py").is_file() is True
        assert (base_dir / "myapp/directives/operations/__init__.py").is_file() is True
    else:
        for name in names:
            assert (base_dir / f"{name}/__init__.py").is_file() is True
            assert (base_dir / f"{name}/tests.py").is_file() is True
            assert (base_dir / f"{name}/v1/__init__.py").is_file() is True
            assert (base_dir / f"{name}/v1/schemas.py").is_file() is True
            assert (base_dir / f"{name}/v1/urls.py").is_file() is True
            assert (base_dir / f"{name}/v1/controllers.py").is_file() is True
            assert (base_dir / f"{name}/directives/__init__.py").is_file() is True
            assert (base_dir / f"{name}/directives/operations/__init__.py").is_file() is True


def test_create_app_with_env_var(cli_tmp_dir: Path, safe_run_cmd):
    (o, e, ss) = _run_cmd(safe_run_cmd, "ravyn createproject myproject")
    assert ss == 0

    apps_dir = cli_tmp_dir / "myproject/myproject/apps"

    (o, e, ss) = _run_cmd(safe_run_cmd, "ravyn createapp myapp", cwd=apps_dir)

    _run_asserts(apps_dir)


def test_create_app_without_env_var(cli_tmp_dir: Path, safe_run_cmd):
    (o, e, ss) = _run_cmd(safe_run_cmd, "ravyn createproject myproject", is_app=False)
    assert ss == 0

    apps_dir = cli_tmp_dir / "myproject/myproject/apps"

    (o, e, ss) = _run_cmd(safe_run_cmd, "ravyn createapp myapp", is_app=False, cwd=apps_dir)

    _run_asserts(apps_dir)


def test_create_app_without_env_var_with_app_flag(cli_tmp_dir: Path, safe_run_cmd):
    (o, e, ss) = _run_cmd(safe_run_cmd, "ravyn createproject myproject", is_app=False)
    assert ss == 0

    apps_dir = cli_tmp_dir / "myproject/myproject/apps"

    (o, e, ss) = _run_cmd(
        safe_run_cmd,
        "ravyn --app tests.cli.main:app createapp myapp",
        is_app=False,
        cwd=apps_dir,
    )

    _run_asserts(apps_dir)


def test_create_multiple_apps_without_env_var_with_app_flag(cli_tmp_dir: Path, safe_run_cmd):
    (o, e, ss) = _run_cmd(safe_run_cmd, "ravyn createproject myproject", is_app=False)
    assert ss == 0

    apps_dir = cli_tmp_dir / "myproject/myproject/apps"

    (o, e, ss) = _run_cmd(
        safe_run_cmd,
        "ravyn --app tests.cli.main:app createapp myapp another multiple",
        is_app=False,
        cwd=apps_dir,
    )

    _run_asserts(apps_dir, ["myapp", "another", "multiple"])
