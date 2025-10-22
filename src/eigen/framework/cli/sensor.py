"""CLI tools for inspecting available sensors."""

from __future__ import annotations

import subprocess
import importlib
import importlib.util
from dataclasses import dataclass
from typing import Iterable, Optional
from pathlib import Path
import sys
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Inspect available sensors and their drivers/features.")
console = Console()


def _find_spec(module: str):
    try:
        return importlib.util.find_spec(module)
    except ModuleNotFoundError:
        return None


def _normalize_entries(values: Iterable[str]) -> str:
    entries = [value for value in values if value]
    return ", ".join(entries) if entries else "-"


def _format_feature_name(value: str) -> str:
    return value.replace("_", " ").lower()


@dataclass
class SensorDescriptor:
    name: str
    module: str
    description: str = ""
    extra: Optional[str] = None
    default_drivers: tuple[str, ...] = ()
    default_features: tuple[str, ...] = ()

    def spec(self):
        return _find_spec(self.module)

    def is_installed(self) -> bool:
        return self.spec() is not None

    def default_drivers_display(self) -> str:
        return _normalize_entries(self.default_drivers)

    def default_features_display(self) -> str:
        return _normalize_entries(
            [_format_feature_name(feature) for feature in self.default_features]
        )


KNOWN_SENSORS: dict[str, SensorDescriptor] = {
    "realsense": SensorDescriptor(
        name="realsense",
        module="eigen.sensors.realsense.realsense",
        description="Intel RealSense RGB-D camera",
        extra="realsense",
        default_drivers=("pybullet", "hardware"),
        default_features=("rgb", "depth"),
    ),
    "zed": SensorDescriptor(
        name="zed",
        module="eigen.sensors.zed.zed",
        description="Stereolabs ZED stereo camera",
        extra="zed",
        default_drivers=("pybullet", "hardware"),
        default_features=("stereo_rgb", "depth"),
    ),
    "velodyne": SensorDescriptor(
        name="velodyne",
        module="eigen.sensors.velodyne.velodyne",
        description="Velodyne LiDAR sensor",
        extra="velodyne",
        default_drivers=("pybullet", "hardware"),
        default_features=("point_cloud",),
    ),
    "basic_camera": SensorDescriptor(  # Fixed: changed key from "basic camera" to "basic_camera"
        name="basic_camera",           # Fixed: changed from "velody111ne" 
        module="eigen.sensors.camera.camera",  # Fixed: proper module path
        description="Basic webcam with RGB_capture functionality",  # Fixed: correct description with underscores
        extra="basic_camera",          # Fixed: changed from "velodyne"
        default_drivers=("pybullet", "genesis", "hardware"),
        default_features=("rgb",),     # Fixed: changed from ("point_cloud",)
    ),
}


def _load_module(descriptor: SensorDescriptor):
    try:
        module = importlib.import_module(descriptor.module)
        return module, None
    except ModuleNotFoundError as exc:
        return None, f"Missing dependency: {exc.name}"
    except Exception as exc:  # pragma: no cover - defensive
        return None, f"Import error: {exc}"


def _driver_status(
    descriptor: SensorDescriptor, module, note: Optional[str]
) -> tuple[str, Optional[str]]:
    if module is None:
        if note and descriptor.extra and note.startswith("Missing dependency"):
            note = f"{note}. Install extra '{descriptor.extra}' to enable drivers."
        drivers_display = descriptor.default_drivers_display()
        if drivers_display == "-":
            drivers_display = "-"
        return drivers_display, note

    drivers_enum = getattr(module, "Drivers", None)
    if drivers_enum is None:
        drivers_display = descriptor.default_drivers_display()
        note = note or None
        return drivers_display, note

    entries: list[str] = []
    driver_note: Optional[str] = None

    for member in drivers_enum:
        driver_cls = member.value
        runnable = False
        if driver_cls is None:
            driver_note = driver_note or f"Driver '{member.name.lower()}' unavailable."
        else:
            runnable = getattr(driver_cls, "_runnable", True)
            if not runnable and descriptor.extra and driver_note is None:
                driver_note = (
                    f"Install extra '{descriptor.extra}' to enable {member.name.lower()}."
                )

        symbol = "✓" if runnable else "✗"
        entries.append(f"{member.name.lower()} {symbol}")

    return ", ".join(entries) if entries else "-", driver_note or note


def _feature_status(descriptor: SensorDescriptor, module) -> str:
    if module is None:
        return descriptor.default_features_display()

    features = getattr(module, "Features", None)
    if features is not None:
        entries = []
        for member in features:
            value = getattr(member, "value", None)
            if isinstance(value, str):
                entries.append(_format_feature_name(value))
            else:
                entries.append(_format_feature_name(member.name))
        return _normalize_entries(entries)

    features_attr = getattr(module, "FEATURES", None)
    print(features_attr)
    if isinstance(features_attr, (list, tuple, set)):
        entries = [
            _format_feature_name(str(feature)) for feature in features_attr
        ]
        return _normalize_entries(entries)

    return descriptor.default_features_display()

def _get_descriptor(name: str) -> Optional[SensorDescriptor]:
    return KNOWN_SENSORS.get(name.lower())

@app.command()
def list() -> None:
    """List sensors bundled with Eigen Robotics and their availability."""
    table = Table(title="Sensors", header_style="bold")
    table.add_column("Sensor", justify="left", style="cyan")
    table.add_column("Installed", justify="center", style="green")
    table.add_column("Drivers", justify="left", style="magenta")
    table.add_column("Features", justify="left", style="blue")
    table.add_column("Notes", justify="left", style="yellow")

    for descriptor in KNOWN_SENSORS.values():
        # print(descriptor)
        module, note = _load_module(descriptor)
        installed = module is not None
        installed_symbol = "✓" if installed else "✗"

        drivers_display, driver_note = _driver_status(
            descriptor, module, note
        )
        features_display = _feature_status(descriptor, module)

        notes: list[str] = []
        if descriptor.description:
            notes.append(descriptor.description)
        if driver_note:
            notes.append(driver_note)
        elif not installed:
            if descriptor.extra:
                notes.append(f"Install extra '{descriptor.extra}'")
            else:
                notes.append("Not installed")

        table.add_row(
            descriptor.name,
            installed_symbol,
            drivers_display,
            features_display,
            "; ".join(notes) if notes else "-",
        )

    console.print(table)

@app.command()
def run(
    name: str,
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show the command that would be executed without running it.",
    ),
    robot_name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Override the sensor component name passed to the runner.",
    ),
    config_path: Optional[Path] = typer.Option(
        None,
        "--config-path",
        "-c",
        help="Path to a global configuration YAML file.",
        exists=False,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
) -> None:
    """Launch a sensor embodiment by name."""

    descriptor = _get_descriptor(name)
    if descriptor is None:
        console.print(f"[red]Unknown sensor '{name}'.[/red]")
        raise typer.Exit(1)

    if descriptor.spec() is None:
        console.print(
            f"[red]Sensor '{descriptor.name}' is not available in this environment.[/red]"
        )
        if descriptor.extra:
            console.print(
                f"Install the 'eigen-sensors[{descriptor.extra}]' extra to enable it."
            )
        raise typer.Exit(1)

    # FORCES the parent folder and the sensors name.py file to be the same
    cmd = [sys.executable, "-m", descriptor.module]
    if robot_name:
        cmd += ["--name", robot_name]
    if config_path:
        cmd += ["--config", str(config_path)]
    console.print(
        f"Launching '{descriptor.name}' via module '{descriptor.module}'."
    )

    if dry_run:
        console.print(f"[dim]{' '.join(cmd)}[/dim]")
        return

    try:
        result = subprocess.run(cmd, check=False)
    except KeyboardInterrupt:  # pragma: no cover - user interaction
        console.print("\nInterrupted.")
        raise typer.Exit(130) from None

    if result.returncode != 0:
        raise typer.Exit(result.returncode)


def main() -> None:  # pragma: no cover - convenience wrapper
    app()
