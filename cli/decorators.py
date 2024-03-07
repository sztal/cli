# type: ignore
import sys
import traceback
from collections.abc import Callable
from functools import wraps
from inspect import signature
from typing import Any

import click
from pydantic import BaseModel

from .utils import match_signature

try:
    import ipdb as pdb
except ImportError:
    import pdb


def debuggable(callable: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(callable)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        try:
            return callable(*args, **kwargs)
        except Exception as exc:
            ctx = click.get_current_context()
            if getattr(ctx.obj, "pdb", False):
                *_, tb = sys.exc_info()
                traceback.print_exc()
                pdb.post_mortem(tb)
            raise exc

    return decorated


def validated_with(
    model: type[BaseModel],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func_sig = signature(func)

        @wraps(func)
        def decorated(*args: Any, **kwargs: Any) -> Any:
            all_args = match_signature(func_sig, *args, **kwargs)
            validated_args = {
                k: v for k, v in all_args.items() if k in model.model_fields
            }
            validated_args = dict(model(**validated_args))
            all_args = {**all_args, **validated_args}
            return func(**all_args)

        return decorated

    return decorator
