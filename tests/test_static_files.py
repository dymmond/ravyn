import os
import pathlib
from typing import Any

import pytest
from pydantic import ValidationError

from ravyn import Include, get
from ravyn.core.config import StaticFilesConfig
from ravyn.core.config.template import TemplateConfig
from ravyn.testclient import create_client


def test_staticfiles(tmpdir: str) -> None:
    path = tmpdir.join("test.txt")
    path.write("content")
    static_files_config = StaticFilesConfig(path="/static", directory=tmpdir)
    with create_client([], static_files_config=static_files_config) as client:
        response = client.get("/static/test.txt")
        assert response.status_code == 200
        assert response.text == "content"


def test_staticfiles_starlette(tmpdir, test_client_factory):
    path = os.path.join(tmpdir, "example.txt")
    with open(path, "w") as file:
        file.write("<file content>")

    static_files_config = StaticFilesConfig(path="/", directory=tmpdir)

    with create_client(routes=[], static_files_config=static_files_config) as client:
        response = client.get("/example.txt")
        assert response.status_code == 200
        assert response.text == "<file content>"


def test_staticfiles_with_pathlib(tmpdir, test_client_factory):
    base_dir = pathlib.Path(tmpdir)
    path = base_dir / "example.txt"
    with open(path, "w") as file:
        file.write("<file content>")

    static_files_config = StaticFilesConfig(path="/", directory=base_dir)
    with create_client(routes=[], static_files_config=static_files_config) as client:
        response = client.get("/example.txt")
        assert response.status_code == 200
        assert response.text == "<file content>"


def test_staticfiles_html(tmpdir: Any) -> None:
    path = tmpdir.join("index.html")
    path.write("content")
    static_files_config = StaticFilesConfig(path="/static", directory=tmpdir, html=True)
    with create_client([], static_files_config=static_files_config) as client:
        response = client.get("/static/index.html")
        assert response.status_code == 200
        assert response.text == "content"


def test_staticfiles_with_package(test_client_factory):
    static_files_config = StaticFilesConfig(path="/", packages=["tests"], html=True)
    with create_client([], static_files_config=static_files_config) as client:
        response = client.get("/example.txt")
        assert response.status_code == 200
        assert response.text == "123\n"


def test_staticfiles_for_slash_path(tmpdir: Any) -> None:
    path = tmpdir.join("text.txt")
    path.write("content")

    static_files_config = StaticFilesConfig(path="/", directory=tmpdir)
    with create_client([], static_files_config=static_files_config) as client:
        response = client.get("/text.txt")
        assert response.status_code == 200
        assert response.text == "content"


def test_config_validation(tmpdir: Any) -> None:
    path = tmpdir.join("text.txt")
    path.write("content")

    with pytest.raises(ValidationError):
        StaticFilesConfig(path="", directory=tmpdir)

    with pytest.raises(ValidationError):
        StaticFilesConfig(path="/{param:int}", directory=tmpdir)


def test_multiple_configs(tmpdir: Any) -> None:
    root1 = tmpdir.mkdir("1")
    root2 = tmpdir.mkdir("2")
    path1 = root1.join("test.txt")
    path1.write("content1")
    path2 = root2.join("test.txt")
    path2.write("content2")

    static_files_config = [
        StaticFilesConfig(path="/1", directory=root1),
        StaticFilesConfig(path="/2", directory=root2),
    ]
    with create_client([], static_files_config=static_files_config) as client:
        response = client.get("/1/test.txt")
        assert response.status_code == 200
        assert response.text == "content1"

        response = client.get("/2/test.txt")
        assert response.status_code == 200
        assert response.text == "content2"


def test_static_substring_of_self(tmpdir: Any) -> None:
    path = tmpdir.mkdir("static_part").mkdir("static")
    path = path.join("test.txt")
    path.write("content")

    static_files_config = StaticFilesConfig(path="/static", directory=tmpdir)
    with create_client([], static_files_config=static_files_config) as client:
        response = client.get("/static/static_part/static/test.txt")
        assert response.status_code == 200
        assert response.text == "content"


def test_static_with_settings(tmpdir: Any) -> None:
    from tests.settings import AppTestSettings

    class StaticSettings(AppTestSettings):
        @property
        def static_files_config(self) -> Any:
            return StaticFilesConfig(path="/static", directory=tmpdir)

    path = tmpdir.mkdir("static_part").mkdir("static")
    path = path.join("test.txt")
    path.write("content")

    with create_client([], settings_module=StaticSettings) as client:
        response = client.get("/static/static_part/static/test.txt")
        assert response.status_code == 200
        assert response.text == "content"


@pytest.mark.parametrize("redirect_slashes", [True, False])
def test_mixing_static_and_include(tmpdir: Any, redirect_slashes) -> None:
    @get("/include")
    async def get_include() -> str:
        return "include"

    path = tmpdir.join("test.txt")
    path.write("content")
    static_files_config = StaticFilesConfig(path="/static", directory=tmpdir)

    with create_client(
        [Include("/", routes=[get_include])],
        static_files_config=static_files_config,
        redirect_slashes=redirect_slashes,
    ) as client:
        response = client.get("/static/test.txt")
        assert response.status_code == 200
        assert response.text == "content"

        response = client.get("/include")
        assert response.status_code == 200


@pytest.mark.parametrize("redirect_slashes", [True, False])
def test_mixing_static_and_include_template_config(
    tmpdir: Any, template_dir, redirect_slashes
) -> None:
    @get("/include")
    async def get_include() -> str:
        return "include"

    path = tmpdir.join("test.txt")
    path.write("content")
    static_files_config = StaticFilesConfig(path="/static", directory=tmpdir)
    template_config = TemplateConfig(directory=template_dir)

    with create_client(
        [Include("/", routes=[get_include])],
        static_files_config=static_files_config,
        redirect_slashes=redirect_slashes,
        template_config=template_config,
    ) as client:
        response = client.get("/static/test.txt")
        assert response.status_code == 200
        assert response.text == "content"

        response = client.get("/include")
        assert response.status_code == 200
