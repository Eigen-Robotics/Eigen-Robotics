"""CLI tools for inspecting and launching robot embodiments."""

from __future__ import annotations

import importlib
import importlib.util
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table


app = typer.Typer(help="Inspect available robots and launch them from the CLI.")
console = Console()


def _find_spec(module: str):
    try:
        return importlib.util.find_spec(module)
    except ModuleNotFoundError:
        return None


@dataclass
class RobotDescriptor:
    name: str
    module: str
    run_module: str
    description: str = ""
    extra: Optional[str] = None

    def spec(self):  # pragma: no cover - thin wrapper
        return _find_spec(self.module)

    def run_spec(self):  # pragma: no cover - thin wrapper
        return _find_spec(self.run_module)

    def is_installed(self) -> bool:
        return self.spec() is not None


KNOWN_ROBOTS: dict[str, RobotDescriptor] = {
    "franka": RobotDescriptor(
        name="franka",
        module="eigen.robots.franka_panda.franka_panda",
        run_module="eigen.robots.franka",
        description="Franka Emika Panda manipulator",
        extra="franka",
    ),
    "so100": RobotDescriptor(
        name="so100",
        module="eigen.robots.so100.so100",
        run_module="eigen.robots.so100",
        description="Eigen SO-100 6-DoF arm",
    ),
}


def _get_descriptor(name: str) -> Optional[RobotDescriptor]:
    return KNOWN_ROBOTS.get(name.lower())


def _driver_status(descriptor: RobotDescriptor) -> tuple[str, Optional[str]]:
    try:
        module = importlib.import_module(descriptor.module)
    except ModuleNotFoundError as exc:
        return "-", f"Missing dependency: {exc.name}"
    except Exception as exc:  # pragma: no cover - defensive
        return "-", f"Import error: {exc}"

    drivers_enum = getattr(module, "Drivers", None)
    if drivers_enum is None:
        return "-", None

    entries: list[str] = []
    note: Optional[str] = None
    for member in drivers_enum:
        driver_cls = member.value
        runnable = getattr(driver_cls, "_runnable", True)
        symbol = "✓" if runnable else "✗"
        label = member.name.lower()
        entries.append(f"{label} {symbol}")
        if not runnable and descriptor.extra and note is None:
            note = f"Install extra '{descriptor.extra}' to enable {label}."

    return ", ".join(entries) if entries else "-", note


@app.command()
def list() -> None:  # noqa: D401 - Typer provides the help string
    """List robots bundled with Eigen Robotics and their availability."""

    table = Table(title="Robots", header_style="bold")
    table.add_column("Robot", justify="left", style="cyan")
    table.add_column("Installed", justify="center", style="green")
    table.add_column("Drivers", justify="left", style="magenta")
    table.add_column("Notes", justify="left", style="yellow")

    for descriptor in KNOWN_ROBOTS.values():
        installed = descriptor.is_installed()
        installed_symbol = "✓" if installed else "✗"
        drivers_display = "-"
        notes: list[str] = []

        if descriptor.description:
            notes.append(descriptor.description)

        if installed:
            drivers_display, driver_note = _driver_status(descriptor)
            if driver_note:
                notes.append(driver_note)
        else:
            if descriptor.extra:
                notes.append(f"Install extra '{descriptor.extra}'")
            else:
                notes.append("Not installed")

        table.add_row(
            descriptor.name,
            installed_symbol,
            drivers_display,
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
        help="Override the robot component name passed to the runner.",
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
    """Launch a robot embodiment by name."""

    descriptor = _get_descriptor(name)
    if descriptor is None:
        console.print(f"[red]Unknown robot '{name}'.[/red]")
        raise typer.Exit(1)

    if descriptor.run_spec() is None:
        console.print(
            f"[red]Robot '{descriptor.name}' is not available in this environment.[/red]"
        )
        if descriptor.extra:
            console.print(
                f"Install the 'eigen-robots[{descriptor.extra}]' extra to enable it."
            )
        raise typer.Exit(1)

    # FORCES the parent folder and the robots name.py file to be the same
    cmd = [sys.executable, "-m", descriptor.module]
    if robot_name:
        cmd += ["--name", robot_name]
    if config_path:
        cmd += ["--config", str(config_path)]
    console.print(
        f"Launching '{descriptor.name}' via module '{descriptor.run_module}'."
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


if __name__ == "__main__":  # pragma: no cover - manual invocation helper
    main()
