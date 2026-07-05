"""OpenAPI v3.2.0 schema types.

The package reuses OpenAPI 3.1 schema objects where unchanged and overrides the
objects whose fixed fields changed in 3.2.0.
"""

from ravyn.openapi.schemas.v3_1_0 import *  # noqa
from ravyn.openapi.schemas.v3_1_0 import __all__ as _v3_1_0_all

from .open_api import OpenAPI
from .path_item import PathItem

__all__ = [*_v3_1_0_all, "OpenAPI", "PathItem"]
