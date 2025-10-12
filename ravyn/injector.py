from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Type, Union

from lilya.dependencies import Depends as _Depends
from lilya.exceptions import ImproperlyConfigured
from pydantic.fields import FieldInfo

from ravyn.core.injector.provider import load_provider
from ravyn.core.transformers.signature import SignatureModel
from ravyn.parsers import ArbitraryHashableBaseModel
from ravyn.typing import Undefined, Void
from ravyn.utils.constants import IS_DEPENDENCY, SKIP_VALIDATION
from ravyn.utils.helpers import is_async_callable

if TYPE_CHECKING:  # pragma: no cover
    from ravyn.typing import AnyCallable


class Factory:
    def __init__(self, provides: Union["AnyCallable", str], *args: Any, **kwargs: Any) -> None:
        """
        A dependency injection factory that supports both positional and keyword arguments.

        The provider can be passed as either:
        - A direct callable
        - A string reference to be dynamically imported

        Example Usage:
            dependencies = {
                "user": Factory(UserDAO, db_session=session, cache=cache)
            }
        """
        self.__args: tuple[Any, ...] = args
        self.__kwargs: dict[str, Any] = kwargs
        self.is_nested: bool = False

        if isinstance(provides, str):
            self.provides, self.is_nested = load_provider(provides)
        else:
            self.provides = provides

    def set_args(self, *args: Any, **kwargs: Any) -> None:
        """Set or update arguments dynamically."""
        self.__args = args
        self.__kwargs = kwargs

    @property
    def cls(self) -> "AnyCallable":  # pragma: no cover
        """Return the provided class or function."""
        return self.provides

    async def __call__(self) -> Any:
        """
        Instantiates the provided class/function, handling both sync and async cases.

        Supports:
            - Nested imports (e.g., MyClass.func, MyClass.SubClass.func)
            - Both sync and async callables
            - Positional and keyword arguments

        Example:
            Factory(UserDAO, db_session=session)
        """
        if self.is_nested:
            self.provides = self.provides()

        if is_async_callable(self.provides):
            return await self.provides(*self.__args, **self.__kwargs)
        return self.provides(*self.__args, **self.__kwargs)


class Inject(ArbitraryHashableBaseModel):
    """
    Ravyn's dependency injector built on Lilya's dependency system internally.
    Keeps full backward compatibility with the old behavior and interface.
    """

    def __init__(self, dependency: "AnyCallable", use_cache: bool = False, **kwargs: Any):
        super().__init__(**kwargs)
        self.dependency = dependency
        self.use_cache = use_cache
        self.signature_model: Optional[Type["SignatureModel"]] = None
        self._depends = _Depends(dependency, use_cache=use_cache)
        self.value: Any = Void

    async def __call__(self, **kwargs: dict[str, Any]) -> Any:
        if self.use_cache and self.value is not Void:
            return self.value

        try:
            if is_async_callable(self.dependency):
                value = await self.dependency(**kwargs)
            else:
                value = self.dependency(**kwargs)
        except TypeError as e:
            raise ImproperlyConfigured(str(e)) from e

        if self.use_cache:
            self.value = value

        return value

    def __eq__(self, other: Any) -> bool:
        return other is self or (
            isinstance(other, self.__class__)
            and other.dependency == self.dependency
            and other.use_cache == self.use_cache
            and getattr(other, "value", Void) == getattr(self, "value", Void)
        )

    def __hash__(self) -> int:
        values: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            values[key] = None
            if isinstance(value, (list, set)):
                values[key] = tuple(value)
            else:
                values[key] = value
        return hash((type(self),) + tuple(values))


class Injects(FieldInfo):
    """
    Creates a FieldInfo class with extra parameters.
    This is used for dependencies and to inject them.

    **Example**

    ```python
    @get(dependencies={"value": Inject(lambda: 13)})
    def myview(value: Injects()):
        return {"value": value}
    ```
    """

    def __init__(
        self,
        default: Any = Undefined,
        skip_validation: bool = False,
        allow_none: bool = True,
    ) -> None:
        self.allow_none = allow_none
        self.extra: dict[str, Any] = {
            IS_DEPENDENCY: True,
            SKIP_VALIDATION: skip_validation,
            "allow_none": self.allow_none,
        }
        super().__init__(default=default, json_schema_extra=self.extra)
