import inspect
from functools import cached_property
from typing import Any, Callable, Optional, Sequence, Union

from pydantic.fields import AliasChoices, AliasPath, FieldInfo

from ravyn.security.scopes import Scopes
from ravyn.typing import Undefined
from ravyn.utils.enums import EncodingType, ParamType
from ravyn.utils.helpers import is_class_and_subclass, make_callable

_PyUndefined: Any = Undefined


class Param(FieldInfo):
    in_: ParamType

    def __init__(
        self,
        default: Any = _PyUndefined,
        *,
        allow_none: Optional[bool] = True,
        default_factory: Optional[Callable[..., Any]] = _PyUndefined,
        annotation: Optional[Any] = None,
        alias: Optional[str] = None,
        alias_priority: Optional[int] = _PyUndefined,
        value_type: Any = _PyUndefined,
        header: Optional[str] = None,
        cookie: Optional[str] = None,
        query: Optional[str] = None,
        path: Optional[str] = None,
        content_encoding: Optional[str] = None,
        required: bool = True,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        multiple_of: Optional[float] = _PyUndefined,
        allow_inf_nan: Optional[bool] = _PyUndefined,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        max_digits: Optional[int] = _PyUndefined,
        strict: Optional[bool] = _PyUndefined,
        pattern: Optional[str] = None,
        examples: Optional[list[Any]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        validation_alias: Optional[Union[str, AliasPath, AliasChoices]] = None,
        discriminator: Optional[str] = None,
        frozen: Optional[bool] = None,
        validate_default: bool = True,
        init_var: bool = True,
        kw_only: bool = True,
        json_schema_extra: Optional[dict[str, Any]] = None,
    ) -> None:
        self.deprecated = deprecated
        self.examples = examples
        self.include_in_schema = include_in_schema
        self.allow_none = allow_none

        extra: dict[str, Any] = {}
        extra.update(header=header)
        extra.update(cookie=cookie)
        extra.update(query=query)
        extra.update(path=path)
        extra.update(required=required)
        extra.update(content_encoding=content_encoding)
        extra.update(value_type=value_type)
        extra.update(examples=self.examples)
        extra.update(deprecated=self.deprecated)
        extra.update(include_in_schema=self.include_in_schema)
        extra.update(allow_none=self.allow_none)

        if json_schema_extra is not None:
            extra.update(json_schema_extra)

        super().__init__(
            annotation=annotation,
            default=default,
            default_factory=default_factory,
            alias=alias,
            alias_priority=alias_priority,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            multiple_of=multiple_of,
            min_length=min_length,
            max_length=max_length,
            pattern=pattern,
            examples=examples,
            allow_inf_nan=allow_inf_nan,
            json_schema_extra=extra,
            validate_default=validate_default,
            validation_alias=validation_alias,
            discriminator=discriminator,
            max_digits=max_digits,
            strict=strict,
            frozen=frozen,
            init_var=init_var,
            kw_only=kw_only,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(annotation={self.annotation}, default={self.default})"


class Header(Param):
    in_ = ParamType.HEADER

    def __init__(
        self,
        *,
        default: Any = _PyUndefined,
        allow_none: Optional[bool] = True,
        default_factory: Optional[Callable[..., Any]] = _PyUndefined,
        annotation: Optional[Any] = None,
        alias: Optional[str] = None,
        alias_priority: Optional[int] = _PyUndefined,
        value: Optional[str] = None,
        value_type: Any = _PyUndefined,
        content_encoding: Optional[str] = None,
        required: bool = True,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        multiple_of: Optional[float] = _PyUndefined,
        allow_inf_nan: Optional[bool] = _PyUndefined,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        max_digits: Optional[int] = _PyUndefined,
        strict: Optional[bool] = _PyUndefined,
        pattern: Optional[str] = None,
        examples: Optional[list[Any]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        validation_alias: Optional[Union[str, AliasPath, AliasChoices]] = None,
        discriminator: Optional[str] = None,
        frozen: Optional[bool] = None,
        validate_default: bool = True,
        init_var: bool = True,
        kw_only: bool = True,
        json_schema_extra: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            default=default,
            allow_none=allow_none,
            default_factory=default_factory,
            annotation=annotation,
            header=value,
            alias=alias,
            alias_priority=alias_priority,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            multiple_of=multiple_of,
            allow_inf_nan=allow_inf_nan,
            min_length=min_length,
            max_length=max_length,
            max_digits=max_digits,
            strict=strict,
            pattern=pattern,
            required=required,
            content_encoding=content_encoding,
            value_type=value_type,
            examples=examples,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            validate_default=validate_default,
            validation_alias=validation_alias,
            discriminator=discriminator,
            frozen=frozen,
            init_var=init_var,
            kw_only=kw_only,
            json_schema_extra=json_schema_extra,
        )


class Cookie(Param):
    in_ = ParamType.COOKIE

    def __init__(
        self,
        default: Any = _PyUndefined,
        *,
        allow_none: Optional[bool] = True,
        default_factory: Optional[Callable[..., Any]] = _PyUndefined,
        annotation: Optional[Any] = None,
        alias: Optional[str] = None,
        alias_priority: Optional[int] = _PyUndefined,
        value_type: Any = _PyUndefined,
        value: Optional[str] = None,
        content_encoding: Optional[str] = None,
        required: bool = True,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        multiple_of: Optional[float] = _PyUndefined,
        allow_inf_nan: Optional[bool] = _PyUndefined,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        max_digits: Optional[int] = _PyUndefined,
        strict: Optional[bool] = _PyUndefined,
        pattern: Optional[str] = None,
        examples: Optional[list[Any]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        validation_alias: Optional[Union[str, AliasPath, AliasChoices]] = None,
        discriminator: Optional[str] = None,
        frozen: Optional[bool] = None,
        validate_default: bool = True,
        init_var: bool = True,
        kw_only: bool = True,
        json_schema_extra: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            default=default,
            allow_none=allow_none,
            default_factory=default_factory,
            annotation=annotation,
            cookie=value,
            alias=alias,
            alias_priority=alias_priority,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            multiple_of=multiple_of,
            allow_inf_nan=allow_inf_nan,
            min_length=min_length,
            max_length=max_length,
            max_digits=max_digits,
            strict=strict,
            pattern=pattern,
            required=required,
            content_encoding=content_encoding,
            value_type=value_type,
            examples=examples,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            validate_default=validate_default,
            validation_alias=validation_alias,
            discriminator=discriminator,
            frozen=frozen,
            init_var=init_var,
            kw_only=kw_only,
            json_schema_extra=json_schema_extra,
        )


class Query(Param):
    in_ = ParamType.QUERY

    def __init__(
        self,
        default: Any = _PyUndefined,
        *,
        allow_none: Optional[bool] = True,
        default_factory: Optional[Callable[..., Any]] = _PyUndefined,
        annotation: Optional[Any] = None,
        alias: Optional[str] = None,
        alias_priority: Optional[int] = _PyUndefined,
        value_type: Any = _PyUndefined,
        value: Optional[str] = None,
        content_encoding: Optional[str] = None,
        required: bool = True,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        multiple_of: Optional[float] = _PyUndefined,
        allow_inf_nan: Optional[bool] = _PyUndefined,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        max_digits: Optional[int] = _PyUndefined,
        strict: Optional[bool] = _PyUndefined,
        pattern: Optional[str] = None,
        examples: Optional[list[Any]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        validation_alias: Optional[Union[str, AliasPath, AliasChoices]] = None,
        discriminator: Optional[str] = None,
        frozen: Optional[bool] = None,
        validate_default: bool = True,
        init_var: bool = True,
        kw_only: bool = True,
        json_schema_extra: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            default=default,
            allow_none=allow_none,
            default_factory=default_factory,
            annotation=annotation,
            query=value,
            alias=alias,
            alias_priority=alias_priority,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            multiple_of=multiple_of,
            allow_inf_nan=allow_inf_nan,
            min_length=min_length,
            max_length=max_length,
            max_digits=max_digits,
            strict=strict,
            pattern=pattern,
            required=required,
            content_encoding=content_encoding,
            value_type=value_type,
            examples=examples,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            validate_default=validate_default,
            validation_alias=validation_alias,
            discriminator=discriminator,
            frozen=frozen,
            init_var=init_var,
            kw_only=kw_only,
            json_schema_extra=json_schema_extra,
        )


class Path(Param):
    in_ = ParamType.PATH

    def __init__(
        self,
        default: Any = _PyUndefined,
        *,
        allow_none: Optional[bool] = True,
        default_factory: Optional[Callable[..., Any]] = _PyUndefined,
        annotation: Optional[Any] = None,
        value_type: Any = _PyUndefined,
        content_encoding: Optional[str] = None,
        required: bool = True,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        max_digits: Optional[int] = _PyUndefined,
        strict: Optional[bool] = _PyUndefined,
        pattern: Optional[str] = None,
        examples: Optional[list[Any]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        validation_alias: Optional[Union[str, AliasPath, AliasChoices]] = None,
        discriminator: Optional[str] = None,
        frozen: Optional[bool] = None,
        validate_default: bool = True,
        init_var: bool = True,
        kw_only: bool = True,
        json_schema_extra: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            default=default,
            allow_none=allow_none,
            default_factory=default_factory,
            annotation=annotation,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            max_digits=max_digits,
            strict=strict,
            pattern=pattern,
            required=required,
            content_encoding=content_encoding,
            value_type=value_type,
            examples=examples,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            validate_default=validate_default,
            validation_alias=validation_alias,
            discriminator=discriminator,
            frozen=frozen,
            init_var=init_var,
            kw_only=kw_only,
            json_schema_extra=json_schema_extra,
        )


class Body(FieldInfo):
    def __init__(
        self,
        default: Any = _PyUndefined,
        *,
        allow_none: Optional[bool] = True,
        default_factory: Optional[Callable[..., Any]] = _PyUndefined,
        annotation: Optional[Any] = None,
        media_type: Union[str, EncodingType] = EncodingType.JSON,
        content_encoding: Optional[str] = None,
        title: Optional[str] = None,
        alias: Optional[str] = None,
        alias_priority: Optional[int] = _PyUndefined,
        description: Optional[str] = None,
        embed: Optional[bool] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        multiple_of: Optional[float] = _PyUndefined,
        allow_inf_nan: Optional[bool] = _PyUndefined,
        max_digits: Optional[int] = _PyUndefined,
        strict: Optional[bool] = _PyUndefined,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        examples: Optional[list[Any]] = None,
        validation_alias: Optional[Union[str, AliasPath, AliasChoices]] = None,
        discriminator: Optional[str] = None,
        frozen: Optional[bool] = None,
        validate_default: bool = True,
        init_var: bool = True,
        kw_only: bool = True,
        include_in_schema: bool = True,
        json_schema_extra: Optional[dict[str, Any]] = None,
    ) -> None:
        extra: dict[str, Any] = {}
        self.media_type = media_type
        self.content_encoding = content_encoding
        self.examples = examples
        self.allow_none = allow_none
        self.include_in_schema = include_in_schema

        extra.update(media_type=self.media_type)
        extra.update(content_encoding=self.content_encoding)
        extra.update(embed=embed)
        extra.update(allow_none=allow_none)

        json_schema_extra = extra if json_schema_extra is None else json_schema_extra.update(extra)

        super().__init__(
            default=default,
            default_factory=default_factory,
            annotation=annotation,
            title=title,
            alias=alias,
            alias_priority=alias_priority,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            multiple_of=multiple_of,
            max_digits=max_digits,
            allow_inf_nan=allow_inf_nan,
            min_length=min_length,
            max_length=max_length,
            pattern=pattern,
            json_schema_extra=json_schema_extra,
            validate_default=validate_default,
            validation_alias=validation_alias,
            discriminator=discriminator,
            frozen=frozen,
            init_var=init_var,
            strict=strict,
            kw_only=kw_only,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(annotation={self.annotation}, default={self.default})"


class Form(Body):
    def __init__(
        self,
        default: Any = _PyUndefined,
        *,
        annotation: Optional[Any] = None,
        default_factory: Optional[Callable[..., Any]] = _PyUndefined,
        allow_none: Optional[bool] = True,
        media_type: Union[str, EncodingType] = EncodingType.URL_ENCODED,
        content_encoding: Optional[str] = None,
        alias: Optional[str] = None,
        alias_priority: Optional[int] = _PyUndefined,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        examples: Optional[list[Any]] = None,
        validation_alias: Optional[Union[str, AliasPath, AliasChoices]] = None,
        discriminator: Optional[str] = None,
        max_digits: Optional[int] = _PyUndefined,
        strict: Optional[bool] = _PyUndefined,
        frozen: Optional[bool] = None,
        validate_default: bool = True,
        init_var: bool = True,
        kw_only: bool = True,
        include_in_schema: bool = True,
        json_schema_extra: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            default=default,
            annotation=annotation,
            allow_none=allow_none,
            default_factory=default_factory,
            embed=True,
            media_type=media_type,
            content_encoding=content_encoding,
            alias=alias,
            alias_priority=alias_priority,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            pattern=pattern,
            examples=examples,
            validate_default=validate_default,
            validation_alias=validation_alias,
            discriminator=discriminator,
            frozen=frozen,
            init_var=init_var,
            kw_only=kw_only,
            include_in_schema=include_in_schema,
            max_digits=max_digits,
            strict=strict,
            json_schema_extra=json_schema_extra,
        )


class File(Form):
    def __init__(
        self,
        default: Any = _PyUndefined,
        *,
        annotation: Optional[Any] = None,
        allow_none: Optional[bool] = True,
        default_factory: Optional[Callable[..., Any]] = _PyUndefined,
        media_type: Union[str, EncodingType] = EncodingType.MULTI_PART,
        content_encoding: Optional[str] = None,
        alias: Optional[str] = None,
        alias_priority: Optional[int] = _PyUndefined,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        examples: Optional[list[Any]] = None,
        validation_alias: Optional[Union[str, AliasPath, AliasChoices]] = None,
        discriminator: Optional[str] = None,
        max_digits: Optional[int] = _PyUndefined,
        strict: Optional[bool] = _PyUndefined,
        frozen: Optional[bool] = None,
        validate_default: bool = True,
        init_var: bool = True,
        kw_only: bool = True,
        include_in_schema: bool = True,
    ) -> None:
        super().__init__(
            default=default,
            annotation=annotation,
            allow_none=allow_none,
            default_factory=default_factory,
            media_type=media_type,
            content_encoding=content_encoding,
            alias=alias,
            alias_priority=alias_priority,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            pattern=pattern,
            examples=examples,
            validate_default=validate_default,
            validation_alias=validation_alias,
            discriminator=discriminator,
            max_digits=max_digits,
            strict=strict,
            frozen=frozen,
            init_var=init_var,
            kw_only=kw_only,
            include_in_schema=include_in_schema,
        )


class BaseRequires:
    """
    A class that represents a requirement with an optional dependency and caching behavior.

    This object serves as a base class for other classes that require dependencies.

    Attributes:
        dependency (Optional[Callable[..., Any]]): An optional callable that represents the dependency.
        use_cache (bool): A flag indicating whether to use caching for the dependency. Defaults to True.

    Methods:
        __repr__(): Returns a string representation of the Requires instance.
    """

    def __init__(self, dependency: Optional[Callable[..., Any]] = None, *, use_cache: bool = True):
        """
        Initializes a Requires instance.

        Args:
            dependency (Optional[Callable[..., Any]]): An optional callable that represents the dependency.
            use_cache (bool): A flag indicating whether to use caching for the dependency. Defaults to True.
        """

        """
        Returns a string representation of the Requires instance.

        Returns:
            str: A string representation of the Requires instance.
        """
        self.dependency = dependency
        self.use_cache = use_cache

        if not callable(dependency):
            dependency = make_callable(dependency)
        self.signature_model = inspect.signature(dependency) if dependency else None

    def __repr__(self) -> str:
        attr = getattr(self.dependency, "__name__", type(self.dependency).__name__)
        cache = "" if self.use_cache else ", use_cache=False"
        return f"{self.__class__.__name__}({attr}{cache})"


class Requires(BaseRequires): ...


class Security(BaseRequires):
    """
    A class used to represent security requirements for a particular operation.

    Attributes:
    ----------
    dependency : Optional[Callable[..., Any]]
        A callable that represents the dependency required for security.
    scopes : Optional[Sequence[str]]
        A sequence of scopes required for the security. Defaults to an empty list.
    use_cache : bool
        A flag indicating whether to use cache. Defaults to True.

    Methods:
    -------
    __init__(self, dependency: Optional[Callable[..., Any]] = None, *, scopes: Optional[Sequence[str]] = None, use_cache: bool = True)
        Initializes the Security class with the given dependency, scopes, and use_cache flag.
    """

    def __init__(
        self,
        dependency: Optional[Callable[..., Any]] = None,
        *,
        scopes: Optional[Sequence[str]] = None,
        use_cache: bool = True,
    ):
        super().__init__(dependency=dependency, use_cache=use_cache)
        self.scopes = scopes or []

    @cached_property
    def is_security_scope_dependency(self) -> bool:
        parameters: dict[str, inspect.Parameter] = dict(self.signature_model.parameters.items())
        return any(
            is_class_and_subclass(param.annotation, Scopes) for param in parameters.values()
        )
