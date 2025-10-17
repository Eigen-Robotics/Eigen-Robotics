"""Test namespace package functionality."""
# this is effectivelly an example and should be refactored by eventually
# deleting this module and including them in their own test collections.

# For example /tests/types/test_types.py is testing both the importability
# (existence) and thus precedes that test here and adds additional
# implementation specific tests on top.


def test_eigen_namespace_import():
    """Test that eigen namespace can be imported."""
    import eigen

    assert eigen is not None


def test_all_modules_importable():
    """Test that all eigen modules can be imported."""
    import eigen.core
    import eigen.ml
    import eigen.robots
    import eigen.sensors
    # import eigen.types

    # Verify they're all different modules
    assert eigen.core is not eigen.robots
    assert eigen.robots is not eigen.sensors
    assert eigen.sensors is not eigen.ml


def test_namespace_discovery():
    """Test that namespace discovery works correctly."""
    import pkgutil

    import eigen

    discovered_modules = set()
    for _, modname, _ in pkgutil.iter_modules(eigen.__path__, eigen.__name__ + "."):
        discovered_modules.add(modname)

    expected_modules = {
        "eigen.core",
        "eigen.robots",
        "eigen.sensors",
        "eigen.ml",
        # "eigen.types",
    }

    print(f"Expected: {expected_modules}")
    print(f"Discovered: {discovered_modules}")

    assert expected_modules.issubset(discovered_modules)


class TestPackageMainFunctions:
    """Test main functions of each package."""

    def test_robots_main_returns_robots(self):
        """Test that robots main function returns 'robots'."""
        from eigen.robots import main

        assert main() == "robots"

    def test_sensors_main_returns_sensors(self):
        """Test that sensors main function returns 'sensors'."""
        from eigen.sensors import main

        assert main() == "sensors"

    def test_ml_main_returns_ml(self):
        """Test that ml main function returns 'ml'."""
        from eigen.ml import main

        assert main() == "ml"


class TestPackageScriptEntries:
    """Test that package script entries work correctly."""

    def test_robots_script_callable(self):
        """Test that robots script entry point is callable."""
        from eigen.robots.main import main

        result = main()
        assert result == "robots"

    def test_sensors_script_callable(self):
        """Test that sensors script entry point is callable."""
        from eigen.sensors.main import main

        result = main()
        assert result == "sensors"

    def test_ml_script_callable(self):
        """Test that ml script entry point is callable."""
        from eigen.ml.main import main

        result = main()
        assert result == "ml"


class TestNamespacePackageStructure:
    """Test namespace package structure and behavior."""

    def test_eigen_is_namespace_package(self):
        """Test that eigen is correctly recognized as namespace package."""
        import eigen

        # Namespace packages have __path__ but no __file__
        assert hasattr(eigen, "__path__")
        assert not hasattr(eigen, "__file__") or eigen.__file__ is None

    def test_submodules_have_correct_paths(self):
        """Test that submodules are loaded from correct paths."""
        import eigen.core
        import eigen.ml
        import eigen.robots
        import eigen.sensors
        # import eigen.types

        # Each should have a __file__ pointing to correct package
        assert "eigen_framework" in eigen.core.__file__
        assert "eigen_robots" in eigen.robots.__file__
        assert "eigen_sensors" in eigen.sensors.__file__
        assert "eigen_ml" in eigen.ml.__file__
        # assert "eigen_framework" in eigen.types.__file__

    def test_cross_package_imports_work(self):
        """Test that imports work across different packages."""
        # This tests that the namespace is truly unified
        # Test that basic imports work across packages
        from eigen.ml import main as ml_main
        from eigen.robots import main as robots_main
        from eigen.sensors import main as sensors_main

        assert robots_main() == "robots"
        assert sensors_main() == "sensors"
        assert ml_main() == "ml"
