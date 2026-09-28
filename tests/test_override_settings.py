import asyncio
import functools
import inspect
import types

import pytest

from ravyn.conf import settings
from ravyn.testclient import override_settings


@override_settings(environment="test_func")
def test_can_override_settings():
    assert settings.environment == "test_func"


@override_settings(environment="test_func")
def test_name_of_settings():
    assert settings.__class__.__name__ == "AppTestSettings"


class TestInClass:
    @override_settings(environment="test_func")
    def test_can_override_settings(self):
        assert settings.environment == "test_func"

    @override_settings(environment="test_func")
    def test_name_of_settings(self):
        assert settings.__class__.__name__ == "AppTestSettings"


class TestInClassAsync:
    @override_settings(environment="test_func")
    @pytest.mark.asyncio
    async def test_can_override_settings(self, test_client_factory):
        assert settings.environment == "test_func"

    @override_settings(environment="test_func")
    @pytest.mark.asyncio
    async def test_name_of_settings(self, test_client_factory):
        assert settings.__class__.__name__ == "AppTestSettings"


@pytest.mark.parametrize("marked", [False, True])
def test_generator_based_coroutine_uses_async_settings_wrapper(marked):
    observed = []

    @types.coroutine
    def legacy_test():
        yield from asyncio.sleep(0).__await__()
        observed.append(settings.environment)

    if marked:
        legacy_test._is_coroutine = asyncio.coroutines._is_coroutine
    assert not inspect.iscoroutinefunction(legacy_test)
    assert asyncio.iscoroutinefunction(legacy_test) is marked

    wrapped = override_settings(environment="legacy_test")(legacy_test)
    assert inspect.iscoroutinefunction(wrapped)
    asyncio.run(wrapped())
    assert observed == ["legacy_test"]


@pytest.mark.parametrize("as_callable_instance", [False, True])
def test_wrapped_generator_coroutine_uses_async_settings_wrapper(as_callable_instance):
    observed = []

    @types.coroutine
    def legacy_test(*_args):
        if False:
            yield
        observed.append(settings.environment)

    class LegacyCallable:
        __call__ = legacy_test

    target = LegacyCallable() if as_callable_instance else functools.partial(legacy_test)
    wrapped = override_settings(environment="legacy_test")(target)

    assert inspect.iscoroutinefunction(wrapped)
    asyncio.run(wrapped())
    assert observed == ["legacy_test"]
