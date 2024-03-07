from importlib.metadata import PackageNotFoundError, version

__version__: str | None
try:
    __version__ = version("cli")
except PackageNotFoundError:
    # package is not properly installed
    __version__ = None
