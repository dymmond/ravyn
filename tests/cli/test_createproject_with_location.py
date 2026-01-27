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
        shutil.rmtree("auto")

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
        shutil.rmtree("auto")

    except OSError:
        pass
    try:
        shutil.rmtree("temp_folder")
    except OSError:
        pass


def test_create_project_with_structure(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "ravyn createproject myproject --location ./auto")
    assert ss == 0

    with open("auto/myproject/.gitignore") as f:
        assert f.readline().strip() == "# Byte-compiled / optimized / DLL files"
    with open("auto/myproject/myproject/urls.py") as f:
        assert f.readline().strip() == '"""myproject Routes Configuration'


def _run_asserts():
    assert os.path.isfile("auto/myproject/Taskfile.yaml") is True
    assert os.path.isfile("auto/myproject/README.md") is True
    assert os.path.isfile("auto/myproject/.gitignore") is True
    assert os.path.isfile("auto/myproject/myproject/__init__.py") is True
    assert os.path.isfile("auto/myproject/myproject/main.py") is True
    assert os.path.isfile("auto/myproject/myproject/serve.py") is True
    assert os.path.isfile("auto/myproject/myproject/urls.py") is True
    assert os.path.isfile("auto/myproject/myproject/tests/__init__.py") is True
    assert os.path.isfile("auto/myproject/myproject/tests/test_app.py") is True
    assert os.path.isfile("auto/myproject/myproject/configs/__init__.py") is True
    assert os.path.isfile("auto/myproject/myproject/configs/settings.py") is True
    assert os.path.isfile("auto/myproject/myproject/configs/development/__init__.py") is True
    assert os.path.isfile("auto/myproject/myproject/configs/development/settings.py") is True
    assert os.path.isfile("auto/myproject/myproject/configs/testing/__init__.py") is True
    assert os.path.isfile("auto/myproject/myproject/configs/testing/settings.py") is True
    assert os.path.isfile("auto/myproject/myproject/apps/__init__.py") is True
    assert os.path.isfile("auto/myproject/requirements/base.txt") is True
    assert os.path.isfile("auto/myproject/requirements/testing.txt") is True
    assert os.path.isfile("auto/myproject/requirements/development.txt") is True


def test_create_project_files_with_env_var(create_folders):
    (o, e, ss) = run_cmd(
        "tests.cli.main:app",
        "ravyn createproject myproject  --location ./auto",
    )
    assert ss == 0

    _run_asserts()


def test_create_project_files_without_env_var(create_folders):
    (o, e, ss) = run_cmd(
        "tests.cli.main:app",
        "ravyn createproject myproject --location ./auto",
        is_app=False,
    )
    assert ss == 0

    _run_asserts()


def test_create_project_files_without_env_var_and_with_app_flag(create_folders):
    (o, e, ss) = run_cmd(
        "tests.cli.main:app",
        "ravyn --app tests.cli.main:app createproject myproject --location ./auto",
        is_app=False,
    )
    assert ss == 0

    _run_asserts()
