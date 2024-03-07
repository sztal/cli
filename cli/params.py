# ruff: noqa: UP007
from collections.abc import Callable
from functools import wraps
from inspect import signature
from typing import Any, Optional

from pydantic import Field
from typer.models import ParameterInfo
from typer.params import Argument as TyperArgument
from typer.params import Option as TyperOption

from .models import ArgumentInfo, OptionInfo, _TypeHint

__all__ = ("Argument", "Option", "Parse")


class Parse:
    """Command-line parse type marker.

    Attributes
    ----------
    ann
        Type annotation.
    """

    def __init__(self, ann: _TypeHint) -> None:
        self.ann = ann

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.ann})"


@wraps(TyperArgument)
def Argument(
    default: Optional[Any] = Ellipsis,
    *,
    annotation: _TypeHint | None = None,
    **kwargs: Any,
) -> ArgumentInfo:
    arg_kwargs, field_kwargs = _separate_kwargs(TyperArgument, **kwargs)
    arg = TyperArgument(default, **arg_kwargs)
    arg = ArgumentInfo.from_param(arg)
    arg.field_kwargs = field_kwargs  # type: ignore
    arg.annotation = annotation  # type: ignore
    return arg


@wraps(TyperOption)
def Option(
    default: Optional[Any] = Ellipsis,
    *param_decls: str,
    annotation: _TypeHint | None = None,
    **kwargs: Any,
) -> OptionInfo:
    opt_kwargs, field_kwargs = _separate_kwargs(TyperOption, **kwargs)
    opt = TyperOption(default, *param_decls, **opt_kwargs)
    opt = OptionInfo.from_param(opt)
    opt.field_kwargs = field_kwargs  # type: ignore
    opt.annotation = annotation  # type: ignore
    return opt


# Internals ----------------------------------------------------------------------------


def _separate_kwargs(
    param_func: Callable[..., ParameterInfo], **kwargs: Any
) -> tuple[dict[str, Any], dict[str, Any]]:
    param_params = list(signature(param_func).parameters)
    field_params = list(signature(Field).parameters)
    field_kwargs = {k: v for k, v in kwargs.items() if k in field_params}
    param_kwargs = {k: v for k, v in kwargs.items() if k in param_params}
    allowed_kwargs = {*field_kwargs, *param_params}
    for key in kwargs:
        if key not in allowed_kwargs:
            errmsg = (
                f"{param_func.__name__}() got an unexpected keyword argument '{key}'"
            )
            raise TypeError(errmsg)

    _remap = {"description": "help"}
    for fname, tname in _remap.items():
        if fname not in field_kwargs and tname in param_kwargs:
            field_kwargs[fname] = param_kwargs[tname]

    return param_kwargs, field_kwargs
