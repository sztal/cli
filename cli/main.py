# ruff: noqa: UP007
# pyright: reportArgumentType=false
# mypy: disable-error-code="assignment"
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any, Optional

from typer import Context, Exit, Typer  # noqa
from typer.models import CommandFunctionType, DefaultPlaceholder

from .commands import CommandDescriptor

__all__ = ("CLI",)


class CLI(Typer):
    """Command-line interface class.

    This is a simple wrapper around :class:`typer.Typer`,
    which provides an extra method for registering commands
    defined in submodules.
    """

    # ruff: noqa: B008
    def __init__(
        self,
        *args: Any,
        context_settings: dict[Any, Any] = DefaultPlaceholder(None),
        validate: bool = True,
        allow_pdb: bool = True,
        **kwargs: Any,
    ) -> None:
        context_settings = context_settings or {}
        context_settings["obj"] = SimpleNamespace(**context_settings.get("obj", {}))
        super().__init__(
            *args,
            context_settings=context_settings,
            **kwargs,
        )
        self.validate = validate
        self.allow_pdb = allow_pdb

    def command(  # type: ignore
        self,
        name: Optional[str] = None,
        *,
        validate: Optional[bool] = None,
        allow_pdb: Optional[bool] = None,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], CommandDescriptor]:
        """Register command.

        Parameters
        ----------
        name
            Command name.
        validate
            Enable :mod:`pydantic` validation.
            Defaults ``self.validation`` when ``None``.
        allow_pdb
            Enable command post-mortem debugging.
            Defaults to ``self.allow_pdb`` when ``None``.
        **kwargs
            Passed to :meth:`typer.Typer.command`.
        """
        validate = self.validate if validate is None else validate
        allow_pdb = self.allow_pdb if allow_pdb is None else allow_pdb
        parent_decorator = super().command(name, **kwargs)
        return self._command(parent_decorator, validate=validate, allow_pdb=allow_pdb)

    def _command(
        self,
        parent_decorator: Callable[[CommandFunctionType], CommandFunctionType],
        **kwds: Any,
    ) -> Callable[[CommandFunctionType], CommandDescriptor]:
        def decorator(func: CommandFunctionType) -> CommandDescriptor:
            return CommandDescriptor(func, parent_decorator, **kwds)

        return decorator
