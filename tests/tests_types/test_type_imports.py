from __future__ import annotations

from pathlib import Path
import sys

import pytest

# The generated LCM modules expect to be importable from the Python path
GENERATED_DIR = Path(__file__).resolve().parents[2] / "src" / "eigen" / "types" / "generated"
if str(GENERATED_DIR) not in sys.path:
    sys.path.insert(0, str(GENERATED_DIR))

from eigen.types import generated  # noqa: E402


@pytest.mark.parametrize(
    "type_name",
    ["float32_multi_array_t", "multi_array_layout_t", "multi_array_dimension_t"],
)
def test_type_exports_are_classes(type_name: str) -> None:
    attr = getattr(generated, type_name, None)
    assert attr is not None, f"{type_name} missing from eigen.types.generated"
    assert attr.__name__ == type_name
