from functools import partial
from typing import Any

import orjson
from lilya.responses import RESPONSE_TRANSFORM_KWARGS


class ORJSONTransformMixin:
    @classmethod
    def transform(cls, value: Any) -> Any:
        """
        The transformation of the data being returned (simplify operation).

        Supports all the default encoders from Lilya and custom from Ravyn.
        """
        transform_kwargs = RESPONSE_TRANSFORM_KWARGS.get()
        if transform_kwargs is None:
            transform_kwargs = {}
        else:
            transform_kwargs = transform_kwargs.copy()
        transform_kwargs.setdefault(
            "json_encode_fn",
            partial(
                orjson.dumps, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_OMIT_MICROSECONDS
            ),
        )
        transform_kwargs.setdefault("post_transform_fn", orjson.loads)

        with cls.with_transform_kwargs(transform_kwargs):
            return super().transform(value)
