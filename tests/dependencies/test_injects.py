from typing import Any, Dict, List, Optional

import pytest
from lilya.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from ravyn.applications import Ravyn
from ravyn.exceptions import ImproperlyConfigured
from ravyn.injector import Factory, Inject, Injects
from ravyn.routing.controllers import Controller
from ravyn.routing.gateways import Gateway
from ravyn.routing.handlers import get
from ravyn.routing.router import Include
from ravyn.testclient import create_client
from ravyn.utils.constants import IS_DEPENDENCY
from tests.conftest import FakeDAO


def test_is_dependency_inserted_into_field_extra() -> None:
    assert Injects().extra[IS_DEPENDENCY] is True


@pytest.mark.parametrize(
    "field_info, exp",
    [
        (Injects(), None),
        (Injects(None), None),
        (Injects(13), 13),
    ],
)
def test_dependency_defaults(field_info: Any, exp: Optional[int]) -> None:
    @get("/")
    def handler(value: Optional[int] = field_info) -> Dict[str, Optional[int]]:
        return {"value": value}

    with create_client(routes=[Gateway(handler=handler)]) as client:
        resp = client.get("/")
        assert resp.json() == {"value": exp}


def test_non_optional_with_default() -> None:
    @get("/")
    def handler(value: int = Injects(default=13)) -> Dict[str, int]:
        return {"value": value}

    with create_client(routes=[Gateway(handler=handler)]) as client:
        resp = client.get("/")
        assert resp.json() == {"value": 13}


def test_non_optional_with_default_include() -> None:
    @get("/")
    def handler(value: int = Injects(default=13)) -> Dict[str, int]:
        return {"value": value}

    with create_client(routes=[Include(routes=[Gateway(handler=handler)])]) as client:
        resp = client.get("/")
        assert resp.json() == {"value": 13}


def test_non_optional_with_default_nested_include() -> None:
    @get("/")
    def handler(value: int = Injects(default=13)) -> Dict[str, int]:
        return {"value": value}

    with create_client(
        routes=[Include(routes=[Include(routes=[Gateway(handler=handler)])])]
    ) as client:
        resp = client.get("/")
        assert resp.json() == {"value": 13}


def test_non_optional_with_default_very_nested_include() -> None:
    @get("/")
    def handler(value: int = Injects(default=13)) -> Dict[str, int]:
        return {"value": value}

    with create_client(
        routes=[
            Include(
                routes=[
                    Include(
                        routes=[
                            Include(
                                routes=[
                                    Include(
                                        routes=[
                                            Include(
                                                routes=[
                                                    Include(
                                                        routes=[
                                                            Include(
                                                                routes=[
                                                                    Include(
                                                                        routes=[
                                                                            Gateway(
                                                                                handler=handler
                                                                            )
                                                                        ]
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    ) as client:
        resp = client.get("/")
        assert resp.json() == {"value": 13}


def test_no_default_dependency_Injected() -> None:
    @get(dependencies={"value": Inject(lambda: 13)})
    def test(value: int = Injects()) -> Dict[str, int]:
        return {"value": value}

    with create_client(routes=[Gateway(handler=test)]) as client:
        resp = client.get("/")
    assert resp.json() == {"value": 13}


def test_no_default_dependency_Injected_with_Factory(get_fake_dao) -> None:
    @get(dependencies={"fake_dao": Inject(Factory(get_fake_dao))})
    async def test(fake_dao: FakeDAO = Injects()) -> Dict[str, int]:
        result = await fake_dao.get_all()
        return {"value": result}

    with create_client(routes=[Gateway(handler=test)]) as client:
        resp = client.get("/")
    assert resp.json() == {"value": ["awesome_data"]}


def test_no_default_dependency_Injected_with_Factory_from_string() -> None:
    @get(dependencies={"fake_dao": Inject(Factory("tests.conftest.FakeDAO"))})
    async def test(fake_dao: FakeDAO = Injects()) -> Dict[str, int]:
        result = await fake_dao.get_all()
        return {"value": result}

    with create_client(routes=[Gateway(handler=test)]) as client:
        resp = client.get("/")
    assert resp.json() == {"value": ["awesome_data"]}


def test_dependency_not_Injected_and_no_default() -> None:
    @get()
    def test(value: int = Injects()) -> Dict[str, int]:
        """ """

    with pytest.raises(ImproperlyConfigured):
        Ravyn(routes=[Gateway(handler=test)])


def test_dependency_Injected_on_APIView() -> None:
    class C(Controller):
        path = ""
        dependencies = {"value": Inject(lambda: 13)}

        @get()
        def test(self, value: int = Injects()) -> Dict[str, int]:
            return {"value": value}

    with create_client(routes=[Gateway(handler=C)]) as client:
        resp = client.get("/")
    assert resp.json() == {"value": 13}


def test_dependency_Injected_on_APIView_with_Factory(get_fake_dao) -> None:
    class C(Controller):
        path = ""
        dependencies = {"fake_dao": Inject(Factory(get_fake_dao))}

        @get()
        async def test(self, fake_dao: FakeDAO = Injects()) -> Dict[str, List[str]]:
            result = await fake_dao.get_all()
            return {"value": result}

    with create_client(routes=[Gateway(handler=C)]) as client:
        resp = client.get("/")
    assert resp.json() == {"value": ["awesome_data"]}


def test_dependency_Injected_on_APIView_with_Factory_from_string() -> None:
    class C(Controller):
        path = ""
        dependencies = {"fake_dao": Inject(Factory("tests.conftest.FakeDAO"))}

        @get()
        async def test(self, fake_dao: FakeDAO = Injects()) -> Dict[str, List[str]]:
            result = await fake_dao.get_all()
            return {"value": result}

    with create_client(routes=[Gateway(handler=C)]) as client:
        resp = client.get("/")
    assert resp.json() == {"value": ["awesome_data"]}


def test_dependency_skip_validation() -> None:
    @get("/validated")
    def validated(value: int = Injects()) -> Dict[str, int]:
        """ """

    @get("/skipped")
    def skipped(value: int = Injects(skip_validation=True)) -> Dict[str, int]:
        return {"value": value}

    with create_client(
        routes=[
            Gateway(handler=validated),
            Gateway(handler=skipped),
        ],
        dependencies={"value": Inject(lambda: "str")},
    ) as client:
        validated_resp = client.get("/validated")
        assert validated_resp.status_code == HTTP_500_INTERNAL_SERVER_ERROR

        skipped_resp = client.get("/skipped")
        assert skipped_resp.status_code == HTTP_200_OK
        assert skipped_resp.json() == {"value": "str"}


def test_dependency_skip_validation_with_Factory(get_fake_dao) -> None:
    @get("/validated")
    def validated(fake_dao: int = Injects()) -> Dict[str, List[str]]:
        """ """

    @get("/skipped")
    async def skipped(fake_dao: FakeDAO = Injects(skip_validation=True)) -> Dict[str, List[str]]:
        result = await fake_dao.get_all()
        return {"value": result}

    with create_client(
        routes=[
            Gateway(handler=validated),
            Gateway(handler=skipped),
        ],
        dependencies={"fake_dao": Inject(Factory(get_fake_dao))},
    ) as client:
        validated_resp = client.get("/validated")
        assert validated_resp.status_code == HTTP_500_INTERNAL_SERVER_ERROR

        skipped_resp = client.get("/skipped")
        assert skipped_resp.status_code == HTTP_200_OK
        assert skipped_resp.json() == {"value": ["awesome_data"]}


def test_dependency_skip_validation_with_Factory_from_string() -> None:
    @get("/validated")
    def validated(fake_dao: int = Injects()) -> Dict[str, List[str]]:
        """ """

    @get("/skipped")
    async def skipped(fake_dao: FakeDAO = Injects(skip_validation=True)) -> Dict[str, List[str]]:
        result = await fake_dao.get_all()
        return {"value": result}

    with create_client(
        routes=[
            Gateway(handler=validated),
            Gateway(handler=skipped),
        ],
        dependencies={"fake_dao": Inject(Factory("tests.conftest.FakeDAO"))},
    ) as client:
        validated_resp = client.get("/validated")
        assert validated_resp.status_code == HTTP_500_INTERNAL_SERVER_ERROR

        skipped_resp = client.get("/skipped")
        assert skipped_resp.status_code == HTTP_200_OK
        assert skipped_resp.json() == {"value": ["awesome_data"]}
