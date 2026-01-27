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


def _run_asserts(names: list[str] | None = None):
    if names is None:
        assert os.path.isfile("myapp/__init__.py") is True
        assert os.path.isfile("myapp/tests.py") is True
        assert os.path.isfile("myapp/v1/__init__.py") is True
        assert os.path.isfile("myapp/v1/schemas.py") is True
        assert os.path.isfile("myapp/v1/urls.py") is True
        assert os.path.isfile("myapp/v1/controllers.py") is True
        assert os.path.isfile("myapp/directives/__init__.py") is True
        assert os.path.isfile("myapp/directives/operations/__init__.py") is True
    else:
        for name in names:
            assert os.path.isfile(f"{name}/__init__.py") is True
            assert os.path.isfile(f"{name}/tests.py") is True
            assert os.path.isfile(f"{name}/v1/__init__.py") is True
            assert os.path.isfile(f"{name}/v1/schemas.py") is True
            assert os.path.isfile(f"{name}/v1/urls.py") is True
            assert os.path.isfile(f"{name}/v1/controllers.py") is True
            assert os.path.isfile(f"{name}/directives/__init__.py") is True
            assert os.path.isfile(f"{name}/directives/operations/__init__.py") is True


def test_create_app_with_env_var(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "ravyn createproject myproject")
    assert ss == 0

    os.chdir("myproject/myproject/apps")

    (o, e, ss) = run_cmd("tests.cli.main:app", "ravyn createapp myapp")

    _run_asserts()


def test_create_app_without_env_var(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "ravyn createproject myproject", is_app=False)
    assert ss == 0

    os.chdir("myproject/myproject/apps")

    (o, e, ss) = run_cmd("tests.cli.main:app", "ravyn createapp myapp", is_app=False)

    _run_asserts()


def test_create_app_without_env_var_with_app_flag(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "ravyn createproject myproject", is_app=False)
    assert ss == 0

    os.chdir("myproject/myproject/apps")

    (o, e, ss) = run_cmd(
        "tests.cli.main:app", "ravyn --app tests.cli.main:app createapp myapp", is_app=False
    )

    _run_asserts()


def test_create_multiple_apps_without_env_var_with_app_flag(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "ravyn createproject myproject", is_app=False)
    assert ss == 0

    os.chdir("myproject/myproject/apps")

    (o, e, ss) = run_cmd(
        "tests.cli.main:app",
        "ravyn --app tests.cli.main:app createapp myapp another multiple",
        is_app=False,
    )

    _run_asserts(["myapp", "another", "multiple"])
