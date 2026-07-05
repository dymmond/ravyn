from typing import Optional

from ravyn.openapi.schemas.v3_1_0.operation import Operation
from ravyn.openapi.schemas.v3_1_0.path_item import PathItem as PathItem31


class PathItem(PathItem31):
    """
    OpenAPI 3.2 Path Item Object.

    OpenAPI 3.2 adds the fixed `query` operation field for the HTTP QUERY method
    and `additionalOperations` for non-fixed extension methods.
    """

    query: Optional[Operation] = None
    """
    A definition of a QUERY operation on this path.
    """

    additionalOperations: Optional[dict[str, Operation]] = None
    """
    A map of additional HTTP operations on this path.
    """
