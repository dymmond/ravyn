from typing import List, Optional, Union

from typing_extensions import Annotated

from ravyn import Gateway, JSONResponse, Query, get
from ravyn.testclient import create_client


@get("/list")
async def check_list(a_value: List[str]) -> JSONResponse:
    return JSONResponse({"value": a_value})


@get("/another-list")
async def check_another_list(
    a_value: Annotated[list, Query()] = ["true", "false", "test"],  # noqa
) -> JSONResponse:
    return JSONResponse({"value": a_value})


def test_query_param(test_client_factory):
    with create_client(
        routes=[Gateway(handler=check_list), Gateway(handler=check_another_list)]
    ) as client:
        response = client.get("/list?a_value=true&a_value=false&a_value=test")

        assert response.status_code == 200
        assert response.json() == {"value": ["true", "false", "test"]}

        response = client.get("/another-list?a_value=true&a_value=false&a_value=test")

        assert response.status_code == 200
        assert response.json() == {"value": ["true", "false", "test"]}


@get("/union")
async def union_list(a_value: Union[List[str], None]) -> JSONResponse:  # noqa
    return JSONResponse({"value": a_value})


def test_query_param_union(test_client_factory):
    with create_client(routes=[Gateway(handler=union_list)]) as client:
        response = client.get("/union")

        assert response.status_code == 200
        assert response.json() == {"value": None}

        response = client.get("/union?a_value=true&a_value=false&a_value=test")

        assert response.status_code == 200
        assert response.json() == {"value": ["true", "false", "test"]}


@get("/union")
async def union_list_syntax(a_value: list[str] | None) -> JSONResponse:  # noqa
    return JSONResponse({"value": a_value})


def test_query_param_union_syntax(test_client_factory):
    with create_client(routes=[Gateway(handler=union_list_syntax)]) as client:
        response = client.get("/union")

        assert response.status_code == 200
        assert response.json() == {"value": None}

        response = client.get("/union?a_value=true&a_value=false&a_value=test")

        assert response.status_code == 200
        assert response.json() == {"value": ["true", "false", "test"]}


@get("/union")
async def union_list_syntax_annotated(
    a_value: Annotated[list[str] | None, Query()],
) -> JSONResponse:  # noqa
    return JSONResponse({"value": a_value})


def test_query_param_union_syntax_annotated(test_client_factory):
    with create_client(routes=[Gateway(handler=union_list_syntax_annotated)]) as client:
        response = client.get("/union")

        assert response.status_code == 200
        assert response.json() == {"value": None}

        response = client.get("/union?a_value=true&a_value=false&a_value=test")

        assert response.status_code == 200
        assert response.json() == {"value": ["true", "false", "test"]}


@get("/optional")
async def optional_list(a_value: Optional[List[str]]) -> JSONResponse:  # noqa
    return JSONResponse({"value": a_value})


def test_query_param_optional(test_client_factory):
    with create_client(routes=[Gateway(handler=optional_list)]) as client:
        response = client.get("/optional")

        assert response.status_code == 200
        assert response.json() == {"value": None}

        response = client.get("/optional?a_value=true&a_value=false&a_value=test")

        assert response.status_code == 200
        assert response.json() == {"value": ["true", "false", "test"]}


@get("/random")
async def random_list(a_value: list[int] | None = None) -> JSONResponse:
    return JSONResponse({"value": a_value})


def test_query_list_with_optional_new_syntax(test_client_factory):
    with create_client(routes=[Gateway(handler=random_list)]) as client:
        response = client.get("/random")

        assert response.status_code == 200
        assert response.json() == {"value": None}

        response = client.get("/random?a_value=1&a_value=2&a_value=3")

        assert response.status_code == 200
        assert response.json() == {"value": [1, 2, 3]}


@get("/random-more")
async def random_list_with_many_params(
    a_value: list[int] | None = None, q: str | None = None
) -> JSONResponse:
    return JSONResponse({"value": a_value, "q": q})


def test_query_list_with_optional_with_more_params(test_client_factory):
    with create_client(routes=[Gateway(handler=random_list_with_many_params)]) as client:
        response = client.get("/random-more")

        assert response.status_code == 200
        assert response.json() == {"value": None, "q": None}

        response = client.get("/random-more?a_value=1&a_value=2&a_value=3&q=test")

        assert response.status_code == 200
        assert response.json() == {"value": [1, 2, 3], "q": "test"}

        response = client.get("/random-more?a_value=1&a_value=2&a_value=3")

        assert response.status_code == 200
        assert response.json() == {"value": [1, 2, 3], "q": None}


@get("/random-more-with-union")
async def random_list_with_many_params_with_union(
    a_value: Union[list[int], None] = None, q: Union[str, None] = None
) -> JSONResponse:
    return JSONResponse({"value": a_value, "q": q})


def test_query_list_with_optional_with_more_params_with_union(test_client_factory):
    with create_client(
        routes=[Gateway(handler=random_list_with_many_params_with_union)]
    ) as client:
        response = client.get("/random-more-with-union")

        assert response.status_code == 200
        assert response.json() == {"value": None, "q": None}

        response = client.get("/random-more-with-union?a_value=1&a_value=2&a_value=3&q=test")

        assert response.status_code == 200
        assert response.json() == {"value": [1, 2, 3], "q": "test"}

        response = client.get("/random-more-with-union?a_value=1&a_value=2&a_value=3")

        assert response.status_code == 200
        assert response.json() == {"value": [1, 2, 3], "q": None}


@get("/random-with-int")
async def random_list_with_int(
    a_value: Union[list[int], None] = None, q: Union[str, None] = None
) -> JSONResponse:
    return JSONResponse({"value": a_value, "q": q})


def test_query_list_with_int(test_client_factory):
    with create_client(routes=[Gateway(handler=random_list_with_int)]) as client:
        response = client.get("/random-with-int")

        assert response.status_code == 200
        assert response.json() == {"value": None, "q": None}

        response = client.get("/random-with-int?a_value=1&a_value=2&a_value=3&q=test")

        assert response.status_code == 200
        assert response.json() == {"value": [1, 2, 3], "q": "test"}

        response = client.get("/random-with-int?a_value=1&a_value=2&a_value=3")

        assert response.status_code == 200
        assert response.json() == {"value": [1, 2, 3], "q": None}


@get("/random-with-int-in-the-mix")
async def random_list_with_int_in_the_mix(
    a_value: Union[list[int], None] = None,
    b_value: Union[list[str], None] = None,
    c_value: Union[list[bool], None] = None,
    q: Union[str, None] = None,
) -> JSONResponse:
    return JSONResponse({"value": a_value, "b": b_value, "c": c_value, "q": q})


def test_random_list_with_int_in_the_mix(test_client_factory):
    with create_client(routes=[Gateway(handler=random_list_with_int_in_the_mix)]) as client:
        response = client.get("/random-with-int-in-the-mix")

        assert response.status_code == 200
        assert response.json() == {"value": None, "b": None, "c": None, "q": None}

        response = client.get("/random-with-int-in-the-mix?a_value=1&a_value=2&a_value=3&q=test")

        assert response.status_code == 200
        assert response.json() == {"value": [1, 2, 3], "b": None, "c": None, "q": "test"}

        response = client.get(
            "/random-with-int-in-the-mix?a_value=1&a_value=2&a_value=3&b_value=test&c_value=true&q=test"
        )

        assert response.status_code == 200
        assert response.json() == {"value": [1, 2, 3], "b": ["test"], "c": [True], "q": "test"}


@get("/random-with-int-in-the-mix-and-dict")
async def random_list_with_int_in_the_mix_and_dict(
    a_value: Union[list[int], None] = None,
    b_value: Union[list[str], None] = None,
    c_value: list[bool] | None = None,
    q: Union[str, None] = None,
    d_value: dict[str, int] | None = None,
) -> JSONResponse:
    return JSONResponse({"value": a_value, "b": b_value, "c": c_value, "q": q, "d": d_value})


def test_random_list_with_int_in_the_mix_and_dict(test_client_factory):
    with create_client(
        routes=[Gateway(handler=random_list_with_int_in_the_mix_and_dict)]
    ) as client:
        response = client.get("/random-with-int-in-the-mix-and-dict")

        assert response.status_code == 200
        assert response.json() == {"value": None, "b": None, "c": None, "q": None, "d": None}

        response = client.get(
            "/random-with-int-in-the-mix-and-dict?a_value=1&a_value=2&a_value=3&q=test&d_value[foo]=1&d_value[bar]=2"
        )

        assert response.status_code == 200
        assert response.json() == {
            "value": [1, 2, 3],
            "b": None,
            "c": None,
            "q": "test",
            "d": {"foo": 1, "bar": 2},
        }

        response = client.get(
            "/random-with-int-in-the-mix-and-dict?a_value=1&a_value=2&a_value=3&b_value=test&c_value=true&q=test&d_value[foo]=1&d_value[bar]=2"
        )

        assert response.status_code == 200
        assert response.json() == {
            "value": [1, 2, 3],
            "b": ["test"],
            "c": [True],
            "q": "test",
            "d": {"foo": 1, "bar": 2},
        }
