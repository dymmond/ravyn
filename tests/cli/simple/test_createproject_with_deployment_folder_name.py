from pathlib import Path

from ravyn import Ravyn
from tests.cli.utils import run_cmd

app = Ravyn(routes=[])


def test_create_project(cli_tmp_dir: Path):
    (o, e, ss) = run_cmd(
        "tests.cli.main:app",
        "ravyn createproject myproject --with-deployment --deployment-folder-name deploy --simple",
    )
    assert ss == 0

    with open("myproject/.gitignore") as f:
        assert f.readline().strip() == "# Byte-compiled / optimized / DLL files"
    with open("myproject/myproject/app.py") as f:
        assert """__name__""" in f.read()


def _run_asserts(base_dir: Path):
    assert (base_dir / "myproject/Taskfile.yaml").is_file() is True
    assert (base_dir / "myproject/README.md").is_file() is True

    # Deployment
    assert (base_dir / "myproject/deploy/docker/Dockerfile").is_file() is True
    assert (base_dir / "myproject/deploy/gunicorn/gunicorn_conf.py").is_file() is True
    assert (base_dir / "myproject/deploy/nginx/nginx.conf").is_file() is True
    assert (base_dir / "myproject/deploy/nginx/nginx.json-logging.conf").is_file() is True
    assert (base_dir / "myproject/deploy/supervisor/supervisord.conf").is_file() is True

    # General
    assert (base_dir / "myproject/.gitignore").is_file() is True
    assert (base_dir / "myproject/myproject/__init__.py").is_file() is True
    assert (base_dir / "myproject/myproject/app.py").is_file() is True
    assert (base_dir / "myproject/myproject/tests/__init__.py").is_file() is True
    assert (base_dir / "myproject/myproject/tests/test_app.py").is_file() is True
    assert (base_dir / "myproject/pyproject.toml").is_file() is True


def test_create_project_files_with_env_var(cli_tmp_dir: Path):
    (o, e, ss) = run_cmd(
        "tests.cli.main:app",
        "ravyn createproject myproject --with-deployment --deployment-folder-name deploy --simple",
    )
    assert ss == 0

    _run_asserts(cli_tmp_dir)


def test_create_project_files_without_env_var(cli_tmp_dir: Path):
    (o, e, ss) = run_cmd(
        "tests.cli.main:app",
        "ravyn createproject myproject --with-deployment --deployment-folder-name deploy --simple",
        is_app=False,
    )
    assert ss == 0

    _run_asserts(cli_tmp_dir)


def test_create_project_files_without_env_var_and_with_app_flag(cli_tmp_dir: Path):
    (o, e, ss) = run_cmd(
        "tests.cli.main:app",
        "ravyn --app tests.cli.main:app createproject myproject --with-deployment --deployment-folder-name deploy --simple",
        is_app=False,
    )
    assert ss == 0

    _run_asserts(cli_tmp_dir)
