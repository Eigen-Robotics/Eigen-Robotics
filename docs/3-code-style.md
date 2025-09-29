# Code Formatting with Ruff

[back to README](../README.md)

## Overview

Ruff formatter automatically fixes code style issues. It handles spacing, indentation, quotes, and line breaks according to configuration rules.

## Basic Commands

```bash
# Format all Python files
uv run ruff format .

# Format specific files
uv run ruff format ark/system/component/robot.py

# Check formatting without applying changes
uv run ruff format --check .

# See what would change (diff output)
uv run ruff format --diff .
```

## Configuration

ARK uses a dedicated `.ruff.toml` configuration file:

```toml
# Ruff configuration for ARK robotics framework
line-length = 80
indent-width = 4
target-version = "py310"

exclude = [
    ".git",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "*.egg-info",
    ".pytest_cache",
    ".mypy_cache",
    "docs/*.md",
]

[lint]
select = [
    "E",   # pycodestyle errors (PEP8 core)
    "PTH", # flake8-use-pathlib (modern path handling)
    "B",   # flake8-bugbear (common bugs and design problems)
    "F",   # Pyflakes (essential error detection)
    "I",   # isort (import sorting)
    "W",   # pycodestyle warnings
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade (Python syntax modernization)
]

ignore = [
    "E501", # Line too long (let formatter handle this)
    "E402", # Module level import not at top (common in __init__.py)
    "B008", # Do not perform function call in default arguments
]

[lint.isort]
known-first-party = ["ark", "arktypes"]
known-third-party = [
    "numpy", "scipy", "matplotlib", "cv2", "pybullet",
    "torch", "tensorflow", "gym", "typing_extensions",
]

[format]
indent-style = "space"
quote-style = "double"
docstring-code-format = true
docstring-code-line-length = 72
```

## Formatting Rules

### Indentation

```python
# Before
def func(a,
    b,
        c):
  return a + b + c

# After (ARK uses 4-space indentation)
def func(a,
         b,
         c):
    return a + b + c
```

### Quote Normalization

```python
# Before
name = 'robot'
path = "config.yaml"

# After
name = "robot"
path = "config.yaml"
```

### Import Formatting

```python
# Before
from typing import Dict,List,Optional
import sys,os

# After
from typing import Dict, List, Optional
import os
import sys
```

### Line Length and Wrapping

```python
# Before
def configure_robot(name: str, joint_limits: Dict[str, float], safety_limits: Dict[str, float]) -> RobotConfig:

# After
def configure_robot(
    name: str,
    joint_limits: Dict[str, float],
    safety_limits: Dict[str, float]
) -> RobotConfig:
```

### Trailing Commas

```python
# Before
robot_config = {
    "name": "franka_arm",
    "dof": 7
}

# After
robot_config = {
    "name": "franka_arm",
    "dof": 7,
}
```

## General Style

 Use built-in types (Python 3.10+ features)

```python
def process_joints(joints: list[float]) -> dict[str, float]:
    return {"status": "ok"}
```

Union types with | operator (Python 3.10+)

```python
def get_robot(robot_id: str | int) -> Robot | None:
    return find_robot(robot_id)
```

Comments start with capital letters and end with periods.

```python
def initialize_robot() -> bool:
    # Initialize the robot hardware connection.
    connection = establish_connection()

    # Verify the connection is stable.
    return verify_connection(connection
```

Path Handling

```python
# Preferred
from pathlib import Path

config_path = Path("config") / "robot.yaml"
if config_path.exists():
    data = config_path.read_text()

# Not: os.path.join("config", "robot.yaml")
```

### Docstring Formatting

Work-In-Progres
TODO(FV): Try to stay compatible with doxygen.

```python
# Before
def move_to_pose(pose):
    """Move robot to target pose.

    Args:
        pose: Target pose as 4x4 matrix

    Returns:
        Success status"""

# After
def move_to_pose(pose):
    """Move robot to target pose.

    Args:
        pose: Target pose as 4x4 matrix

    Returns:
        Success status
    """
```

## Integration Patterns

### Pre-commit Hook

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.2
    hooks:
      - id: ruff-format
```

### CI/CD Pipeline

```yaml
- name: Check formatting
  run: uv run ruff format --check .

- name: Format code
  run: uv run ruff format .
```

### Editor Integration

#### VS Code

```json
{
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true
    }
}
```

#### Vim/Neovim

```lua
vim.api.nvim_create_autocmd("BufWritePre", {
    pattern = "*.py",
    command = "!ruff format %"
})
```

## Exclusions

Exclude files from formatting:

```toml
[format]
exclude = [
    "generated/*.py",
    "third_party/",
    "*.pyi"
]
```

Per-file exclusions:

```python
# ruff: noqa: format
def legacy_function():
    # Preserve original formatting
    return    {"status":   "ok"}
```

## Common Issues

### Mixed Indentation

```python
# Problem: tabs and spaces mixed
def func():
     return True  # Tab + spaces

# Solution: ruff format fixes automatically
def func():
    return True
```

### Inconsistent String Quotes

```python
# Problem: mixed quote styles
config = {'host': "localhost", "port": '8080'}

# Solution: normalized to double quotes
config = {"host": "localhost", "port": "8080"}
```

### Long Lines

```python
# Problem: exceeds line length
robot_state = RobotState(joint_positions=[1.0, 2.0, 3.0, 4.0, 5.0], joint_velocities=[0.1, 0.2, 0.3, 0.4, 0.5])

# Solution: automatic wrapping
robot_state = RobotState(
    joint_positions=[1.0, 2.0, 3.0, 4.0, 5.0],
    joint_velocities=[0.1, 0.2, 0.3, 0.4, 0.5]
)
```

## Format vs Lint

Formatter handles style consistency:

- Spacing and indentation
- Quote style
- Line breaks
- Trailing commas

Linter handles code quality:

- Unused imports
- Type errors
- Logic issues
- Best practices

Run both:

```bash
uv run ruff check --fix .    # Fix linting issues
uv run ruff format .         # Fix formatting issues
```

## Workspace Integration

For semantic workspace structure:

```bash
# Format entire workspace
uv run ruff format packages/

# Format specific package
uv run ruff format packages/ark_robots/

# Check all packages
find packages/ -name "*.py" -exec ruff format --check {} +
```

[back to README](../README.md)
