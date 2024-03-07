# ruff: noqa: B008
from collections.abc import Sequence

import pytest
from pydantic import NonNegativeInt, ValidationError

from cli import CLI, Argument, Option


def parse_cli(count: int, names: Sequence[str] = ()) -> str:
    return " ".join(list(names) * count)


Count = Argument(annotation=NonNegativeInt)
Names = Option(..., "--name", "-n", annotation=list[str], default_factory=list)


app = CLI(
    name="test-cli",
    help="This is a simple CLI used for testing purposes.",
    validate=True,
)


@app.callback()
def callback():
    pass


# Commands as functions ----------------------------------------------------------------


# Using standard 'Typer' approach
@app.command("function_typer", validate=False)
def parse_cli_typer(count: Count.ann = Count, names: Names.ann = Names) -> None:
    print(parse_cli(count, names))


# Using 'CLI' and pydantic validation
@app.command("function")
def parse_cli_validated(count: Count.ann = Count, names: Names.ann = Names) -> None:
    print(parse_cli(count, names))


# Commands as static and class methods -------------------------------------------------


class StaticMethod:
    @app.command("staticmethod")
    @staticmethod
    def command(count: Count.ann = Count, names: Names.ann = Names) -> None:
        print(parse_cli(count, names))


class DerivedStaticMethod(StaticMethod):
    @app.command("derived_staticmethod")
    @staticmethod
    def command(count: Count.ann = Count, names: Names.ann = Names) -> None:
        super(DerivedStaticMethod, DerivedStaticMethod).command(count, names)
        print("I am a subclass!")


class ClassMethod:
    @app.command("classmethod")
    @classmethod
    def command(cls, count: Count.ann = Count, names: Names.ann = Names) -> None:
        print(parse_cli(count, names))


class DerivedClassMethod(ClassMethod):
    @app.command("derived_classmethod")
    @classmethod
    def command(cls, count: Count.ann = Count, names: Names.ann = Names) -> None:
        super().command(count, names)
        print("I am a subclass!")


# Commands as class-bound classmethods -------------------------------------------------

app.command("classmethod_bound")(ClassMethod.command)
app.command("derived_classmethod_bound")(DerivedClassMethod.command)


# Commands as instance-bound methods ---------------------------------------------------


class SomeClass:
    def command(self, count: Count.ann = Count, names: Names.ann = Names) -> None:
        print(parse_cli(count, names))


class SomeDerivedClass(SomeClass):
    def command(self, count: Count.ann = Count, names: Names.ann = Names) -> None:
        super().command(count, names)
        print("I am a subclass!")


inst = SomeClass()
derived_inst = SomeDerivedClass()
app.command("method_bound")(inst.command)
app.command("derive_method_bound")(derived_inst.command)


# Test function ------------------------------------------------------------------------


@pytest.mark.parametrize("command", [c.name for c in app.registered_commands])
@pytest.mark.parametrize("count", [-1, 1])
@pytest.mark.parametrize("names", [None, ["x"], ["x", "y"]])
def test_basic(runner, command: str, count: int, names: list[str] | None) -> None:
    parts = [command]
    if names is not None:
        for name in names:
            parts.extend(["--name", name])
    parts.extend(["--", str(count)])
    command = " ".join(parts)
    results = runner.invoke(app, command, catch_exceptions=True)
    if count < 0 and "typer" not in command:
        assert results.exit_code == 1
        assert isinstance(results.exception, ValidationError)
    elif results.exit_code == 0:
        text, *extra = results.stdout.split("\n")
        text = text.strip()
        # if "typer" in command and text:
        #     assert text != text.upper()
        # else:
        #     assert text == text.upper()
        if extra and (extra := extra.pop()):
            assert extra == "I am a subclass!"
    else:
        pytest.fail("incorrect result")
