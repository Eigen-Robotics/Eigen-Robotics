"""CLI commands for component registry management."""

import importlib
import pkgutil

from rich.console import Console
from rich.table import Table
import typer

from eigen.core.system.component_registry import list_components

app = typer.Typer()
console = Console()


def _discover_and_import_components(debug: bool = False):
    """Discover and import all available eigen component modules."""
    # List of eigen packages that might contain components
    eigen_packages = ["eigen.robots", "eigen.sensors", "eigen.objects"]

    for package_name in eigen_packages:
        try:
            # Try to import the package
            package = importlib.import_module(package_name)
            if debug:
                console.print(f"[dim]Found package: {package_name}[/dim]")

            # Walk through all submodules recursively in the package
            if hasattr(package, "__path__"):
                for _, modname, _ in pkgutil.walk_packages(
                    package.__path__,
                    prefix=package.__name__ + ".",
                    onerror=lambda x: None,  # Continue on errors
                ):
                    try:
                        # Import each module to trigger component registrations
                        if debug:
                            console.print(f"[dim]Importing: {modname}[/dim]")
                        importlib.import_module(modname)
                    except ImportError as e:
                        # Skip modules with missing optional dependencies
                        # This allows components to be registered even if runtime deps are missing
                        if debug:
                            console.print(
                                f"[dim yellow]Skipped {modname} (ImportError): {e}[/dim yellow]"
                            )
                        pass
                    except Exception as e:
                        # Skip any other import errors (e.g., syntax errors, circular imports)
                        if debug:
                            console.print(
                                f"[dim red]Error importing {modname}: {e}[/dim red]"
                            )
                        pass

        except ImportError:
            # Package not installed, skip it
            if debug:
                console.print(
                    f"[dim]Package not available: {package_name}[/dim]"
                )
            pass
        except Exception as e:
            # Any other error, skip this package
            if debug:
                console.print(
                    f"[dim red]Error with package {package_name}: {e}[/dim red]"
                )
            pass


@app.command()
def list(
    debug: bool = typer.Option(
        False, "--debug", help="Show debug output during component discovery"
    ),
    no_discovery: bool = typer.Option(
        False, "--no-discovery", help="Skip automatic component discovery"
    ),
):
    """List all registered components in the component registry."""
    # Discover and import all available components first (unless disabled)
    if not no_discovery:
        _discover_and_import_components(debug)

    components = list_components()

    if not components:
        console.print("No components registered.")
        return

    # Create table
    table = Table(title="Registered Components")
    table.add_column("ID", justify="left", style="cyan")
    table.add_column("Type", justify="left", style="magenta")
    table.add_column("Is Driver", justify="center", style="green")
    table.add_column("Is Default", justify="center", style="yellow")

    # Sort components by component_id for consistent output
    sorted_components = sorted(
        components.items(), key=lambda x: x[0].component_id
    )

    for component_key, _ in sorted_components:
        table.add_row(
            component_key.component_id,
            component_key.component_type.value,
            "✓" if component_key.is_driver else "✗",
            "✓" if component_key.is_default else "✗",
        )

    console.print(table)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
