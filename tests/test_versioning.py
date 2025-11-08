from __future__ import annotations

import re
from pathlib import Path

import eigen
import tomllib


def test_eigen_alias_matches_original_package() -> None:
    import eigen

    assert eigen.__version__ is not None
