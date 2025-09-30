import typer

from eigen.core.client.comm_infrastructure.base_node import main
from eigen.core.tools.visualization.image_viewer import ImageViewNode

app = typer.Typer()


@app.command()
def start(
    channel: str = typer.Option("image/sim", help="Channel to listen to"),
    image_type: str = typer.Option(
        "image",
        help="Type of image message: image, depth, or rgbd",
    ),
):
    """Start the image viewer node."""
    main(ImageViewNode, channel, image_type)


def cli_main():
    app()


if __name__ == "__main__":
    cli_main()
