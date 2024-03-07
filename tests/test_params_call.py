import pytest

from cli import CLI
from cli.params import Argument, Option

app = CLI()

Arg1 = Argument(1, annotation=int)
Arg2 = Arg1("x1", annotation=str)

Opt1 = Option(1, annotation=int)
Opt2 = Option("x1", annotation=str)


@app.command("arg-command1")
def arg_command1(x: Arg1.ann = Arg1) -> None:
    print(x)


@app.command("arg-command2")
def arg_command2(x: Arg2.ann = Arg2) -> None:
    print(x)


@app.command("opt-command1")
def opt_command1(x: Opt1.ann = Opt1) -> None:
    print(x)


@app.command("opt-command2")
def opt_command2(x: Opt2.ann = Opt2) -> None:
    print(x)


@pytest.mark.parametrize("command", [c.name for c in app.registered_commands])
def test_params_call(runner, command: str):
    results = runner.invoke(app, command)
    assert results.exit_code == 0
    if command.endswith("command1"):
        assert results.stdout.strip() == "1"
    elif command.endswith("command2"):
        assert results.stdout.strip() == "x1"
