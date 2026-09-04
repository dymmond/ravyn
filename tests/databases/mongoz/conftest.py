import typing

import pytest

from ravyn import settings

client = settings.mongoz_registry


def pytest_configure(config):
    config.option.asyncio_mode = "strict"


@pytest.fixture(scope="package")
def anyio_backend():
    return ("asyncio", {"debug": False})


@pytest.fixture(scope="package", autouse=True)
async def registry_lifespan() -> typing.AsyncGenerator:
    yield
    await client.close()


@pytest.fixture(autouse=True)
async def test_database() -> typing.AsyncGenerator:
    await client.drop_database("test_db")
    yield
    await client.drop_database("test_db")
