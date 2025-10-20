# src/eigen/__init__.py
from __future__ import annotations

import importlib
import importlib.abc
import importlib.util
import sys
from types import ModuleType

__all__ = ["cli", "core", "sim", "robots", "sensors", "types"]

from . import robots
from . import sensors


class _AliasModule(ModuleType):
    """Module proxy that forwards attribute access to the target module."""

    __slots__ = ()

    def __init__(self, alias_name: str, target_name: str, target_module: ModuleType) -> None:
        super().__init__(alias_name, doc=target_module.__doc__)
        self.__dict__["_target_module"] = target_module
        self.__dict__["_target_name"] = target_name
        self.__dict__["__package__"] = alias_name.rpartition(".")[0]
        if hasattr(target_module, "__file__"):
            self.__dict__["__file__"] = target_module.__file__
        if hasattr(target_module, "__path__"):
            self.__dict__["__path__"] = list(target_module.__path__)
        if hasattr(target_module, "__all__"):
            self.__dict__["__all__"] = target_module.__all__

    def __getattr__(self, item: str):
        target_module = self.__dict__["_target_module"]
        try:
            value = getattr(target_module, item)
        except AttributeError as exc:
            target_fullname = f"{self.__dict__['_target_name']}.{item}"
            alias_fullname = f"{self.__name__}.{item}"
            existing_alias = sys.modules.get(alias_fullname)
            if existing_alias is not None:
                value = existing_alias
                self.__dict__[item] = value
                return value
            try:
                target_submodule = importlib.import_module(target_fullname)
            except ModuleNotFoundError:
                raise AttributeError(item) from exc
            alias_module = _AliasModule(alias_fullname, target_fullname, target_submodule)
            alias_module.__loader__ = getattr(target_submodule, "__loader__", None)
            alias_module.__spec__ = getattr(target_submodule, "__spec__", None)
            sys.modules[alias_fullname] = alias_module
            value = alias_module
        self.__dict__[item] = value
        return value

    def __setattr__(self, key: str, value) -> None:
        setattr(self.__dict__["_target_module"], key, value)

    def __delattr__(self, item: str) -> None:
        delattr(self.__dict__["_target_module"], item)

    def __dir__(self) -> list[str]:
        return sorted(set(dir(self.__dict__["_target_module"])))


class _ModuleAliasLoader(importlib.abc.Loader):
    def __init__(self, fullname: str, target_fullname: str) -> None:
        self._fullname = fullname
        self._target_fullname = target_fullname

    def create_module(self, spec):
        target_module = importlib.import_module(self._target_fullname)
        module = _AliasModule(spec.name, self._target_fullname, target_module)
        module.__loader__ = self
        module.__spec__ = spec
        return module

    def exec_module(self, module) -> None:
        sys.modules[self._fullname] = module


class _ModuleAliasFinder(importlib.abc.MetaPathFinder):
    def __init__(self, mapping: dict[str, str]) -> None:
        self._mapping = dict(mapping)

    @property
    def mapping(self) -> dict[str, str]:
        return dict(self._mapping)

    def find_spec(self, fullname, path=None, target=None):
        target_fullname = None
        for alias, mapped in self._mapping.items():
            if fullname == alias or fullname.startswith(alias + "."):
                suffix = fullname[len(alias):]
                target_fullname = mapped + suffix
                break
        if target_fullname is None:
            return None
        target_spec = importlib.util.find_spec(target_fullname)
        if target_spec is None:
            return None
        is_package = target_spec.submodule_search_locations is not None
        loader = _ModuleAliasLoader(fullname, target_fullname)
        spec = importlib.util.spec_from_loader(
            fullname,
            loader,
            origin=target_spec.origin,
            is_package=is_package,
        )
        if is_package:
            spec.submodule_search_locations = target_spec.submodule_search_locations
        return spec


_ALIAS_TARGETS = {
    "eigen.core": "eigen.framework.core",
    "eigen.cli": "eigen.framework.cli",
    "eigen.sim": "eigen.framework.sim",
    "eigen.types": "eigen.framework.types",
}

if not any(isinstance(finder, _ModuleAliasFinder) and finder.mapping == _ALIAS_TARGETS for finder in sys.meta_path):
    sys.meta_path.insert(0, _ModuleAliasFinder(_ALIAS_TARGETS))

core = importlib.import_module("eigen.core")
cli = importlib.import_module("eigen.cli")
sim = importlib.import_module("eigen.sim")
types = importlib.import_module("eigen.types")
