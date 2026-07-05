from typing import Any, Optional, Union

from pydantic import ConfigDict

from ravyn.openapi.schemas.v3_1_0.open_api import OpenAPI as OpenAPI31
from ravyn.openapi.schemas.v3_1_0.reference import Reference

from .path_item import PathItem


class OpenAPI(OpenAPI31):
    """Root OpenAPI 3.2 document object."""

    openapi: str = "3.2.0"
    paths: Optional[dict[str, Union[PathItem, Any]]] = None
    webhooks: Optional[dict[str, Union[PathItem, Reference]]] = None

    model_config = ConfigDict(extra="ignore")
