from cli import CLI, Argument

app = CLI(validate=True)

Arg1 = Argument(2, annotation=int)
Arg1.validator(lambda x: x * 2)
Arg2 = Arg1()


@Arg2.validator  # type: ignore
def triple(x):
    return x * 3


@app.command("command")
def command(x1: Arg1.ann = Arg1, x2: Arg2.ann = Arg2) -> None:
    print(x1, x2)


def test_param_validators(runner):
    results = runner.invoke(app, catch_exceptions=False)
    assert results.exit_code == 0
    assert results.stdout.strip() == "4 6"
