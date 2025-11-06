from __future__ import annotations

import re
from pathlib import Path

import eigen as er
import eigen_robotics as er_pkg
import tomllib


def _project_version() -> str:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    return data["project"]["version"]


def test_dunder_version_matches_pyproject() -> None:
    assert er.__version__ == _project_version()


def test_get_version_agrees_with_dunder() -> None:
    assert er.get_version() == er.__version__


def test_version_is_semantic() -> None:
    pattern = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
    assert pattern.match(er.__version__)


def test_eigen_alias_matches_original_package() -> None:
    assert er.__version__ == er_pkg.__version__
    assert er.get_version() == er_pkg.get_version()
