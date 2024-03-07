# ruff: noqa: UP007
# pyright: reportArgumentType=false
# mypy: disable-error-code="assignment"
import typing
from collections.abc import Callable
from functools import wraps
from inspect import Parameter, signature
from types import UnionType
from typing import (  # type: ignore
    Any,
    Union,
    _UnionGenericAlias,  # type: ignore
)

from pydantic import BaseModel, ConfigDict, Field, create_model, model_validator
from pydantic.alias_generators import to_pascal
from pydantic.fields import FieldInfo
from typer.models import CommandFunctionType
from typing_extensions import _AnnotatedAlias

from .decorators import debuggable, validated_with  # type: ignore
from .params import Parse, _TypeHint


class CommandDescriptor:
    def __init__(
        self,
        func: Callable[..., Any] | classmethod,
        command_decorator: Callable[[CommandFunctionType], CommandFunctionType],
        *,
        validate: bool = True,
        allow_pdb: bool = True,
    ) -> None:
        self.func = func
        self.command_decorator = command_decorator
        self.name: str | None = None
        self.owner: type | None = None
        self.validate = validate
        self.allow_pdb = allow_pdb
        self.__validators__: dict[str, Callable[..., Any]] | None = None

        if not isinstance(self.func, classmethod):
            func = self._decorate(self.func)
            func = typing.cast(CommandFunctionType, func)
            self.command_decorator(func)

    def __get__(self, obj: object, cls: type | None = None) -> Callable[..., Any]:
        func = self.func
        if isinstance(func, classmethod):
            if cls is None:
                cls = type(obj)
            func = self.func.__get__(None, cls)
        return self._decorate(func)

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
        self.owner = owner
        if isinstance(self.func, classmethod):
            callback = getattr(owner, name)
            self.command_decorator(callback)

    def validator(
        self, **kwargs: Any
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            if not self.validate:
                errmsg = "cannot set validator on command with 'validate=False'"
                raise TypeError(errmsg)
            self.__validators__ = {
                "__command_validator__": model_validator(**kwargs)(func)
            }
            return func

        return decorator

    def _decorate(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def decorated(*args: Any, **kwds: Any) -> Any:
            nonlocal func
            local_func = typing.cast(Callable, func)
            if self.validate:
                model = self._create_model()
                local_func = validated_with(model)(local_func)
            if self.allow_pdb:
                local_func = debuggable(local_func)
            return local_func(*args, **kwds)

        return decorated

    def _create_model(self) -> type[BaseModel]:
        func = self.func.__func__ if isinstance(self.func, classmethod) else self.func
        func = typing.cast(Callable, func)
        func_sig = signature(func)
        fields = {
            name: self._get_field_spec(param)
            for name, param in func_sig.parameters.items()
            if name in self.func.__annotations__
        }
        mconf = ConfigDict(
            arbitrary_types_allowed=True,
        )
        mname = f"{to_pascal(self.func.__name__)}Model"

        return create_model(  # type: ignore
            mname, **fields, __config__=mconf, __validators__=self.__validators__
        )

    def _get_field_spec(self, param: Parameter) -> tuple[_TypeHint, FieldInfo]:
        def _get_input_ann(ann: _TypeHint) -> _TypeHint:
            if isinstance(ann, _AnnotatedAlias):
                for obj in ann.__metadata__:
                    if isinstance(obj, Parse):
                        ann = obj.ann
                        break
            return ann

        ann = _get_input_ann(param.annotation)
        if isinstance(ann, UnionType | _UnionGenericAlias):
            ann = Union[*tuple(_get_input_ann(a) for a in ann.__args__)]  # type: ignore
        return ann, Field(**getattr(param.default, "field_kwargs", {}))
