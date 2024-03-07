# type: ignore
import nox

session_opts = {"python": ["3.11", "3.12"], "venv_backend": "conda"}


@nox.session(**session_opts)
def lint(session: nox.Session) -> None:
    session.install(".[lint]")
    session.run("ruff", "check", "cli")


@nox.session(**session_opts)
def mypy(session: nox.Session) -> None:
    session.install(".[mypy]")
    session.run("mypy", "cli")


@nox.session(**session_opts)
def test(session: nox.Session) -> None:
    session.install(".[test]")
    session.run("pytest")
