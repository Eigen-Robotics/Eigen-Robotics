from .main import main

try:
    import typer
except ImportError:
    print("Please instal the [cli] extra.")
    exit(1)

__all__ = ["main"]
