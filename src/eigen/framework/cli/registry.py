import typer

from eigen.core.client.comm_infrastructure.registry import Registry

app = typer.Typer()


@app.command()
def start(
    registry_host: str = typer.Option(
        "127.0.0.1", "--host", help="The host address for the registry server."
    ),
    registry_port: int = typer.Option(
        1234, "--port", help="The port for the registry server."
    ),
):
    """!
    Start the Registry server with the specified host and port.

    @param registry_host: Host address for the registry server.
    @param registry_port: Port for the registry server.
    """
    server = Registry(registry_host=registry_host, registry_port=registry_port)
    server.start()


def main():
    """! Entry point for the CLI."""
    app()  # Initializes the Typer CLI


if __name__ == "__main__":
    main()
