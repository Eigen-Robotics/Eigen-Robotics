"""Tests for the components CLI."""

from typer.testing import CliRunner

from eigen.cli.components import app
from eigen.core.system.component_registry import (
    ComponentSpec,
    ComponentType,
    _component_registry,
    _register_default_component,
    register_component,
)
from eigen.core.system.driver import RobotDriver, SensorDriver


class TestComponentsCLI:
    """Test the components CLI commands."""

    def setup_method(self):
        """Clear registry before each test."""
        _component_registry.clear()
        self.runner = CliRunner()

    def teardown_method(self):
        """Clear registry after each test."""
        _component_registry.clear()

    def test_list_command_exists(self):
        """Test that the list command is available."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "List all registered components" in result.stdout

    def test_list_empty_registry(self):
        """Test listing components when registry is empty."""
        result = self.runner.invoke(
            app, ["--no-discovery"]
        )  # Skip auto-discovery for test
        assert result.exit_code == 0
        assert "No components registered" in result.stdout

    def test_list_with_registered_components(self):
        """Test listing components with both default and custom components registered."""

        # Register a default component
        @_register_default_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id="franka-base",
                is_driver=True,
            )
        )
        class DefaultFrankaDriver(RobotDriver):
            pass

        # Register a custom (non-default) component
        @register_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id="franka-custom",
                is_driver=False,
            )
        )
        class CustomFrankaRobot:
            pass

        # Register another custom driver
        @register_component(
            ComponentSpec(
                component_type=ComponentType.SENSOR,
                id="lidar-custom",
                is_driver=True,
            )
        )
        class CustomLidarDriver(SensorDriver):
            pass

        result = self.runner.invoke(app, ["--no-discovery"])

        assert result.exit_code == 0

        # Check that the table is displayed
        assert "Registered Components" in result.stdout

        # Check that all components are listed
        assert "franka-base" in result.stdout
        assert "franka-custom" in result.stdout
        assert "lidar-custom" in result.stdout

        # Check component types
        assert "robot" in result.stdout
        assert "sensor" in result.stdout

        # Check driver status (using ✓ and ✗ symbols)
        lines = result.stdout.split("\n")

        # Find lines containing our components and verify their properties
        franka_base_line = next(line for line in lines if "franka-base" in line)
        assert "robot" in franka_base_line
        assert "✓" in franka_base_line  # is_driver = True
        assert (
            franka_base_line.count("✓") == 2
        )  # is_driver=True, is_default=True

        franka_custom_line = next(
            line for line in lines if "franka-custom" in line
        )
        assert "robot" in franka_custom_line
        assert "✗" in franka_custom_line  # is_driver = False

        lidar_custom_line = next(
            line for line in lines if "lidar-custom" in line
        )
        assert "sensor" in lidar_custom_line
        # Should have ✓ for is_driver and ✗ for is_default
        assert lidar_custom_line.count("✓") == 1  # is_driver=True
        assert lidar_custom_line.count("✗") == 1  # is_default=False

    def test_list_components_sorted_by_id(self):
        """Test that components are sorted by ID."""

        # Register components in non-alphabetical order
        @register_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id="zebra-custom",
                is_driver=False,
            )
        )
        class ZebraRobot:
            pass

        @register_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id="alpha-custom",
                is_driver=False,
            )
        )
        class AlphaRobot:
            pass

        result = self.runner.invoke(app, ["--no-discovery"])

        assert result.exit_code == 0

        # Find the positions of the component IDs in the output
        alpha_pos = result.stdout.find("alpha-custom")
        zebra_pos = result.stdout.find("zebra-custom")

        # Alpha should come before Zebra (sorted order)
        assert alpha_pos < zebra_pos

    def test_list_mixed_component_types(self):
        """Test listing with different component types (robot, sensor, object)."""

        @register_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id="robot-custom",
                is_driver=True,
            )
        )
        class TestRobotDriver(RobotDriver):
            pass

        @register_component(
            ComponentSpec(
                component_type=ComponentType.SENSOR,
                id="sensor-custom",
                is_driver=True,
            )
        )
        class TestSensorDriver(SensorDriver):
            pass

        @register_component(
            ComponentSpec(
                component_type=ComponentType.OBJECT,
                id="object-custom",
                is_driver=False,
            )
        )
        class TestObjectComponent:
            pass

        result = self.runner.invoke(app, ["--no-discovery"])

        assert result.exit_code == 0
        assert "robot-custom" in result.stdout
        assert "sensor-custom" in result.stdout
        assert "object-custom" in result.stdout
        assert "robot" in result.stdout
        assert "sensor" in result.stdout
        assert "object" in result.stdout
