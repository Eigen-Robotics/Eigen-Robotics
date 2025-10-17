# eigen-robotics

[back to README](../README.md)

Cross-platform Python project with seamless PyBullet installation.

## Quick Setup

```bash
make install
```

That's it (the basic)! Works on both Linux and macOS.

## How It Works

**The Problem**: PyPI only provides PyBullet wheels for Linux. On macOS, pip install fails.

**The Solution**:

- **Linux**: Uses PyPI wheels directly (fast)
- **macOS**: Builds PyBullet from source and creates a local wheel (slower to build, the rest is very fast)

## Project Structure

```output
eigen_robotics/                        # Workspace root
├── Makefile                        # Cross-platform automation
├── scripts/
│   └── build_pybullet_macos.py     # PyBullet build script for macOS
├── packages/                       # Semantic packages (workspace)
│   ├── eigen_framework/              # Core framework + types
│   ├── eigen_robots/                 # Robot implementations
│   ├── eigen_sensors/                # Sensor implementations
│   └── eigen_ml/                     # ML implementations
├── tests/                          # Integration tests
├── pyproject.toml                  # Workspace config
├── uv.lock                         # Unified lockfile
└── .gitignore                      # Excludes wheels/```

## Commands

```bash
make install    # First-time setup (builds PyBullet wheel on macOS)
make sync       # Update dependencies (or just: uv sync, switching branches etc.)
make clean      # Clean cache and built files
make help       # Show available commands
```

## Workspace Benefits

EIGEN uses **semantic packaging** with unified namespace:

```python
# All packages contribute to 'eigen' namespace
from eigen.core import Node              # from eigen-framework
from eigen.robots.franka import Robot    # from eigen-robots
from eigen.sensors.realsense import Camera # from eigen-sensors
from eigen.ml.rl import PolicyNetwork    # from eigen-ml
```

## Flexibility

Work-In-Progress, the final picture will be something more aking to `install eigen_robots[husky,franka]; install eigen_sensors[...]` with an implicit dependency on famework. In another words, optional dependencies get grouped and abstracted away once more, similar to the `--dev` dependency group. `eigen_robotics` and the `/src/eigen_robotics/__init__.py` is a stub to glue all of this together for now, it might have more meaningful uses later or we find a way to get rid of it

### Install all capabilities

```sh
uv sync --extra robots --extra sensors --extra ml
```

### Install selectively

```sh
uv sync --extra robots                 # Just robots
uv sync --extra dev                    # Development tools
```

## Daily Workflow

After the initial `make install`, you can use uv normally:

**Make commands:**

```bash
make sync              # Update dependencies (alias for uv sync)
make clean            # Clean cache and built files
```

**UV commands:**

```bash
uv sync               # Install/update dependencies
uv run python         # Run Python in the environment
uv add <package>      # Add new dependencies (to workspace root)

# Package-specific development
cd packages/eigen_robots
uv add numpy          # Add dependency to specific package

# Testing and quality
uv run pytest        # Run tests
uv run ruff check .   # Lint code
uv run ruff format .  # Format code
```

## Requirements

- **uv** package manager
- **macOS only**: Xcode Command Line Tools

### Installing uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installing Xcode Command Line Tools (macOS)

```bash
xcode-select --install
```

## First-Time Setup Details

**Linux**: Just installs PyBullet from PyPI wheels.

**macOS**:

1. Checks if `wheels/pybullet_macos.whl` exists
2. If not, runs `uv run build_pybullet_macos.py` to build it (takes 1-2 minutes)
3. The script uses uv's inline dependencies to install build tools automatically in a temporary build environment
4. The build process attempts to create a replicable build for SHA256 sum cross-check with `uv.lock` and gives the built wheel an appropriate package/version/pyver/abi name checked by `uv` to acommodate the requested linux dependency for feature parity.
5. Updates the wheel name in the `pyproject.toml` macOS specific dependency.
6. Creates a venv and installs dependencies via `uv sync`

The wheel is cached, so subsequent setups are fast.

## Troubleshooting

**macOS build fails**: Ensure Xcode Command Line Tools are installed

## Why This Approach

- **Pure uv workflow** after initial setup
- **No conda dependency**
- **Cached builds** - wheel built once, reused (todo, should reuse if macOS and linux dependency versions match and a wheel of that version is present)
- **Standard packaging** - uses normal Python dependency resolution
- **Cross-platform** - single command works everywhere

[back to README](../README.md)
