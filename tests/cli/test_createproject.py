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


def test_create_project(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "ravyn createproject myproject")
    assert ss == 0

    with open("myproject/.gitignore") as f:
        assert f.readline().strip() == "# Byte-compiled / optimized / DLL files"
    with open("myproject/myproject/urls.py") as f:
        assert f.readline().strip() == '"""myproject Routes Configuration'


def _run_asserts(names: list[str] | None = None):
    if names is None:
        assert os.path.isfile("myproject/Taskfile.yaml") is True
        assert os.path.isfile("myproject/README.md") is True
        assert os.path.isfile("myproject/.gitignore") is True
        assert os.path.isfile("myproject/myproject/__init__.py") is True
        assert os.path.isfile("myproject/myproject/main.py") is True
        assert os.path.isfile("myproject/myproject/serve.py") is True
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
        assert os.path.isfile("myproject/requirements/base.txt") is True
        assert os.path.isfile("myproject/requirements/testing.txt") is True
        assert os.path.isfile("myproject/requirements/development.txt") is True
    else:
        for name in names:
            assert os.path.isfile(f"{name}/Taskfile.yaml") is True
            assert os.path.isfile(f"{name}/README.md") is True
            assert os.path.isfile(f"{name}/.gitignore") is True
            assert os.path.isfile(f"{name}/{name}/__init__.py") is True
            assert os.path.isfile(f"{name}/{name}/main.py") is True
            assert os.path.isfile(f"{name}/{name}/serve.py") is True
            assert os.path.isfile(f"{name}/{name}/urls.py") is True
            assert os.path.isfile(f"{name}/{name}/tests/__init__.py") is True
            assert os.path.isfile(f"{name}/{name}/tests/test_app.py") is True
            assert os.path.isfile(f"{name}/{name}/configs/__init__.py") is True
            assert os.path.isfile(f"{name}/{name}/configs/settings.py") is True
            assert os.path.isfile(f"{name}/{name}/configs/development/__init__.py") is True
            assert os.path.isfile(f"{name}/{name}/configs/development/settings.py") is True
            assert os.path.isfile(f"{name}/{name}/configs/testing/__init__.py") is True
            assert os.path.isfile(f"{name}/{name}/configs/testing/settings.py") is True
            assert os.path.isfile(f"{name}/{name}/apps/__init__.py") is True
            assert os.path.isfile(f"{name}/requirements/base.txt") is True
            assert os.path.isfile(f"{name}/requirements/testing.txt") is True
            assert os.path.isfile(f"{name}/requirements/development.txt") is True


def test_create_project_files_with_env_var(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "ravyn createproject myproject")
    assert ss == 0

    _run_asserts()


def test_create_project_files_without_env_var(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "ravyn createproject myproject", is_app=False)
    assert ss == 0

    _run_asserts()


def test_create_project_files_without_env_var_and_with_app_flag(create_folders):
    (o, e, ss) = run_cmd(
        "tests.cli.main:app",
        "ravyn --app tests.cli.main:app createproject myproject another multiple",
        is_app=False,
    )
    assert ss == 0

    _run_asserts(["myproject", "another", "multiple"])
