# type: ignore
import pytest

from cli import CLI, Context, Option
from cli.utils import pdb_callback

app = CLI(allow_pdb=True)


@app.callback()
def callback(ctx: Context, pdb: bool = Option(False)) -> None:
    pdb_callback(ctx, pdb)
    if pdb and ctx.obj.pdb:
        print("pdb on")


@app.command("bad-command")
def bad_command() -> None:
    print(1 / 0)


@pytest.mark.parametrize("pdb", [False, True])
def test_pdb(runner, pdb: bool) -> None:
    command = "--pdb bad-command" if pdb else "bad-command"
    result = runner.invoke(app, command, catch_exceptions=True)
    assert isinstance(result.exception, ZeroDivisionError)
    if pdb:
        assert result.stdout.strip().startswith("pdb on")
