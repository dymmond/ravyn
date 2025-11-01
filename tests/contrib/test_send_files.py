import io
import os
import tempfile
from typing import Any

from ravyn import Gateway, Ravyn, get
from ravyn.contrib.responses.files import send_file
from ravyn.testclient import RavynTestClient


def create_temp_file(content: bytes, suffix=".txt"):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(content)
    tmp.close()
    return tmp.name


def test_send_file_from_path_as_inline(test_client_factory):
    tmp_path = create_temp_file(b"hello world", ".txt")

    @get()
    async def endpoint() -> Any:
        return send_file(tmp_path)

    app = Ravyn(routes=[Gateway("/file", handler=endpoint)])
    client = RavynTestClient(app)

    response = client.get("/file")
    assert response.status_code == 200
    assert response.text == "hello world"
    assert response.headers["content-disposition"] == "inline"

    os.remove(tmp_path)


def test_send_file_from_path_as_attachment(test_client_factory):
    tmp_path = create_temp_file(b"download me", ".txt")

    @get()
    async def endpoint() -> Any:
        return send_file(tmp_path, as_attachment=True)

    app = Ravyn(routes=[Gateway("/download", handler=endpoint)])
    client = RavynTestClient(app)

    response = client.get("/download")
    assert response.status_code == 200
    assert response.headers["content-disposition"].startswith("attachment;")
    assert response.content == b"download me"

    os.remove(tmp_path)


def test_send_file_with_custom_filename(test_client_factory):
    tmp_path = create_temp_file(b"abc123", ".dat")

    @get()
    async def endpoint() -> Any:
        return send_file(tmp_path, as_attachment=True, attachment_filename="custom.bin")

    app = Ravyn(routes=[Gateway("/custom", handler=endpoint)])
    client = RavynTestClient(app)

    response = client.get("/custom")
    assert response.status_code == 200
    assert 'filename="custom.bin"' in response.headers["content-disposition"]

    os.remove(tmp_path)


def test_send_file_with_file_like_object(test_client_factory):
    file_like = io.BytesIO(b"streamed content")

    @get()
    async def endpoint() -> Any:
        return send_file(file_like, mimetype="text/plain")

    app = Ravyn(routes=[Gateway("/stream", handler=endpoint)])
    client = RavynTestClient(app)

    response = client.get("/stream")
    assert response.status_code == 200
    assert response.text == "streamed content"
    assert response.headers["content-type"].startswith("text/plain")


def test_send_file_with_cache_control(test_client_factory):
    tmp_path = create_temp_file(b"cache me")

    @get()
    async def endpoint() -> Any:
        return send_file(tmp_path, max_age=3600)

    app = Ravyn(routes=[Gateway("/cache", handler=endpoint)])
    client = RavynTestClient(app)

    response = client.get("/cache")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=3600"

    os.remove(tmp_path)
