"""Test namespace package functionality."""
# this is effectivelly an example and should be refactored by eventually
# deleting this module and including them in their own test collections.

# For example /tests/types/test_types.py is testing both the importability
# (existence) and thus precedes that test here and adds additional
# implementation specific tests on top.


def test_ark_namespace_import():
    """Test that ark namespace can be imported."""
    import ark

    assert ark is not None


def test_all_modules_importable():
    """Test that all ark modules can be imported."""
    import ark.core
    import ark.ml
    import ark.robots
    import ark.sensors
    # import ark.types

    # Verify they're all different modules
    assert ark.core is not ark.robots
    assert ark.robots is not ark.sensors
    assert ark.sensors is not ark.ml


def test_namespace_discovery():
    """Test that namespace discovery works correctly."""
    import pkgutil

    import ark

    discovered_modules = set()
    for _, modname, _ in pkgutil.iter_modules(ark.__path__, ark.__name__ + "."):
        discovered_modules.add(modname)

    expected_modules = {
        "ark.core",
        "ark.robots",
        "ark.sensors",
        "ark.ml",
        # "ark.types",
    }

    print(f"Expected: {expected_modules}")
    print(f"Discovered: {discovered_modules}")

    assert expected_modules.issubset(discovered_modules)


class TestPackageMainFunctions:
    """Test main functions of each package."""

    def test_robots_main_returns_robots(self):
        """Test that robots main function returns 'robots'."""
        from ark.robots import main

        assert main() == "robots"

    def test_sensors_main_returns_sensors(self):
        """Test that sensors main function returns 'sensors'."""
        from ark.sensors import main

        assert main() == "sensors"

    def test_ml_main_returns_ml(self):
        """Test that ml main function returns 'ml'."""
        from ark.ml import main

        assert main() == "ml"


class TestPackageScriptEntries:
    """Test that package script entries work correctly."""

    def test_robots_script_callable(self):
        """Test that robots script entry point is callable."""
        from ark.robots.main import main

        result = main()
        assert result == "robots"

    def test_sensors_script_callable(self):
        """Test that sensors script entry point is callable."""
        from ark.sensors.main import main

        result = main()
        assert result == "sensors"

    def test_ml_script_callable(self):
        """Test that ml script entry point is callable."""
        from ark.ml.main import main

        result = main()
        assert result == "ml"


class TestNamespacePackageStructure:
    """Test namespace package structure and behavior."""

    def test_ark_is_namespace_package(self):
        """Test that ark is correctly recognized as namespace package."""
        import ark

        # Namespace packages have __path__ but no __file__
        assert hasattr(ark, "__path__")
        assert not hasattr(ark, "__file__") or ark.__file__ is None

    def test_submodules_have_correct_paths(self):
        """Test that submodules are loaded from correct paths."""
        import ark.core
        import ark.ml
        import ark.robots
        import ark.sensors
        # import ark.types

        # Each should have a __file__ pointing to correct package
        assert "ark_framework" in ark.core.__file__
        assert "ark_robots" in ark.robots.__file__
        assert "ark_sensors" in ark.sensors.__file__
        assert "ark_ml" in ark.ml.__file__
        # assert "ark_framework" in ark.types.__file__

    def test_cross_package_imports_work(self):
        """Test that imports work across different packages."""
        # This tests that the namespace is truly unified
        # Test that basic imports work across packages
        from ark.ml import main as ml_main
        from ark.robots import main as robots_main
        from ark.sensors import main as sensors_main

        assert robots_main() == "robots"
        assert sensors_main() == "sensors"
        assert ml_main() == "ml"
