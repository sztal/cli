from typing import Annotated

import pytest
from pydantic import PositiveInt, ValidationError

from cli import CLI, Parse

app = CLI()


@app.command("command")
def command(name: str, x: Annotated[int, Parse(PositiveInt)] = 1) -> None:
    print(f"{name} " * x)


@pytest.mark.parametrize("x", [None, 2, -1])
def test_simple_command(runner, x: int | None):
    command = "Hej!"
    if x is not None:
        command += f" {x}"
    results = runner.invoke(app, command, catch_exceptions=False)
    if results.exit_code == 0:
        assert results.stdout.strip().startswith("Hej!")
    elif results.exit_code == 1:
        assert isinstance(results.exception, ValidationError)
