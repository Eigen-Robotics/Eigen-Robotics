"""Top-level package for the eigen_robotics project."""

from __future__ import annotations

from importlib import metadata
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from typing import Final

try:
    _version = metadata.version("eigen-robotics")
except PackageNotFoundError:
    project_root = Path(__file__).resolve().parents[2]
    pyproject = project_root / "pyproject.toml"
    if not pyproject.exists():
        raise RuntimeError(
            "Unable to determine package version: pyproject.toml not found"
        ) from None

    try:
        import tomllib
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Python 3.11+ is required to read pyproject.toml for version retrieval"
        ) from exc

    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    _version = data["project"]["version"]

_VERSION: Final[str] = _version
__version__: Final[str] = _VERSION
__all__ = ["__version__", "get_version"]


def get_version() -> str:
    """Return the current package version."""
    return __version__
