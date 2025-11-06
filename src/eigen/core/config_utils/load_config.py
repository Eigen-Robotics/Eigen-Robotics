from pathlib import Path
from omegaconf import OmegaConf, DictConfig

from eigen.core.tools import log

def _load_yaml_cfg(path: Path) -> DictConfig:
    """Load a single YAML file into an OmegaConf DictConfig.

    Always returns a DictConfig, logging an error and returning an empty one on failure.
    """
    try:
        cfg = OmegaConf.load(path)

        if not isinstance(cfg, DictConfig):
            raise TypeError(
                f"Expected DictConfig but got {type(cfg).__name__}"
            )
        return cfg

    except Exception as e:
        log.error(f"Failed to load YAML config {path}: {e}")
        return OmegaConf.create({})


def _resolve_nested_configs(
    cfg: DictConfig,
    base_dir: Path,
    seen: set[Path],
    max_depth: int = 20,
    depth: int = 0,
) -> DictConfig:
    """Recursively resolve any YAML-path references inside a config."""
    if depth > max_depth:
        log.error(f"Maximum config nesting depth ({max_depth}) exceeded.")
        return cfg

    for key, value in list(cfg.items()):
        # Nested mapping → recurse
        if isinstance(value, DictConfig):
            cfg[key] = _resolve_nested_configs(value, base_dir, seen, max_depth, depth + 1)

        # String → maybe a YAML file path
        elif isinstance(value, str) and value.endswith((".yml", ".yaml")):
            sub_path = (base_dir / value).resolve()

            if sub_path in seen:
                log.error(f"Detected config include cycle at {sub_path}, skipping.")
                cfg[key] = {}
                continue

            if not sub_path.exists():
                log.error(f"Referenced config does not exist: {sub_path}")
                cfg[key] = {}
                continue

            seen.add(sub_path)
            sub_cfg = _load_yaml_cfg(sub_path)
            sub_cfg = _resolve_nested_configs(
                sub_cfg, sub_path.parent, seen, max_depth, depth + 1
            )
            cfg[key] = sub_cfg

        # Otherwise leave as-is

    return cfg


def _load_composed_config(path: str | Path) -> DictConfig:
    """Load a YAML config where values can point to other YAMLs (infinitely nested)."""
    path = Path(path).resolve()

    if not path.exists():
        log.error(f"Config file not found: {path}")
        return OmegaConf.create({})

    root_cfg = _load_yaml_cfg(path)
    seen = {path}

    resolved_cfg = _resolve_nested_configs(root_cfg, path.parent, seen)
    OmegaConf.resolve(resolved_cfg)
    log.info(f"Loaded composed config: {path}")

    return resolved_cfg

def load_config(global_config: dict | str | Path | None = None) -> DictConfig:
    """Load configuration from a YAML file path, dictionary, or None.

    Args:
        global_config: A dict (already loaded config), a string path, a Path object,
                       or None.

    Returns:
        A dictionary containing the loaded configuration, or an empty dict on failure.
    """
    # Case 1: Already a dictionary
    if isinstance(global_config, dict):
        return OmegaConf.create(global_config)

    # Case 2: String path → convert to Path
    if isinstance(global_config, str):
        global_config = Path(global_config)

    # Case 3: Path object → load YAML
    if isinstance(global_config, Path):
        if not global_config.exists():
            log.error(f"Config file not found: {global_config}")
            return OmegaConf.create({})

        try:
            # Normalize path (resolve relative -> absolute)
            global_config = global_config.resolve()
        except Exception as e:
            log.error(f"Failed to resolve config path {global_config}: {e}")
            return OmegaConf.create({})

        try:
            # Delegate to your composed loader (OmegaConf or YAML)
            return _load_composed_config(global_config)
        except Exception as e:
            log.error(f"Error loading config from {global_config}: {e}")
            return OmegaConf.create({})

    # Case 4: None → use default / empty
    if global_config is None:
        log.warning("No global configuration provided. Using empty default config.")
        return OmegaConf.create({})

    # Case 5: Invalid type
    log.error(
        f"Invalid type for global_config ({type(global_config)}). "
        "Must be dict, str, Path, or None."
    )
    return OmegaConf.create({})