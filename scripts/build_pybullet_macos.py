#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "setuptools",
#     "wheel",
# ]
# ///
"""
Build PyBullet wheel for macOS and save to WHEELS_CACHE
"""

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import sysconfig
import tempfile
import urllib.request

WHEELS_CACHE_DIR_PATH = Path(".wheels")
PROJECT_TOML_PATH = Path("packages/ark_framework/pyproject.toml")


# This prevents package managers from failing reinstalling attempts that
# build the same source code and verify the wheel SHA256.
def setup_reproducible_environment() -> None:
    """Set environment variables for reproducible builds."""

    # Most important: Fixed timestamp for reproducible builds
    # This affects __DATE__, __TIME__ macros and file timestamps
    os.environ["SOURCE_DATE_EPOCH"] = "1640995200"  # 2022-01-01 00:00:00 UTC

    # Force single-threaded compilation to ensure deterministic ordering
    os.environ["MAX_JOBS"] = "1"
    os.environ["MAKEFLAGS"] = "-j1"

    # Disable parallel builds in distutils/setuptools
    os.environ["DISTUTILS_USE_SDK"] = "1"

    # Set deterministic compilation flags
    reproducible_cflags = [
        "-fdebug-prefix-map=/tmp=.",  # Normalize debug paths
        "-fmacro-prefix-map=/tmp=.",  # Normalize macro paths
        "-ffile-prefix-map=/tmp=.",  # Normalize file paths
        "-Wno-builtin-macro-redefined",  # Allow macro override
        '-D__DATE__="Jan  1 2022"',  # Fixed build date
        '-D__TIME__="00:00:00"',  # Fixed build time
        "-frandom-seed=0",  # Deterministic random seed
    ]

    reproducible_cxxflags = reproducible_cflags + [
        "-fno-ident",  # Don't emit compiler version
    ]

    reproducible_ldflags = [
        "-Wl,--build-id=none",  # No build ID (Linux)
        "-Wl,-no_uuid",  # No UUID (macOS)
    ]

    # Combine with existing flags
    existing_cflags = os.environ.get("CFLAGS", "")
    existing_cxxflags = os.environ.get("CXXFLAGS", "")
    existing_ldflags = os.environ.get("LDFLAGS", "")

    os.environ["CFLAGS"] = (
        f"{existing_cflags} {' '.join(reproducible_cflags)}".strip()
    )
    os.environ["CXXFLAGS"] = (
        f"{existing_cxxflags} {' '.join(reproducible_cxxflags)}".strip()
    )
    os.environ["LDFLAGS"] = (
        f"{existing_ldflags} {' '.join(reproducible_ldflags)}".strip()
    )

    # Set locale for consistent sorting
    os.environ["LC_ALL"] = "C"
    os.environ["LANG"] = "C"

    # Disable ccache if present (can cause non-determinism)
    os.environ["CCACHE_DISABLE"] = "1"

    # Python-specific settings
    os.environ["PYTHONHASHSEED"] = "0"  # Deterministic hash seed
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"  # Don't write .pyc files

    print("✓ Set reproducible build environment variables")


def get_required_pybullet_version() -> str | None:
    """Parse project config to get required pybullet version."""
    try:
        with PROJECT_TOML_PATH.open() as f:
            content = f.read()

        # Look for pybullet version in dependencies
        pattern = r"pybullet\s*[><=!]+\s*([0-9.]+)"
        match = re.search(pattern, content)
        if match:
            version = match.group(1)
            print(f"📋 Found required pybullet version: {version}")
            return version

        print(
            f"⚠️  No specific pybullet version found in {PROJECT_TOML_PATH.name}"
        )
        return None
    except Exception as e:
        print(f"⚠️  Failed to parse {PROJECT_TOML_PATH.name}: {e}")
        return None


def get_setup_py_version(branch_or_tag: str) -> str | None:
    """Get version from setup.py in a specific branch/tag."""
    url = f"https://raw.githubusercontent.com/bulletphysics/bullet3/{branch_or_tag}/setup.py"
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read().decode("utf-8")

        # Look for version in setup.py
        pattern = r"version\s*=\s*['\"]([^'\"]+)['\"]"
        match = re.search(pattern, content)
        if match:
            version = match.group(1)
            print(f"✓ Found setup.py version in {branch_or_tag}: {version}")
            return version

        print(f"⚠️  No version found in setup.py for {branch_or_tag}")
        return None
    except Exception as e:
        print(f"⚠️  Failed to fetch setup.py from {branch_or_tag}: {e}")
        return None


def find_matching_branch_or_tag(required_version: str) -> str:
    """Find the right branch/tag for the required version."""
    print(f"🔍 Looking for branch/tag matching version {required_version}")

    # First check master
    master_version = get_setup_py_version("master")
    if master_version == required_version:
        print("✓ Master branch has matching version")
        return "master"

    # Try to convert wheel version to tag format (e.g. 3.2.4 -> 3.24)
    version_parts = required_version.split(".")
    if len(version_parts) >= 3:
        # Convert 3.2.4 to 3.24
        tag_version = f"{version_parts[0]}.{version_parts[1]}{version_parts[2]}"
        print(f"🔍 Trying tag format: {tag_version}")

        tag_setup_version = get_setup_py_version(tag_version)
        if tag_setup_version == required_version:
            print(f"✓ Tag {tag_version} has matching version")
            return tag_version
        else:
            print(
                f"⚠️  Tag {tag_version} has version {tag_setup_version}, expected {required_version}"
            )

    print(
        f"⚠️  No matching branch/tag found for version {required_version}, using master"
    )
    return "master"


def run_command(
    cmd: list[str],
    cwd: Path | None = None,
    check: bool = True,
    env: dict | None = None,
) -> subprocess.CompletedProcess:
    """Run command and handle errors."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd, cwd=cwd, check=False, capture_output=True, text=True, env=env
    )

    if result.stdout:
        print(result.stdout)

    if result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        if result.stderr:
            print(f"Error output: {result.stderr}")
        if check:
            raise subprocess.CalledProcessError(
                result.returncode, cmd, result.stdout, result.stderr
            )

    return result


def find_python_framework_path() -> tuple[str, str]:
    """Find Python framework paths using auto-detection with fallbacks."""
    print("🔍 Auto-detecting Python paths...")

    # Method 1: Use sysconfig (most reliable)
    try:
        include_path = sysconfig.get_path("include")
        if include_path and Path(include_path).exists():
            print(f"✓ Found include path via sysconfig: {include_path}")

            stdlib_path = sysconfig.get_path("stdlib")
            if stdlib_path:
                lib_path = str(Path(stdlib_path).parent)
                if Path(lib_path).exists():
                    print(f"✓ Found lib path via sysconfig: {lib_path}")
                    return lib_path, include_path

    except Exception as e:
        print(f"⚠️  sysconfig detection failed: {e}")

    # Method 2: Derive from sys.executable (follow symlinks)
    try:
        print("🔍 Trying path derivation from sys.executable...")
        real_python = Path(sys.executable).resolve()
        print(f"   Real Python executable: {real_python}")

        path_parts = real_python.parts
        framework_idx = None
        for i, part in enumerate(path_parts):
            if part == "Python.framework":
                framework_idx = i
                break

        if framework_idx is not None and framework_idx + 2 < len(path_parts):
            version_path = Path(*path_parts[: framework_idx + 3])
            lib_path = str(version_path / "lib")
            include_path = str(
                version_path
                / "include"
                / f"python{sys.version_info.major}.{sys.version_info.minor}"
            )

            if Path(lib_path).exists() and Path(include_path).exists():
                print("✓ Found framework paths via derivation:")
                print(f"   Lib: {lib_path}")
                print(f"   Include: {include_path}")
                return lib_path, include_path

    except Exception as e:
        print(f"⚠️  Path derivation failed: {e}")

    # Method 3: Fallback to common locations
    print("🔍 Trying common framework locations...")
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

    common_locations = [
        f"/Library/Frameworks/Python.framework/Versions/{python_version}",
        f"/opt/homebrew/opt/python@{python_version}/Frameworks/Python.framework/Versions/{python_version}",
        f"/usr/local/opt/python@{python_version}/Frameworks/Python.framework/Versions/{python_version}",
    ]

    for base_path in common_locations:
        lib_path = f"{base_path}/lib"
        include_path = f"{base_path}/include/python{python_version}"

        if Path(lib_path).exists() and Path(include_path).exists():
            print("✓ Found framework paths at common location:")
            print(f"   Base: {base_path}")
            return lib_path, include_path
        else:
            print(f"   Checked {base_path}: not found")

    # Method 4: Last resort
    print("🔍 Using current Python installation paths as last resort...")
    base_path = Path(sys.executable).parent.parent
    lib_path = str(base_path / "lib")
    include_path = str(base_path / "include" / f"python{python_version}")

    print("⚠️  Using fallback paths:")
    print(f"   Lib: {lib_path}")
    print(f"   Include: {include_path}")

    return lib_path, include_path


def validate_build_environment(lib_path: str, include_path: str) -> None:
    """Validate that we have the necessary files for building C extensions."""
    print("🔍 Validating build environment...")

    python_h = Path(include_path) / "Python.h"
    if not python_h.exists():
        print(f"❌ Critical: Python.h not found at {python_h}")
        raise RuntimeError(
            f"Python development headers not found at {include_path}"
        )

    print(f"✓ Found Python.h at {python_h}")


def patch_zlib_header(bullet_dir: Path) -> None:
    """Patch zlib header to fix fdopen issue on macOS."""
    zutil_path = bullet_dir / "examples" / "ThirdPartyLibs" / "zlib" / "zutil.h"

    if not zutil_path.exists():
        print(f"Warning: {zutil_path} not found, skipping patch")
        return

    with zutil_path.open() as f:
        content = f.read()

    content = content.replace(
        "#define fdopen(fd, mode) NULL",
        "// #define fdopen(fd, mode) NULL  // Commented out for macOS build",
    )

    with zutil_path.open("w") as f:
        f.write(content)

    print("✓ Patched zlib header")


def check_existing_wheel(version: str) -> str | None:
    """Check if a wheel for the given version already exists.

    Returns the wheel filename if it exists, None otherwise.
    """
    if not WHEELS_CACHE_DIR_PATH.exists():
        return None

    # Look for existing wheels matching the version pattern
    # PyBullet wheels typically follow pattern: pybullet-{version}-{python_tag}-{abi_tag}-{platform_tag}.whl
    pattern = f"pybullet-{version}-*.whl"
    existing_wheels = list(WHEELS_CACHE_DIR_PATH.glob(pattern))

    if existing_wheels:
        wheel_file = existing_wheels[0]
        print(f"✅ Wheel already exists: {wheel_file.name}")
        return wheel_file.name

    return None


def update_pyproject_sources(wheel_filename: str) -> None:
    """Update [tool.uv.sources] section with the built wheel path."""
    try:
        with PROJECT_TOML_PATH.open("r") as f:
            content = f.read()

        framework_relative_wheel_path = (
            "../../" / WHEELS_CACHE_DIR_PATH / wheel_filename
        )
        new_source_line = f'pybullet = {{ path = "{framework_relative_wheel_path}", marker = "sys_platform == \'darwin\'" }}'

        # Replace or add the [tool.uv.sources] section
        if "[tool.uv.sources]" in content:
            lines = content.split("\n")
            updated_lines = []
            in_sources = False
            pybullet_updated = False

            for line in lines:
                if line.strip() == "[tool.uv.sources]":
                    in_sources = True
                    updated_lines.append(line)
                elif (
                    in_sources
                    and line.startswith("[")
                    and not line.startswith("[tool.uv.sources]")
                ):
                    in_sources = False
                    if not pybullet_updated:
                        updated_lines.append(new_source_line)
                    updated_lines.append(line)
                elif in_sources and "pybullet" in line and "=" in line:
                    updated_lines.append(new_source_line)
                    pybullet_updated = True
                else:
                    updated_lines.append(line)

            if in_sources and not pybullet_updated:
                updated_lines.append(new_source_line)

            content = "\n".join(updated_lines)
        else:
            content += f"\n\n[tool.uv.sources]\n{new_source_line}\n"

        with PROJECT_TOML_PATH.open("w") as f:
            f.write(content)

        print(
            f"✓ Updated {PROJECT_TOML_PATH.name} sources with: {framework_relative_wheel_path}"
        )
    except Exception as e:
        print(f"⚠️  Failed to update {PROJECT_TOML_PATH.name}: {e}")


def build_pybullet_wheel() -> None:
    """Build PyBullet wheel and save to WHEELS_CACHE with proper filename"""
    print("🚀 Building PyBullet from source...")
    setup_reproducible_environment()

    # Determine which version to build
    required_version = get_required_pybullet_version()
    if required_version:
        # Check if wheel already exists
        existing_wheel = check_existing_wheel(required_version)
        if existing_wheel:
            update_pyproject_sources(existing_wheel)
            return

        branch_or_tag = find_matching_branch_or_tag(required_version)
    else:
        branch_or_tag = "master"
        print("📋 Using master branch (no version specified)")

    # Create wheels directory
    WHEELS_CACHE_DIR_PATH.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        bullet_dir = tmp_path / "bullet3"

        print(f"📦 Cloning bullet3 repository ({branch_or_tag})...")
        if branch_or_tag == "master":
            run_command(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "https://github.com/bulletphysics/bullet3.git",
                    str(bullet_dir),
                ]
            )
        else:
            run_command(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    branch_or_tag,
                    "https://github.com/bulletphysics/bullet3.git",
                    str(bullet_dir),
                ]
            )

        print("🔧 Applying macOS patches...")
        patch_zlib_header(bullet_dir)

        print("🏗️  Setting up build environment...")
        lib_path, include_path = find_python_framework_path()
        validate_build_environment(lib_path, include_path)

        env = os.environ.copy()
        env.update(
            {
                "LDFLAGS": f"-L{lib_path}",
                "CPPFLAGS": f"-I{include_path}",
                "CFLAGS": f"-I{include_path}",
            }
        )

        print("🔧 Build environment:")
        print(f"   LDFLAGS: {env['LDFLAGS']}")
        print(f"   CPPFLAGS: {env['CPPFLAGS']}")

        print("🔨 Building PyBullet wheel...")
        result = run_command(
            ["python", "setup.py", "bdist_wheel"],
            cwd=bullet_dir,
            check=False,
            env=env,
        )

        if result.returncode != 0:
            print("❌ Build failed. Trying with verbose output...")
            run_command(
                ["python", "setup.py", "bdist_wheel", "--verbose"],
                cwd=bullet_dir,
                env=env,
            )

        # Find the built wheel
        dist_dir = bullet_dir / "dist"
        wheel_files = list(dist_dir.glob("*.whl"))

        if not wheel_files:
            raise RuntimeError("No wheel file found after build")

        wheel_file = wheel_files[0]
        print(f"✓ Built wheel: {wheel_file.name}")

        # Copy wheel preserving the proper filename
        target_wheel = WHEELS_CACHE_DIR_PATH / wheel_file.name
        shutil.copy2(wheel_file, target_wheel)

        print(f"✅ PyBullet wheel saved to: {target_wheel}")
        update_pyproject_sources(wheel_file.name)


if __name__ == "__main__":
    build_pybullet_wheel()
