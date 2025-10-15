import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Mapping,
    NamedTuple,
    Set,
    Tuple,
    Type,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from lilya.datastructures import URL, QueryParam
from pydantic.fields import FieldInfo

from ravyn.exceptions import ImproperlyConfigured, ValidationErrorException
from ravyn.params import Cookie, Header, Path, Query
from ravyn.parsers import ArbitraryExtraBaseModel, HashableBaseModel
from ravyn.requests import Request
from ravyn.typing import Undefined
from ravyn.utils.constants import REQUIRED
from ravyn.utils.dependencies import is_requires
from ravyn.utils.enums import ParamType, ScopeType
from ravyn.utils.helpers import is_class_and_subclass, is_union
from ravyn.utils.schema import should_skip_json_schema

if TYPE_CHECKING:  # pragma: no cover
    from ravyn.core.transformers.signature import Parameter, SignatureModel
    from ravyn.injector import Inject
    from ravyn.types import ConnectionType


class ParamSetting(NamedTuple):
    default_value: Any
    field_alias: str
    field_name: str
    is_required: bool
    param_type: ParamType
    field_info: FieldInfo
    is_security: bool = False
    is_requires_dependency: bool = False


class Dependency(HashableBaseModel, ArbitraryExtraBaseModel):
    def __init__(
        self,
        key: str,
        inject: "Inject",
        dependencies: list["Dependency"],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.key = key
        self.inject = inject
        self.dependencies = dependencies


def _merge_difference_parameters(difference: Set[ParamSetting]) -> Set[ParamSetting]:
    """
    Merge difference parameters based on field alias and requirement.

    Args:
        difference (Set[ParamSetting]): Set of difference parameters.

    Returns:
        Set[ParamSetting]: Merged difference parameters.
    """
    merged_result = set()

    for parameter in difference:
        if parameter.is_required or not any(
            param.field_alias == parameter.field_alias and param.is_required
            for param in difference
        ):
            merged_result.add(parameter)

    return merged_result


def merge_sets(first_set: Set[ParamSetting], second_set: Set[ParamSetting]) -> Set[ParamSetting]:
    """
    Merge two sets of parameter settings.

    Args:
        first_set (Set[ParamSetting]): First set of parameter settings.
        second_set (Set[ParamSetting]): Second set of parameter settings.

    Returns:
        Set[ParamSetting]: Merged set of parameter settings.
    """
    merged_result = first_set.intersection(second_set)
    difference = first_set.symmetric_difference(second_set)

    merged_result.update(_merge_difference_parameters(difference))

    return merged_result


def _get_default_value(field_info: FieldInfo) -> Any:
    """
    Get the default value from field information.

    Args:
        field_info (FieldInfo): Information about the field.

    Returns:
        Any: Default value of the field.
    """
    return field_info.default if field_info.default is not Undefined else None


def create_parameter_setting(
    allow_none: bool,
    field_info: FieldInfo,
    field_name: str,
    path_parameters: Set[str],
    is_security: bool,
    is_requires_dependency: bool,
) -> ParamSetting:
    """
    Create a setting definition for a parameter.

    Args:
        allow_none (bool): Flag indicating if None is allowed.
        field_info (FieldInfo): Information about the field.
        field_name (str): Name of the field.
        path_parameters (Set[str]): Set of path parameters.

    Returns:
        ParamSetting: Parameter setting definition.
    """
    extra = cast("dict[str, Any]", field_info.json_schema_extra) or {}
    is_required = extra.get(REQUIRED, True)
    default_value = _get_default_value(field_info)

    field_alias = extra.get(ParamType.QUERY) or field_name
    param_type = getattr(field_info, "in_", ParamType.QUERY)
    param: Union[Path, Header, Cookie, Query]

    if field_name in path_parameters:
        field_alias = field_name
        param_type = ParamType.PATH
        param = Path(default=default_value)
    elif extra.get(ParamType.HEADER):
        field_alias = extra[ParamType.HEADER]
        param_type = ParamType.HEADER
        param = Header(default=default_value)
    elif extra.get(ParamType.COOKIE):
        field_alias = extra[ParamType.COOKIE]
        param_type = ParamType.COOKIE
        param = Cookie(default=default_value)
    else:
        # Checking if the value should go to body or query params
        param = Query(default=default_value)

    if not field_info.alias:
        field_info.alias = field_name

    for key, _ in param._attributes_set.items():
        setattr(param, key, getattr(field_info, key, None))

    param_settings = ParamSetting(
        param_type=param_type,
        field_alias=field_alias,
        default_value=default_value,
        field_name=field_name,
        field_info=param,
        is_required=is_required and (default_value is None and not allow_none),
        is_security=is_security,
        is_requires_dependency=is_requires_dependency,
    )
    return param_settings


def _get_missing_required_params(params: Any, expected: Set[ParamSetting]) -> list[str]:
    """
    Get missing required parameters.

    Args:
        params (Any): Request parameters.
        expected (Set[ParamSetting]): Set of expected parameters.

    Returns:
        list[str]: list of missing required parameters.
    """
    missing_params = []
    for param in expected:
        if param.is_required and param.field_alias not in params:
            missing_params.append(param.field_alias)
    return missing_params


async def get_request_params(
    params: Mapping[Union[int, str], Any] | QueryParam,
    expected: Set[ParamSetting],
    url: URL,
) -> dict[str, Any]:
    """
    Extract and validate request parameters based on expected settings.

    Args:
        params (Mapping | QueryParam): Incoming request parameters.
        expected_params (Set[ParamSetting]): Set of expected parameter definitions.
        url (URL): The request URL, used for error reporting.

    Returns:
        dict[str, Any]: A dictionary of validated and extracted parameter values.

    Raises:
        ValidationErrorException: If required parameters are missing.
    """
    missing = _get_missing_required_params(params, expected)
    if missing:
        raise ValidationErrorException(
            f"Missing required parameter(s): {', '.join(missing)} for URL {url}."
        )

    extracted: dict[str, Any] = {}

    def extract_dict_param(field_alias: str, default: Any) -> dict[str, Any] | Any:
        """
        Extract dictionary-style query parameters from the request.

        This function supports two styles of query parameter encoding for dictionary-like fields:

        1. **Nested keys**: Parameters encoded with square brackets, e.g. `d_value[foo]=1`.
        These are parsed into a dictionary like `{"foo": 1}`.

        2. **Flat key-value pairs**: If the expected parameter is the only one in the request,
        all query parameters are treated as part of the dictionary, e.g.
        `?a_value=true&b_value=false` becomes `{"a_value": "true", "b_value": "false"}`.

        Args:
            field_alias (str): The alias used to identify the dictionary field in the query string.
            default (Any): The default value to return if no matching parameters are found.

        Returns:
            dict[str, Any]: A dictionary constructed from matching query parameters,
                            or the default value if none are found.
        """
        prefix = f"{field_alias}["
        nested = {
            key[len(prefix) : -1]: value  # type: ignore
            for key, value in params.items()
            if key.startswith(prefix) and key.endswith("]")
        }
        if nested:
            return nested

        if len(expected) == 1:
            return dict(params.items()) if params else default

        return default

    def get_param_value(
        origin_type: Any,
        field_name: str,
        field_alias: str,
        default: Any,
    ) -> Any:
        """
        Resolve the value of a request parameter based on its expected type.

        Args:
            origin_type (Any): The resolved origin type of the parameter annotation.
            field_name (str): The name of the parameter field.
            field_alias (str): The alias used to look up the parameter in the request.
            default (Any): The default value to use if the parameter is not provided.

        Returns:
            Any: The extracted value from the request parameters, or the default if not found.

        Notes:
            - If the parameter is a list or tuple, all values are retrieved using `getall`.
            - If the parameter is a dictionary, all items are returned as a dict.
            - Otherwise, a single value is retrieved using `get`, falling back to the default.
        """

        if is_class_and_subclass(origin_type, (list, tuple)):
            return params.getall(field_name, None)
        elif is_class_and_subclass(origin_type, dict):
            return extract_dict_param(field_alias, default)
        else:
            return params.get(field_alias, default)

    for param in expected:
        field_name = param.field_name
        field_alias = param.field_alias
        annotation = param.field_info.annotation
        default = param.default_value

        if is_requires(default):
            """
            Checks if the default value is a Requires instance.
            """
            extracted[field_name] = default
            continue

        origin = get_origin(annotation) or annotation

        if is_union(annotation):
            union_args = get_args(annotation)
            if any(
                is_class_and_subclass(get_origin(arg) or arg, (list, tuple)) for arg in union_args
            ):
                extracted[field_name] = params.getall(field_name, None)
            elif any(is_class_and_subclass(get_origin(arg) or arg, dict) for arg in union_args):
                extracted[field_name] = extract_dict_param(field_alias, default)
            else:
                extracted[field_name] = params.get(field_alias, default)
        else:
            extracted[field_name] = get_param_value(origin, field_name, field_alias, default)

    return extracted


def get_connection_info(connection: "ConnectionType") -> Tuple[str, "URL"]:
    """
    Extacts the information from the ConnectionType.
    """
    method = connection.method if isinstance(connection, Request) else ScopeType.WEBSOCKET
    return method, connection.url


def get_signature(value: Any) -> Type["SignatureModel"]:
    try:
        return cast("Type[SignatureModel]", value.signature_model)
    except AttributeError as exc:
        raise ImproperlyConfigured(f"The 'signature' attribute for {value} is not set.") from exc


def get_field_definition_from_param(fn: Callable[..., Any], param: "Parameter") -> Tuple[Any, Any]:
    """
    This method will make sure that __future__ references are resolved by
    the Any type. This is necessary because the signature model will be
    generated before the actual type is resolved.
    """
    annotation: Any | FieldInfo

    if param.optional:
        annotation = should_skip_json_schema(param)
    if isinstance(param.annotation, str):
        try:
            hints = get_type_hints(
                fn, globalns=sys.modules[fn.__module__].__dict__, include_extras=True
            )
            annotation = hints.get(param.param_name)
        except NameError:
            # This is to handle cases where the annotation is a string from the TYPE_CHECKING block
            annotation = Any
    else:
        annotation = param.annotation

    if param.default_defined:
        definition = annotation, param.default
    elif not param.optional:
        definition = annotation, ...
    else:
        definition = annotation, None
    return definition
