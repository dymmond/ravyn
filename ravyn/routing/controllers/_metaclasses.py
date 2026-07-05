from typing import TYPE_CHECKING, Any, ClassVar, Set, Tuple, Type, cast

if TYPE_CHECKING:
    from ravyn import SimpleAPIController
    from ravyn.routing.controllers.generics import ListAPIController


class SimpleAPIMeta(type):
    """
    Metaclass responsible for making sure
    only the CRUD objects are allowed.
    """

    __filtered_handlers__: ClassVar[list[str]]
    extra_allowed: list[str] = None

    def __new__(cls, name: str, bases: Tuple[Type, ...], attrs: Any) -> Any:
        """
        Making sure the `http_allowed_methods` are extended if inheritance happens
        in the subclass.

        The `http_allowed_methods` is the default for each type of generic but to allow
        extra allowed methods, the `extra_allowed` must be added.
        """
        view = super().__new__

        parents = [parent for parent in bases if isinstance(parent, SimpleAPIMeta)]
        if not parents:
            return view(cls, name, bases, attrs)

        http_allowed_methods: list[str] = []
        simple_view = cast("SimpleAPIController", view(cls, name, bases, attrs))
        cls.__filtered_handlers__ = [
            attr
            for attr in dir(simple_view)
            if not attr.startswith("__") and not attr.endswith("__")
        ]

        for base in bases:
            if (
                hasattr(base, "http_allowed_methods")
                and hasattr(base, "__is_generic__")
                and getattr(base, "__is_generic__", False) not in [False, None]
            ):
                http_allowed_methods.extend(base.http_allowed_methods)

        if hasattr(simple_view, "extra_allowed") and simple_view.extra_allowed is not None:
            assert isinstance(simple_view.extra_allowed, list), (
                "`extra_allowed` must be a list of strings allowed."
            )

            http_allowed_methods.extend(simple_view.extra_allowed)

        http_allowed_methods.extend(simple_view.http_allowed_methods)

        # Remove any duplicates
        allowed_methods: Set[str] = {method.lower() for method in http_allowed_methods}

        # Reasign the new clean list
        simple_view.http_allowed_methods = list(allowed_methods)
        for handler_name in cls.__filtered_handlers__:
            for base in simple_view.__bases__:
                attribute = getattr(simple_view, handler_name)
                simple_view.is_method_allowed(handler_name, base, attribute)
        return simple_view


class ListAPIMeta(SimpleAPIMeta):
    """
    Metaclass with an extra for lists specifically.
    """

    def __new__(cls, name: str, bases: Tuple, attrs: Any) -> Any:
        view: "ListAPIController" = super().__new__(cls, name, bases, attrs)

        if not hasattr(view, "__filtered_handlers__"):
            return view

        for handler_name in view.__filtered_handlers__:
            for base in view.__bases__:
                attribute = getattr(view, handler_name)
                view.is_signature_valid(handler_name, base, attribute, signature_type=list)
        return view
