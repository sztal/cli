# ruff: noqa: UP007
import typing
from collections.abc import Callable
from inspect import signature
from types import UnionType
from typing import (  # type: ignore
    Any,
    GenericAlias,  # type: ignore
    Optional,
    Self,
    TypeAlias,
    Union,
    _BaseGenericAlias,  # type: ignore
    _SpecialForm,
)

from typer import Argument, Option
from typer.models import ArgumentInfo as _ArgumentInfo
from typer.models import OptionInfo as _OptionInfo
from typer.models import ParameterInfo
from typing_extensions import TypeAliasType

from .utils import match_signature

_hint_types = [
    type,
    UnionType,
    GenericAlias,
    _BaseGenericAlias,
    _SpecialForm,
    TypeAliasType,
]

_TypeHint: TypeAlias = Union[tuple(_hint_types)]  # type: ignore # noqa


class ParameterInfoExtensionsMixin:
    annotation: _TypeHint

    def __call__(self, *args: Any, **kwargs: Any) -> ParameterInfo:
        typ = typing.cast(type[ParameterInfo], type(self))
        constructor = Argument if issubclass(typ, _ArgumentInfo) else Option
        sig = signature(typing.cast(Callable, constructor))
        all_args = match_signature(sig, *args, **kwargs)
        attrs = {attr: getattr(self, attr) for attr in sig.parameters}
        new_param = typ(**{**attrs, **all_args})  # type: ignore
        for attr in ("field_kwargs", "annotation", "_validator"):
            val = kwargs.get(attr, getattr(self, attr, None))
            setattr(new_param, attr, val)
        return new_param

    @property
    def ann(self) -> _TypeHint:
        return self.annotation

    @classmethod
    def from_param(cls, param: ParameterInfo) -> Self:
        """Construct from an appropriate :class:`typer.models.ParameterInfo` object."""
        if not issubclass(cls, type(param)):
            errmsg = (
                f"cannot create '{cls.__name__}' from "
                f"'{param.__class__.__name__}' instance"
            )
            raise TypeError(errmsg)
        sig = signature(cls)
        kwds = {attr: getattr(param, attr) for attr in sig.parameters}
        return cls(**kwds)

    def validator(self, callback: Callable[..., Any]) -> Callable[..., Any]:
        """Register validator function on the parameter."""
        self.callback: Optional[Callable[..., Any]] = callback
        return callback


class ArgumentInfo(_ArgumentInfo, ParameterInfoExtensionsMixin):
    pass


class OptionInfo(_OptionInfo, ParameterInfoExtensionsMixin):
    pass
