import os
import shutil

import pytest

from ravyn import Ravyn
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
        shutil.rmtree("simple/myproject")
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
        shutil.rmtree("simple/myproject")
    except OSError:
        pass
    try:
        shutil.rmtree("temp_folder")
    except OSError:
        pass


def test_create_project(create_folders):
    (o, e, ss) = run_cmd(
        "tests.cli.main:app",
        "ravyn createproject myproject --with-deployment --deployment-folder-name deploy --simple",
    )
    assert ss == 0

    with open("myproject/.gitignore") as f:
        assert f.readline().strip() == "# Byte-compiled / optimized / DLL files"
    with open("myproject/myproject/app.py") as f:
        assert """__name__""" in f.read()


def _run_asserts():
    assert os.path.isfile("myproject/Taskfile.yaml") is True
    assert os.path.isfile("myproject/README.md") is True

    # Deployment
    assert os.path.isfile("myproject/deploy/docker/Dockerfile") is True
    assert os.path.isfile("myproject/deploy/gunicorn/gunicorn_conf.py") is True
    assert os.path.isfile("myproject/deploy/nginx/nginx.conf") is True
    assert os.path.isfile("myproject/deploy/nginx/nginx.json-logging.conf") is True
    assert os.path.isfile("myproject/deploy/supervisor/supervisord.conf") is True

    # General
    assert os.path.isfile("myproject/.gitignore") is True
    assert os.path.isfile("myproject/myproject/__init__.py") is True
    assert os.path.isfile("myproject/myproject/app.py") is True
    assert os.path.isfile("myproject/myproject/tests/__init__.py") is True
    assert os.path.isfile("myproject/myproject/tests/test_app.py") is True
    assert os.path.isfile("myproject/pyproject.toml") is True


def test_create_project_files_with_env_var(create_folders):
    (o, e, ss) = run_cmd(
        "tests.cli.main:app",
        "ravyn createproject myproject --with-deployment --deployment-folder-name deploy --simple",
    )
    assert ss == 0

    _run_asserts()


def test_create_project_files_without_env_var(create_folders):
    (o, e, ss) = run_cmd(
        "tests.cli.main:app",
        "ravyn createproject myproject --with-deployment --deployment-folder-name deploy --simple",
        is_app=False,
    )
    assert ss == 0

    _run_asserts()


def test_create_project_files_without_env_var_and_with_app_flag(create_folders):
    (o, e, ss) = run_cmd(
        "tests.cli.main:app",
        "ravyn --app tests.cli.main:app createproject myproject --with-deployment --deployment-folder-name deploy --simple",
        is_app=False,
    )
    assert ss == 0

    _run_asserts()
