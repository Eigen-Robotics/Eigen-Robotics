# Testing Guide

[back to README](../README.md)

## Overview

ARK uses pytest with a structured approach that mirrors the semantic package organization. Tests are organized both by integration level and by module focus.

Work-In-Progress: I expectect discussion to ensue, separation of fast unit tests vs slow integration tests should be kept in mind. Because not all components (robots, sensors, etc.) are going to be run together and some might have strictly conflicting dependencies, ephermal environments and CI/CD runs should be considered. Right now the tests do not show anything ground breaking, but they do help with a sanity check that the workspace solution works import-wise.

## Test Structure

```output
tests/
├── test_namespace_packages.py    # Integration tests (workspace-level)
├── robots/
│   ├── __init__.py
│   ├── test_robot_integration.py # Robot-specific integration tests
│   └── test_franka_robot.py      # Individual robot tests
├── sensors/
│   ├── __init__.py
│   └── test_sensor_integration.py
├── ml/
│   ├── __init__.py
│   └── test_ml_integration.py
└── core/
    ├── __init__.py
    └── test_core_functionality.py
```

## Test Organization Levels

### 1. Workspace Integration Tests

Located in `tests/test_namespace_packages.py` - test the overall workspace functionality:

```python
def test_ark_namespace_import():
    """Test that ark namespace can be imported."""
    import ark
    assert ark is not None

class TestNamespacePackageStructure:
    """Test namespace package structure and behavior."""

    def test_ark_is_namespace_package(self):
        """Test that ark is correctly recognized as namespace package."""
        import ark
        assert hasattr(ark, "__path__")
```

### 2. Module-Focused Tests

Located in `tests/{module}/` - test specific package functionality:

```python
class TestRobotIntegration:
    """Test robot package integration and core functionality."""

    def test_robot_main_function(self):
        """Test that robot main function works correctly."""
        from ark.robots import main
        assert main() == "robots"
```

### 3. Implementation-Specific Tests

Located in `tests/{module}/test_{specific_implementation}.py`:

```python
class TestFrankaRobot:
    """Test Franka robot specific functionality."""

    def test_franka_initialization(self):
        """Test Franka robot can be initialized."""
        # Implementation-specific tests
        pass
```

## Running Tests

### All Tests

```bash
uv run pytest                     # Run all tests
uv run pytest -v                  # Verbose output
uv run pytest --cov=ark           # With coverage
```

### Module-Specific Tests

```bash
uv run pytest tests/robots/       # All robot tests
uv run pytest tests/sensors/      # All sensor tests
uv run pytest tests/ml/           # All ML tests
uv run pytest tests/core/         # All core tests
```

### Integration vs Unit Tests

```bash
uv run pytest tests/test_namespace_packages.py  # Integration tests
uv run pytest tests/robots/test_robot_integration.py  # Robot integration
uv run pytest tests/robots/test_franka_robot.py       # Specific robot
```

## Test Conventions

### Class Organization

Group related tests using descriptive class names:

```python
class TestRobotConfiguration:
    """Test robot configuration and setup."""

class TestRobotMovement:
    """Test robot movement and control."""

class TestRobotSafety:
    """Test robot safety systems."""
```

### Test Method Naming

Use descriptive names that explain what is being tested:

```python
def test_robot_initializes_with_valid_config(self):
    """Test that robot initializes when given valid configuration."""

def test_robot_raises_error_with_invalid_config(self):
    """Test that robot raises appropriate error for invalid config."""
```

### Imports and Setup

Place imports at the function level for namespace tests:

```python
def test_robot_import(self):
    """Test robot module can be imported."""
    from ark.robots.franka import FrankaRobot  # Import inside test
    assert FrankaRobot is not None
```

Use class-level setup for related tests:

```python
class TestFrankaRobot:
    """Test Franka robot functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        from ark.robots.franka import FrankaRobot
        self.robot_class = FrankaRobot
```

## Test Markers

Use pytest markers to categorize tests:

```python
import pytest

@pytest.mark.integration
def test_full_robot_workflow():
    """Test complete robot workflow."""
    pass

@pytest.mark.slow
def test_robot_calibration():
    """Test robot calibration process (takes time)."""
    pass

@pytest.mark.hardware
def test_real_robot_connection():
    """Test connection to real robot hardware."""
    pass
```

Run specific markers:

```bash
uv run pytest -m integration      # Only integration tests
uv run pytest -m "not slow"       # Skip slow tests
uv run pytest -m "not hardware"   # Skip hardware tests
```

## Configuration

Tests are configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
  "--strict-markers",
  "--disable-warnings",
  "-v"
]
markers = [
  "slow: marks tests as slow",
  "integration: marks tests as integration tests",
  "hardware: marks tests that require hardware"
]
```

## Example Test Files

### Module Integration Test

`tests/robots/test_robot_integration.py`:

```python
"""Integration tests for robot package."""

class TestRobotIntegration:
    """Test robot package integration."""

    def test_robot_package_imports(self):
        """Test all robot imports work."""
        from ark.robots import main
        assert main() == "robots"

    def test_robot_namespace_contribution(self):
        """Test robots contribute to ark namespace."""
        import ark
        assert hasattr(ark, 'robots')
```

### Specific Implementation Test

`tests/robots/test_franka_robot.py`:

```python
"""Tests for Franka robot implementation."""

import pytest

class TestFrankaRobot:
    """Test Franka robot specific functionality."""

    def test_franka_robot_exists(self):
        """Test Franka robot class can be imported."""
        # This will be implemented when we have actual robot classes
        pass

    @pytest.mark.hardware
    def test_franka_hardware_connection(self):
        """Test Franka robot hardware connection."""
        # Hardware-specific tests
        pytest.skip("Hardware not available in CI")
```

## Best Practices

1. **Mirror package structure** - organize tests to match `packages/` structure
2. **Use descriptive class names** - group related functionality
3. **Test namespace integration** - ensure packages work together
4. **Mark hardware tests** - separate tests that need real hardware
5. **Keep tests focused** - one concept per test method
6. **Use fixtures for setup** - avoid repetitive setup code

## Adding New Tests

When adding a new robot implementation:

1. Create `tests/robots/test_{robot_name}_robot.py`
2. Add class `Test{RobotName}Robot`
3. Include basic import and functionality tests
4. Mark hardware-specific tests appropriately
5. Add integration test in `test_robot_integration.py`

This structure scales with your semantic package organization and provides clear separation between integration tests and implementation-specific tests.

[back to README](../README.md)
