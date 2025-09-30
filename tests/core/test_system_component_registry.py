"""Tests for the Eigen component registrations."""

import pytest

from eigen.core.system.component import Robot, Sensor
from eigen.core.system.component_registry import (
    ComponentSpec,
    ComponentType,
    InvalidComponentNameError,
    _component_registry,
    _ComponentKey,
    _register_default_component,
    get_component,
    get_component_pair,
    list_components,
    register_component,
)
from eigen.core.system.driver import ComponentDriver, RobotDriver, SensorDriver


class TestComponentSpec:
    """Test ComponentSpec validation and behavior."""

    @pytest.mark.parametrize(
        "component_type,component_id,is_driver,expected_driver",
        [
            (ComponentType.ROBOT, "franka-base", True, True),
            (ComponentType.SENSOR, "lidar-base", False, False),
            (ComponentType.OBJECT, "object-base", True, True),
            (
                ComponentType.SENSOR,
                "camera-base",
                None,
                False,
            ),  # Test default value
        ],
    )
    def test_valid_component_spec_creation(
        self, component_type, component_id, is_driver, expected_driver
    ):
        """Test that valid ComponentSpec objects can be created."""
        if is_driver is None:
            spec = ComponentSpec(component_type=component_type, id=component_id)
        else:
            spec = ComponentSpec(
                component_type=component_type,
                id=component_id,
                is_driver=is_driver,
            )

        assert spec.component_type == component_type
        assert spec.id == component_id
        assert spec.is_driver is expected_driver

    @pytest.mark.parametrize(
        "valid_id",
        [
            "franka-base",
            "franka_base",
            "sensor-base",
            "lidar-base",
            "camera-base",
            "robot-base",
            "franka-robot",
            "sensor-lidar",
            "camera-intel",
            "simple-name",
            "franka-custom",
            "sensor-experimental",
        ],
    )
    def test_component_id_validation_valid_ids(self, valid_id):
        """Test that valid component IDs are accepted."""
        spec = ComponentSpec(component_type=ComponentType.ROBOT, id=valid_id)
        assert spec.id == valid_id

    @pytest.mark.parametrize(
        "invalid_id,expected_exception",
        [
            ("Franka-base", Exception),  # uppercase
            ("123-robot", Exception),  # starts with number
            ("robot@home", Exception),  # special character
            ("ro", Exception),  # too short
            ("", Exception),  # empty
            ("robot with spaces", Exception),  # spaces
            ("-robot", Exception),  # starts with hyphen
            ("_robot", Exception),  # starts with underscore
            ("a" * 51, ValueError),  # too long (over 50 characters)
            ("base-robot", InvalidComponentNameError),  # base in first part
            ("base-custom", InvalidComponentNameError),  # base in first part
            (
                "base_anything",
                InvalidComponentNameError,
            ),  # base in first part with underscore
        ],
    )
    def test_component_id_validation_invalid_ids(
        self, invalid_id, expected_exception
    ):
        """Test that invalid component IDs are rejected."""
        with pytest.raises(expected_exception):
            ComponentSpec(component_type=ComponentType.ROBOT, id=invalid_id)


class TestComponentRegistration:
    """Test component registration functionality."""

    def setup_method(self):
        """Clear registry before each test."""
        _component_registry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        _component_registry.clear()

    def test_register_robot_driver_success(self):
        """Test successful registration of a robot driver."""

        @register_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id="franka-custom",
                is_driver=True,
            )
        )
        class MockFrankaDriver(RobotDriver):
            pass

        # Verify registration
        retrieved = get_component(
            ComponentType.ROBOT, "franka-custom", is_driver=True
        )
        assert retrieved is MockFrankaDriver

    def test_register_sensor_driver_success(self):
        """Test successful registration of a sensor driver."""

        @register_component(
            ComponentSpec(
                component_type=ComponentType.SENSOR,
                id="lidar-custom",
                is_driver=True,
            )
        )
        class MockLidarDriver(SensorDriver):
            pass

        retrieved = get_component(
            ComponentType.SENSOR, "lidar-custom", is_driver=True
        )
        assert retrieved is MockLidarDriver

    def test_register_component_driver_success(self):
        """Test successful registration of a generic component driver."""

        @register_component(
            ComponentSpec(
                component_type=ComponentType.OBJECT,
                id="object-custom",
                is_driver=True,
            )
        )
        class MockObjectDriver(ComponentDriver):
            pass

        retrieved = get_component(
            ComponentType.OBJECT, "object-custom", is_driver=True
        )
        assert retrieved is MockObjectDriver

    def test_register_non_driver_component(self):
        """Test registration of non-driver components."""

        class MockComponent:
            pass

        @register_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id="franka-custom",
                is_driver=False,
            )
        )
        class MockRobotComponent(MockComponent):
            pass

        retrieved = get_component(
            ComponentType.ROBOT, "franka-custom", is_driver=False
        )
        assert retrieved is MockRobotComponent

    def test_default_component_registration_success(self):
        """Test successful registration of default components with 'base' in ID."""

        @_register_default_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id="franka-base",
                is_driver=True,
            )
        )
        class DefaultFrankaDriver(RobotDriver):
            pass

        # Check that it's registered with is_default=True
        components = list_components()
        default_key = _ComponentKey(
            component_type=ComponentType.ROBOT,
            component_id="franka-base",
            is_driver=True,
            is_default=True,
        )
        assert default_key in components
        assert components[default_key] is DefaultFrankaDriver

    def test_default_component_registration_failure_no_base(self):
        """Test that default component registration fails without 'base' in ID."""
        with pytest.raises(
            InvalidComponentNameError,
            match="Default component ID must contain 'base'",
        ):

            @_register_default_component(
                ComponentSpec(
                    component_type=ComponentType.ROBOT,
                    id="franka-custom",  # No 'base' in ID
                    is_driver=True,
                )
            )
            class InvalidDefaultDriver(RobotDriver):
                pass

    def test_default_component_registration_failure_single_part(self):
        """Test that default component registration fails with single-part ID."""
        with pytest.raises(
            InvalidComponentNameError,
            match="Default component ID must contain 'base'",
        ):

            @_register_default_component(
                ComponentSpec(
                    component_type=ComponentType.ROBOT,
                    id="frankabase",  # Single part, no delimiter
                    is_driver=True,
                )
            )
            class InvalidSinglePartDriver(RobotDriver):
                pass

    def test_non_default_component_registration_failure_with_base(self):
        """Test that non-default component registration fails with 'base' in ID."""
        with pytest.raises(
            InvalidComponentNameError,
            match="Non-default component ID must not contain 'base'",
        ):

            @register_component(
                ComponentSpec(
                    component_type=ComponentType.ROBOT,
                    id="franka-base",  # Contains 'base' - not allowed for non-default
                    is_driver=True,
                )
            )
            class InvalidNonDefaultDriver(RobotDriver):
                pass

    @pytest.mark.parametrize(
        "valid_non_default_id",
        [
            "franka-custom",
            "franka_custom",
            "sensor-custom",
            "lidar-velodyne",
            "camera-realsense",
            "robot-user",
            "franka-01",
            "sensor_v2",
            "franka-production",
            "sensor-experimental",
        ],
    )
    def test_non_default_component_registration_valid_ids(
        self, valid_non_default_id
    ):
        """Test that valid non-default component IDs are accepted (no 'base' allowed)."""

        @register_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id=valid_non_default_id,
                is_driver=True,
            )
        )
        class TestNonDefaultDriver(RobotDriver):
            pass

        # Verify registration succeeded
        retrieved = get_component(
            ComponentType.ROBOT, valid_non_default_id, is_driver=True
        )
        assert retrieved is TestNonDefaultDriver

    @pytest.mark.parametrize(
        "valid_default_id",
        [
            "franka-base",
            "franka_base",
            "sensor-base",
            "lidar-base",
            "camera-base",
            "robot-base",
        ],
    )
    def test_default_component_registration_valid_ids(self, valid_default_id):
        """Test that valid default component IDs with 'base' are accepted."""

        @_register_default_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id=valid_default_id,
                is_driver=True,
            )
        )
        class TestDefaultDriver(RobotDriver):
            pass

        # Verify registration succeeded
        retrieved = get_component(
            ComponentType.ROBOT, valid_default_id, is_driver=True
        )
        assert retrieved is TestDefaultDriver


class TestComponentInheritanceValidation:
    """Test inheritance validation for drivers and components."""

    def setup_method(self):
        """Clear registry before each test."""
        _component_registry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        _component_registry.clear()

    def test_robot_driver_inheritance_validation_success(self):
        """Test that robot drivers must inherit from RobotDriver."""

        @register_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id="franka-01",
                is_driver=True,
            )
        )
        class ValidRobotDriver(RobotDriver):
            pass

        # Should not raise an exception
        assert (
            get_component(ComponentType.ROBOT, "franka-01", is_driver=True)
            is ValidRobotDriver
        )

    def test_robot_driver_inheritance_validation_failure_robot(self):
        """Test that invalid robot driver inheritance is rejected."""
        with pytest.raises(
            TypeError, match="Robot driver .* must inherit from RobotDriver"
        ):

            @register_component(
                ComponentSpec(
                    component_type=ComponentType.ROBOT,
                    id="franka-01",
                    is_driver=True,
                )
            )
            class InvalidRobotDriver(Robot):
                pass

    def test_robot_driver_inheritance_validation_failure_class(self):
        """Test that invalid robot driver inheritance is rejected."""
        with pytest.raises(
            TypeError, match="Robot driver .* must inherit from RobotDriver"
        ):

            @register_component(
                ComponentSpec(
                    component_type=ComponentType.ROBOT,
                    id="franka-01",
                    is_driver=True,
                )
            )
            class InvalidRobotDriver:
                pass

    def test_sensor_driver_inheritance_validation_success(self):
        """Test that sensor drivers must inherit from SensorDriver."""

        @register_component(
            ComponentSpec(
                component_type=ComponentType.SENSOR,
                id="camera-custom",
                is_driver=True,
            )
        )
        class ValidSensorDriver(SensorDriver):
            pass

        assert (
            get_component(ComponentType.SENSOR, "camera-custom", is_driver=True)
            is ValidSensorDriver
        )

    def test_sensor_driver_inheritance_validation_failure(self):
        """Test that invalid sensor driver inheritance is rejected."""
        with pytest.raises(
            TypeError, match="Sensor driver .* must inherit from SensorDriver"
        ):

            @register_component(
                ComponentSpec(
                    component_type=ComponentType.SENSOR,
                    id="camera-custom",
                    is_driver=True,
                )
            )
            class InvalidSensorDriver:
                pass

    def test_object_driver_inheritance_validation_success(self):
        """Test that object drivers must inherit from ComponentDriver."""

        @register_component(
            ComponentSpec(
                component_type=ComponentType.OBJECT,
                id="object-custom",
                is_driver=True,
            )
        )
        class ValidObjectDriver(ComponentDriver):
            pass

        assert (
            get_component(ComponentType.OBJECT, "object-custom", is_driver=True)
            is ValidObjectDriver
        )

    def test_object_driver_inheritance_validation_failure(self):
        """Test that invalid object driver inheritance is rejected."""
        with pytest.raises(
            TypeError,
            match="Object driver .* must inherit from ComponentDriver",
        ):

            @register_component(
                ComponentSpec(
                    component_type=ComponentType.OBJECT,
                    id="object-custom",
                    is_driver=True,
                )
            )
            class InvalidObjectDriver:
                pass

    # Tests for non-driver components
    def test_robot_component_registration_success(self):
        """Test that robot components can be registered (no inheritance validation for non-drivers)."""

        @register_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id="franka-custom",
                is_driver=False,
            )
        )
        class MockRobotComponent(Robot):
            pass

        retrieved = get_component(
            ComponentType.ROBOT, "franka-custom", is_driver=False
        )
        assert retrieved is MockRobotComponent

    def test_sensor_component_registration_success(self):
        """Test that sensor components can be registered (no inheritance validation for non-drivers)."""

        @register_component(
            ComponentSpec(
                component_type=ComponentType.SENSOR,
                id="lidar-custom",
                is_driver=False,
            )
        )
        class MockSensorComponent(Sensor):
            pass

        retrieved = get_component(
            ComponentType.SENSOR, "lidar-custom", is_driver=False
        )
        assert retrieved is MockSensorComponent

    def test_any_class_can_be_non_driver_component(self):
        """Test that any class can be registered as a non-driver component."""

        class AnyClass:
            pass

        @register_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id="robot-custom",
                is_driver=False,
            )
        )
        class AnyRobotComponent(AnyClass):
            pass

        retrieved = get_component(
            ComponentType.ROBOT, "robot-custom", is_driver=False
        )
        assert retrieved is AnyRobotComponent

    @pytest.mark.skip(
        reason="OBJECT component validation might be considered in the future"
    )
    def test_object_component_inheritance_validation_future(self):
        """Test for OBJECT component inheritance - to be implemented in the future."""
        # TODO(FV): Define proper inheritance requirements for OBJECT components
        # This test is skipped as OBJECT component validation is not yet defined
        pass


class TestComponentRetrieval:
    """Test component retrieval functionality."""

    def setup_method(self):
        """Setup test components."""
        _component_registry.clear()

        # Register test components (using non-base names for non-default components)
        @register_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id="franka-custom",
                is_driver=False,
            )
        )
        class MockRobotComponent:
            pass

        @register_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id="franka-custom",
                is_driver=True,
            )
        )
        class MockRobotDriver(RobotDriver):
            pass

        @register_component(
            ComponentSpec(
                component_type=ComponentType.SENSOR,
                id="lidar-custom",
                is_driver=True,
            )
        )
        class MockSensorDriver(SensorDriver):
            pass

        self.robot_component = MockRobotComponent
        self.robot_driver = MockRobotDriver
        self.sensor_driver = MockSensorDriver

    def teardown_method(self):
        """Clear registry after each test."""
        _component_registry.clear()

    def test_get_component_success(self):
        """Test successful component retrieval."""
        component = get_component(
            ComponentType.ROBOT, "franka-custom", is_driver=False
        )
        assert component is self.robot_component

        driver = get_component(
            ComponentType.ROBOT, "franka-custom", is_driver=True
        )
        assert driver is self.robot_driver

    def test_get_component_not_found(self):
        """Test component retrieval when component doesn't exist."""
        component = get_component(
            ComponentType.ROBOT, "nonexistent", is_driver=False
        )
        assert component is None

    def test_get_component_pair_success(self):
        """Test successful retrieval of component-driver pair."""
        component, driver = get_component_pair(
            ComponentType.ROBOT, "franka-custom"
        )
        assert component is self.robot_component
        assert driver is self.robot_driver

    def test_get_component_pair_partial_match(self):
        """Test component pair retrieval when only one exists."""
        component, driver = get_component_pair(
            ComponentType.SENSOR, "lidar-custom"
        )
        assert component is None  # No non-driver sensor registered
        assert driver is self.sensor_driver

    def test_get_component_pair_no_match(self):
        """Test component pair retrieval when neither exists."""
        component, driver = get_component_pair(
            ComponentType.ROBOT, "nonexistent"
        )
        assert component is None
        assert driver is None


class TestComponentListing:
    """Test component listing functionality."""

    def setup_method(self):
        """Setup test components."""
        _component_registry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        _component_registry.clear()

    def test_list_components_empty_registry(self):
        """Test listing components when registry is empty."""
        components = list_components()
        assert components == {}

    def test_list_components_with_registered_components(self):
        """Test listing components with registered components."""

        @register_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id="franka-01",
                is_driver=True,
            )
        )
        class TestRobotDriver(RobotDriver):
            pass

        @register_component(
            ComponentSpec(
                component_type=ComponentType.SENSOR,
                id="camera-custom",
                is_driver=False,
            )
        )
        class TestSensorComponent:
            pass

        components = list_components()
        assert len(components) == 2

        # Verify the components are in the list
        robot_key = _ComponentKey(
            component_type=ComponentType.ROBOT,
            component_id="franka-01",
            is_driver=True,
            is_default=False,
        )
        sensor_key = _ComponentKey(
            component_type=ComponentType.SENSOR,
            component_id="camera-custom",
            is_driver=False,
            is_default=False,
        )

        assert robot_key in components
        assert sensor_key in components
        assert components[robot_key] is TestRobotDriver
        assert components[sensor_key] is TestSensorComponent

    def test_list_components_returns_copy(self):
        """Test that list_components returns a copy, not the original registry."""

        @register_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id="franka-custom",
                is_driver=True,
            )
        )
        class TestDriver(RobotDriver):
            pass

        components = list_components()
        original_length = len(components)

        # Modify the returned dictionary
        components.clear()

        # Original registry should be unchanged
        new_components = list_components()
        assert len(new_components) == original_length


class TestSystemComponentRegistry:
    """Integration tests for the entire component registry system."""

    def setup_method(self):
        """Clear registry before each test."""
        _component_registry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        _component_registry.clear()

    def test_complete_robot_registration_workflow(self):
        """Test complete workflow for robot component registration and retrieval."""

        # Register a robot component and driver
        @register_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id="franka-custom",
                is_driver=False,
            )
        )
        class FrankaRobot:
            def __init__(self):
                self.name = "Franka Robot"

        @register_component(
            ComponentSpec(
                component_type=ComponentType.ROBOT,
                id="franka-custom",
                is_driver=True,
            )
        )
        class FrankaRobotDriver(RobotDriver):
            def __init__(self):
                self.driver_name = "Franka Driver"

            def check_torque_status(self):
                pass

            def pass_joint_efforts(self, *args):
                pass

            def pass_joint_group_control_cmd(self, *args):
                pass

            def pass_joint_positions(self, *args):
                pass

            def pass_joint_velocities(self, *args):
                pass

            def shutdown_driver(self):
                pass

        # Test individual retrieval
        robot_cls = get_component(
            ComponentType.ROBOT, "franka-custom", is_driver=False
        )
        driver_cls = get_component(
            ComponentType.ROBOT, "franka-custom", is_driver=True
        )

        assert robot_cls is FrankaRobot
        assert driver_cls is FrankaRobotDriver

        # Test pair retrieval
        robot_pair_cls, driver_pair_cls = get_component_pair(
            ComponentType.ROBOT, "franka-custom"
        )
        assert robot_pair_cls is FrankaRobot
        assert driver_pair_cls is FrankaRobotDriver

        # Test instantiation
        robot_instance = robot_cls()
        driver_instance = driver_cls()
        assert robot_instance.name == "Franka Robot"
        assert driver_instance.driver_name == "Franka Driver"

    def test_types_import(self):
        """Test that robot package imports work correctly."""
        import eigen.types  # noqa: F401
