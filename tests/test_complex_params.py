# type: ignore
# ruff: noqa: B008
import json
from typing import Annotated

import pytest
from pydantic import Json, PositiveInt, ValidationError

from cli import CLI, Argument, Option, Parse

app = CLI(validate=True)


@app.callback()
def callback():
    pass


@app.command("command")
def command(
    data: Annotated[list[str], Parse(list[Json])] = Argument(),
    numbers: Annotated[list[int], Parse(set[PositiveInt])] | None = Option(
        None, "--number", "-n"
    ),
) -> None:
    print(data)
    print(numbers)


@pytest.mark.parametrize("data", [['{"a": 1}'], ['{"a": 1, "b": [1, 2]}', "[1,2]"]])
@pytest.mark.parametrize("numbers", [[], [1], [1, 2], [2, 2], [2, -1]])
def test_complex_params(runner, data: list[str], numbers: list[int]):
    parts = ["command"]
    parts.extend(f"""'{d}'""" for d in data)
    parts.extend(f" -n {n}" for n in numbers)
    command = " ".join(parts)
    results = runner.invoke(app, command)
    if any(n <= 0 for n in numbers):
        assert results.exit_code == 1
        assert isinstance(results.exception, ValidationError)
    else:
        assert results.exit_code == 0
        data = list(map(json.loads, data))
        out_data, out_numbers = list(map(eval, results.stdout.strip().split("\n")))
        assert data == out_data
        assert out_numbers == set(numbers)
