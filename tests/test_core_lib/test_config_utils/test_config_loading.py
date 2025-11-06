from pathlib import Path
from omegaconf import DictConfig
from eigen.core.config_utils.load_config import load_config

# --- Utility function for reuse ---
def assert_network_cfg(cfg, host="127.0.0.1", port=1234, bounces=1):
    """Helper to assert network configuration values."""
    assert isinstance(cfg, DictConfig)
    assert cfg.network is not None
    assert cfg.simulator is not None

    assert cfg.network.registry_host == host
    assert cfg.network.registry_port == port
    assert cfg.network.lcm_network_bounces == bounces


# --- Tests ---
def test_whole_config():
    cfg = load_config("tests/test_core_lib/test_config_utils/configs/whole_config/global_config.yaml")
    assert_network_cfg(cfg)


def test_nested_config():
    cfg = load_config("tests/test_core_lib/test_config_utils/configs/nested_config/global_config.yaml")
    assert_network_cfg(cfg)


def test_inline_dict_config():
    inline_config = {
        "network": {
            "registry_host": "127.0.0.1",
            "registry_port": 1234,
            "lcm_network_bounces": 1,
        },
        "simulator": {"enabled": True},
    }
    cfg = load_config(inline_config)

    assert_network_cfg(cfg)
    assert cfg.simulator.enabled is True


def test_inline_path_config():
    config_path = Path("tests/test_core_lib/test_config_utils/configs/whole_config/global_config.yaml")
    cfg = load_config(config_path)
    assert_network_cfg(cfg)
