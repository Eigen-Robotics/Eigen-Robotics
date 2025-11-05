# drivers_registry.py
from __future__ import annotations
import importlib
from typing import Any
import importlib.util
import sys
from enum import EnumMeta
from pathlib import Path
from typing import Any, Literal, Tuple

def resolve(dotted: str) -> Any:
    """
    Resolve 'package.module:Qual.Name' into the actual object,
    importing the module only when this is called.
    """
    mod_path, _, qualname = dotted.partition(":")
    mod = importlib.import_module(mod_path)
    obj = mod
    if qualname:
        for part in qualname.split("."):
            obj = getattr(obj, part)
    return obj

def try_resolve(dotted: str) -> Any | None:
    try:
        return resolve(dotted)
    except Exception:
        return None

def import_class_from_directory(
    path: Path,
    backend: str | None,
    *,
    raise_on_missing_driver: bool = True,
) -> Tuple[type[Any], Any | None]:
    """
    Load and return a class (and optionally ONE selected driver) from ``path``.

    - Looks for ``<ClassName>.py`` in ``path`` and imports it as module <ClassName>.
    - The main class is the one whose name matches the directory, or (fallback)
      the single non-Drivers class defined in the module.
    - If ``backend`` is provided (e.g., "pybullet", "genesis"), we look for a member of the
      module's ``Drivers`` Enum whose NAME contains that substring (case-insensitive).
      Only that driver's import string is resolved and returned. Others are ignored.

    Returns:
        (target_class, selected_driver_class_or_None)

    Raises:
        FileNotFoundError, ImportError, ValueError
        Additionally, if raise_on_missing_driver=True and the specified backend
        can't be found/resolved, raises ValueError.
    """
    class_name = path.name
    file_path = (path / f"{class_name}.py").resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    module_dir = str(file_path.parent)
    sys.path.insert(0, module_dir)

    try:
        spec = importlib.util.spec_from_file_location(class_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {file_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[class_name] = module
        spec.loader.exec_module(module)  # executes the module

    finally:
        sys.modules.pop(class_name, None)
        sys.path.pop(0)

    # --- Discover the main class exported by the module ---
    class_candidates = [
        obj
        for obj in vars(module).values()
        if isinstance(obj, type) and obj.__module__ == module.__name__
    ]

    target_class = next((cls for cls in class_candidates if cls.__name__ == class_name), None)
    if target_class is None:
        non_driver_classes = [cls for cls in class_candidates if cls.__name__ != "Drivers"]
        if len(non_driver_classes) != 1:
            raise ValueError(
                f"Expected a single class definition in {file_path}, found {len(non_driver_classes)}."
            )
        target_class = non_driver_classes[0]

    # --- If a backend is requested, resolve ONLY that driver lazily ---
    selected_driver = None
    if backend:
        drivers_cls = getattr(module, "Drivers", None)
        if isinstance(drivers_cls, EnumMeta):
            backend_key = backend.upper()
            # Find the first enum member whose name contains the backend token (case-insensitive)
            match = next(
                (
                    member
                    for name, member in drivers_cls.__members__.items()
                    if backend_key in name.upper()
                ),
                None,
            )
            if match is not None:
                selected_driver = try_resolve(match.value)  # value must be "pkg.mod:QualName"
                if selected_driver is None and raise_on_missing_driver:
                    raise ValueError(
                        f"Driver for backend '{backend}' found in Drivers enum "
                        f"but could not be imported (value='{match.value}')."
                    )
            elif raise_on_missing_driver:
                raise ValueError(
                    f"No driver matching backend '{backend}' found in Drivers enum. "
                    f"Available: {', '.join(drivers_cls.__members__.keys()) or '(none)'}"
                )
        elif raise_on_missing_driver:
            raise ValueError("Module has no 'Drivers' enum to select a backend from.")

    return target_class, selected_driver