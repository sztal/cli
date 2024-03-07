from collections.abc import Callable
from inspect import Signature, signature
from typing import Any

from typer import Option

from .main import Context


def pdb_callback(
    ctx: Context,
    pdb: bool = Option(  # type: ignore
        False, help="Jump into PDB post-mortem session on error.", is_eager=True
    ),
) -> None:
    if pdb:
        ctx.obj.pdb = True


def match_signature(
    sig: Signature | Callable[..., Any], *args: Any, **kwargs: Any
) -> dict[str, Any]:
    """Match arguments to the signature of a callable."""
    if not isinstance(sig, Signature):
        sig = signature(sig)
    posargs = sig.bind(*args).arguments if args else {}
    kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return {**posargs, **kwargs}  # type: ignore
