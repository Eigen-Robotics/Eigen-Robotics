from eigen.core.config_utils.load_config import load_config
from omegaconf import DictConfig

def test_whole_config():
    cfg = load_config("tests/test_core_lib/test_config_utils/configs/whole_config/global_config.yaml")


    assert isinstance(cfg, DictConfig)

    assert cfg.network is not None
    assert cfg.simulator is not None

    assert cfg.network.registry_host == "127.0.0.1"
    assert cfg.network.registry_port == 1234
    assert cfg.network.lcm_network_bounces == 1


def test_nested_config():
    cfg = load_config("tests/test_core_lib/test_config_utils/configs/nested_config/global_config.yaml")

    assert isinstance(cfg, DictConfig)

    assert cfg.network is not None
    assert cfg.simulator is not None

    assert cfg.network.registry_host == "127.0.0.1"
    assert cfg.network.registry_port == 1234
    assert cfg.network.lcm_network_bounces == 1


# TODO: Add test inline config of type dict and of type Path