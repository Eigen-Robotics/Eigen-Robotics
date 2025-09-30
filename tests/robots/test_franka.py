"""Tests for Franka Panda robot component registration."""

import pytest

from eigen.core.system.component_registry import (
    ComponentType,
    _ComponentKey,
    get_component,
    get_component_pair,
    list_components,
)


class TestFrankaComponentRegistration:
    """Test Franka Panda robot component registration."""

    def test_franka_robot_component_is_registered(self):
        """Test that the Franka robot component is registered as default."""
        # Import to trigger registration
        from eigen.robots.franka_panda.franka_panda import FrankaPanda

        # Get the registered component
        robot_component = get_component(
            ComponentType.ROBOT, "franka-base", is_driver=False
        )

        assert robot_component is FrankaPanda

    def test_franka_pybullet_driver_is_registered(self):
        """Test that the Franka PyBullet driver is registered as default."""
        # Import to trigger registration
        from eigen.robots.franka_panda.franka_pybullet_driver import (
            FrankaPyBulletDriver,
        )

        # Get the registered driver
        driver_component = get_component(
            ComponentType.ROBOT, "franka-base", is_driver=True
        )

        assert driver_component is FrankaPyBulletDriver

    def test_franka_research_driver_is_registered(self):
        """Test that the Franka Research driver is registered as default (if available)."""
        try:
            # Import to trigger registration (may fail if franky library not available)
            from eigen.robots.franka_panda.franka_driver import (
                FrankaResearch3Driver,
            )

            # Get the registered driver
            driver_component = get_component(
                ComponentType.ROBOT, "franka-research3d-base", is_driver=True
            )

            assert driver_component is FrankaResearch3Driver

        except ImportError:
            # Skip test if franky library is not available
            pytest.skip(
                "franky library not available, skipping FrankaResearch3Driver test"
            )

    def test_franka_component_pair_retrieval(self):
        """Test retrieving the Franka component-driver pair."""
        # Import to trigger registration
        from eigen.robots.franka_panda.franka_panda import FrankaPanda
        from eigen.robots.franka_panda.franka_pybullet_driver import (
            FrankaPyBulletDriver,
        )

        # Get the component pair
        robot_component, driver_component = get_component_pair(
            ComponentType.ROBOT, "franka-base"
        )

        assert robot_component is FrankaPanda
        assert driver_component is FrankaPyBulletDriver

    def test_franka_components_are_default(self):
        """Test that Franka components are registered as default (library-provided)."""
        # Import to trigger registration
        from eigen.robots.franka_panda.franka_panda import FrankaPanda
        from eigen.robots.franka_panda.franka_pybullet_driver import (
            FrankaPyBulletDriver,
        )

        # Get all registered components
        components = list_components()

        # Find the Franka components
        franka_robot_key = _ComponentKey(
            component_type=ComponentType.ROBOT,
            component_id="franka-base",
            is_driver=False,
            is_default=True,
        )

        franka_driver_key = _ComponentKey(
            component_type=ComponentType.ROBOT,
            component_id="franka-base",
            is_driver=True,
            is_default=True,
        )

        # Verify they are registered as default
        assert franka_robot_key in components
        assert franka_driver_key in components
        assert components[franka_robot_key] is FrankaPanda
        assert components[franka_driver_key] is FrankaPyBulletDriver

    def test_franka_components_in_registry_listing(self):
        """Test that Franka components appear correctly in the registry listing."""
        # Import to trigger registration
        from eigen.robots.franka_panda.franka_panda import FrankaPanda  # noqa: F401, I001
        from eigen.robots.franka_panda.franka_pybullet_driver import (
            FrankaPyBulletDriver,  # noqa: F401
        )

        # Get all registered components
        components = list_components()

        # Should have at least the Franka components
        component_ids = [key.component_id for key in components.keys()]

        assert "franka-base" in component_ids

        # Count components with franka-base ID
        franka_base_components = [
            key
            for key in components.keys()
            if key.component_id == "franka-base"
        ]

        # Should have exactly 2: robot component + driver
        assert len(franka_base_components) == 2

        # Should have one driver and one non-driver
        drivers = [key for key in franka_base_components if key.is_driver]
        non_drivers = [
            key for key in franka_base_components if not key.is_driver
        ]

        assert len(drivers) == 1
        assert len(non_drivers) == 1

        # All should be default (library-provided)
        for key in franka_base_components:
            assert key.is_default is True
