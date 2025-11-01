from __future__ import annotations

from copy import deepcopy
from typing import Any, MutableMapping

Json = dict[str, Any] | list[Any] | str | int | float | bool | None


def _fix_additional_properties(node: Json) -> None:
    if isinstance(node, dict):
        if node.get("type") == "object":
            ap = node.get("additionalProperties", None)
            if ap == {}:
                node["additionalProperties"] = True

        # Recurse into possible nested schema containers
        if isinstance(node.get("items"), dict):
            _fix_additional_properties(node["items"])
        ap_val = node.get("additionalProperties")
        if isinstance(ap_val, dict):
            _fix_additional_properties(ap_val)
        for key in ("anyOf", "oneOf", "allOf"):
            if isinstance(node.get(key), list):
                for sub in node[key]:
                    _fix_additional_properties(sub)


def _strip_null_anyof_for_params(param: MutableMapping[str, Any]) -> None:
    """
    For OpenAPI parameter objects only, remove 'null' alternatives from anyOf/oneOf.
    Optionality for parameters is expressed via `required: false`, not via nullable schemas.
    """
    schema = param.get("schema")
    if not isinstance(schema, dict):
        return

    # Remove {"type": "null"} branches
    for key in ("anyOf", "oneOf"):
        if isinstance(schema.get(key), list):
            without_null = [
                x for x in schema[key] if not (isinstance(x, dict) and x.get("type") == "null")
            ]
            if len(without_null) == 1:
                # collapse to the single schema
                param["schema"] = without_null[0]
            else:
                schema[key] = without_null

    # Keep titles if Pydantic dropped them during collapse
    if "title" not in param.get("schema", {}) and "title" in schema:
        param["schema"]["title"] = schema["title"]


def normalize_openapi(doc: dict[str, Any]) -> dict[str, Any]:
    """
    Return a normalized copy of an OpenAPI JSON for comparison in tests.
    Safe normalizations:
      - parameters: remove null branches from anyOf/oneOf
      - schemas anywhere: treat additionalProperties:{} as True
    """
    out = deepcopy(doc)

    # Normalize parameter schemas under paths/*/*/parameters[*]
    paths = out.get("paths", {})
    if isinstance(paths, dict):
        for _path, ops in paths.items():
            if not isinstance(ops, dict):
                continue
            for _method, op in ops.items():
                if not isinstance(op, dict):
                    continue
                params = op.get("parameters")
                if isinstance(params, list):
                    for p in params:
                        if isinstance(p, dict):
                            _strip_null_anyof_for_params(p)

    # Normalize additionalProperties throughout the document
    def walk(node: Json) -> None:
        if isinstance(node, dict):
            _fix_additional_properties(node)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(out)
    return out
