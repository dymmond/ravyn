import os
import shlex
from pathlib import Path

from ravyn import Ravyn

app = Ravyn(routes=[])


def _run_cmd(safe_run_cmd, app: str, cmd: str, is_app: bool = True, cwd: Path | None = None):
    if is_app:
        os.environ["RAVYN_DEFAULT_APP"] = app
    process = safe_run_cmd(shlex.split(cmd), cwd=cwd, env=dict(os.environ))
    return process.stdout, process.stderr, process.returncode


def _run_asserts(base_dir: Path):
    assert (base_dir / "deploy/docker/Dockerfile").is_file() is True
    assert (base_dir / "deploy/gunicorn/gunicorn_conf.py").is_file() is True
    assert (base_dir / "deploy/nginx/nginx.conf").is_file() is True
    assert (base_dir / "deploy/nginx/nginx.json-logging.conf").is_file() is True
    assert (base_dir / "deploy/supervisor/supervisord.conf").is_file() is True


def test_create_app_with_env_var(cli_tmp_dir: Path, safe_run_cmd):
    (o, e, ss) = _run_cmd(
        safe_run_cmd,
        "tests.cli.main:app",
        "ravyn createdeployment myproject --deployment-folder-name deploy",
    )
    assert ss == 0

    _run_asserts(cli_tmp_dir)


def test_create_app_without_env_var(cli_tmp_dir: Path, safe_run_cmd):
    (o, e, ss) = _run_cmd(
        safe_run_cmd,
        "tests.cli.main:app",
        "ravyn createdeployment myproject --deployment-folder-name deploy",
        is_app=False,
    )
    assert ss == 0

    _run_asserts(cli_tmp_dir)


def test_create_app_without_env_var_with_app_flag(cli_tmp_dir: Path, safe_run_cmd):
    (o, e, ss) = _run_cmd(
        safe_run_cmd,
        "tests.cli.main:app",
        "ravyn --app tests.cli.main:app createdeployment myproject --deployment-folder-name deploy",
        is_app=False,
    )
    assert ss == 0

    _run_asserts(cli_tmp_dir)
