from typing import Any

import pytest
from lilya.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from ravyn.exceptions import ImproperlyConfigured
from ravyn.routing.router import HTTPHandler
from ravyn.utils.enums import HttpMethod


@pytest.mark.parametrize(
    "method, status_code",
    [
        (HttpMethod.POST.value, HTTP_201_CREATED),
        (HttpMethod.DELETE.value, HTTP_204_NO_CONTENT),
        (HttpMethod.GET.value, HTTP_200_OK),
        (HttpMethod.QUERY.value, HTTP_200_OK),
        (HttpMethod.PUT.value, HTTP_200_OK),
        (HttpMethod.PATCH.value, HTTP_200_OK),
    ],
)
def test_route_handler_default_status_code(method: Any, status_code: int) -> None:
    route_handler = HTTPHandler(path="/", methods=[method], status_code=status_code)
    assert route_handler.status_code == status_code


@pytest.mark.parametrize(
    "method, status_code",
    [
        ([HttpMethod.POST.value], HTTP_201_CREATED),
        ([HttpMethod.DELETE.value], HTTP_204_NO_CONTENT),
        ([HttpMethod.GET.value], HTTP_200_OK),
        ([HttpMethod.QUERY.value], HTTP_200_OK),
        ([HttpMethod.PUT.value], HTTP_200_OK),
        ([HttpMethod.PATCH.value], HTTP_200_OK),
    ],
)
def test_raises_exception_route_handler(method: Any, status_code: int) -> None:
    with pytest.raises(ImproperlyConfigured):
        HTTPHandler(path="/", methods=[method], status_code=status_code)
