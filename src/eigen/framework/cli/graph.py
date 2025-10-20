import argparse

import typer

from eigen.core.tools.eigen_graph.eigen_graph import EigenGraph
from eigen.core.tools.log import log

app = typer.Typer()


def parse_args():
    """
    Parse command-line arguments for running EigenGraph as a script.

    Returns:
        argparse.Namespace: The parsed arguments with `registry_host` and `registry_port`.
    """
    parser = argparse.ArgumentParser(
        description="EigenGraph - Visualize your NOAHR network."
    )
    parser.add_argument(
        "--registry_host",
        type=str,
        default="127.0.0.1",
        help="The host address for the registry server.",
    )
    parser.add_argument(
        "--registry_port",
        type=int,
        default=1234,
        help="The port for the registry server.",
    )
    return parser.parse_args()


@app.command()
def start(
    registry_host: str = typer.Option(
        "127.0.0.1", "--host", help="The host address for the registry server."
    ),
    registry_port: int = typer.Option(
        1234, "--port", help="The port for the registry server."
    ),
):
    """Starts the graph with specified host and port."""
    # TODO(FV): review, remova noqa
    server = EigenGraph(registry_host=registry_host, registry_port=registry_port)  # noqa: F841


@app.command()
def save(
    file_path: str,
    registry_host: str = typer.Option(
        "127.0.0.1", "--host", help="The host address for the registry server."
    ),
    registry_port: int = typer.Option(
        1234, "--port", help="The port for the registry server."
    ),
):
    """Save the graph image to ``FILE_PATH`` without displaying it.

    ``FILE_PATH`` must end with ``.png``.
    """
    server = EigenGraph(
        registry_host=registry_host, registry_port=registry_port, display=False
    )
    try:
        server.save_image(file_path)
    except ValueError as exc:
        log.error(str(exc))
        raise typer.Exit(code=1) from exc
    else:
        log.ok(f"Graph saved to {file_path}")


def main():
    """Entry point for the CLI."""
    app()  # Initializes the Typer CLI


if __name__ == "__main__":
    main()
