# type: ignore
from typing import Any

import pytest

from cli import CLI, Argument

app = CLI(validate=True)


@app.callback()
def callback():
    pass


@app.command("function")
def command(x: int = Argument(1), y: int = Argument(2)) -> None:
    print(x, y)


@command.validator(mode="after")
def validate(obj: Any) -> Any:
    obj.x *= obj.y
    return obj


class StaticMethod:
    @app.command("staticmethod")
    @staticmethod
    def command(x: int = Argument(1), y: int = Argument(2)) -> None:
        print(x, y)

    @command.validator(mode="after")
    def validate(cls, obj: Any) -> Any:
        obj.x *= obj.y
        return obj


class ClassMethod:
    @app.command("classmethod")
    @classmethod
    def command(cls, x: int = Argument(1), y: int = Argument(2)) -> None:
        print(x, y)

    @command.validator(mode="before")
    @classmethod
    def validate(cls, obj: dict[str, Any]) -> dict[str, Any]:
        obj["x"] *= obj["y"]
        return obj


class DerivedClassMethod(ClassMethod):
    @app.command("classmethod_derived")
    @classmethod
    def command(cls, x: int = Argument(1), y: int = Argument(2)) -> None:
        super().command(x, y)


@pytest.mark.parametrize("command", [c.name for c in app.registered_commands])
def test_command_validators(runner, command: str):
    results = runner.invoke(app, command)
    results = runner.invoke(app, command)
    assert results.exit_code == 0
    assert results.stdout.strip() == "2 2"
