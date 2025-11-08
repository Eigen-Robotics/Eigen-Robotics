from pathlib import Path

from omegaconf import DictConfig, ListConfig

from eigen.core.config_utils.load_config import get_node_config, load_config

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


def test_missing_config_path_returns_empty(caplog):
    missing_path = Path("tests/test_core_lib/test_config_utils/configs/whole_config/missing.yaml")
    assert not missing_path.exists(), "Missing config unexpectedly exists"

    with caplog.at_level("ERROR"):
        cfg = load_config(missing_path)

    assert len(cfg) == 0
    assert any("Config file not found" in record.message for record in caplog.records)


def test_invalid_config_type_returns_empty(caplog):
    with caplog.at_level("ERROR"):
        cfg = load_config(123)  # type: ignore[arg-type]

    assert len(cfg) == 0
    assert any("Invalid type for global_config" in record.message for record in caplog.records)


def test_none_config_logs_warning(caplog):
    with caplog.at_level("WARNING"):
        cfg = load_config(None)

    assert len(cfg) == 0
    assert any("No global configuration provided" in record.message for record in caplog.records)


def test_list_based_config_returns_empty(caplog):
    config_path = Path("tests/test_core_lib/test_config_utils/configs/invalid_structure/list_config.yaml")
    with caplog.at_level("ERROR"):
        cfg = load_config(config_path)

    assert len(cfg) == 0
    assert any("Expected DictConfig" in record.message for record in caplog.records)


def test_cycle_detection_replaces_reference_with_empty_mapping(caplog):
    config_path = Path("tests/test_core_lib/test_config_utils/configs/cycle_config/global_config.yaml")
    with caplog.at_level("ERROR"):
        cfg = load_config(config_path)

    assert cfg.network.registry_host == "127.0.0.1"
    loop_value = cfg.network.global_ref
    assert isinstance(loop_value, (DictConfig, dict))
    assert len(loop_value) == 0
    assert any("Detected config include cycle" in record.message for record in caplog.records)

def test_load_node_config():
    base_config = load_config("tests/test_core_lib/test_config_utils/configs/whole_config/global_config.yaml")
    robot_node_config, robot_file = get_node_config("my_robot", "robots", base_config)

    assert isinstance(robot_node_config, DictConfig)
    assert robot_file == "example_file"
    assert robot_node_config.param1 == "value1"
    assert robot_node_config.param2 == 42

    sensor_node_config, sensor_file = get_node_config("camera_sensor", "sensors", base_config)
    assert isinstance(sensor_node_config, DictConfig)
    assert sensor_file == "camera_sensor"
    assert sensor_node_config.resolution == [640, 480]
    assert sensor_node_config.fov == 90

    