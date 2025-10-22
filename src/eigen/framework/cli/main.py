import typer

from . import (
    components,
    graph,
    image_veiwer,
    launcher,
    network,
    registry,
    robot,
    sensor,
)

app = typer.Typer()

# Core tooling
app.add_typer(registry.app, name="registry")
app.add_typer(graph.app, name="graph")
app.add_typer(launcher.app, name="launcher")
app.add_typer(components.app, name="components")
app.add_typer(robot.app, name="robot")
app.add_typer(sensor.app, name="sensor")
app.add_typer(sensor.app, name="sensors")

# Network inspection utilities
app.add_typer(network.node, name="node")
app.add_typer(network.channel, name="channel")
app.add_typer(network.service, name="service")
app.add_typer(image_veiwer.app, name="view")


def main():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
