from eigen.core.tools import log


def test_logging_import() -> None:
    assert hasattr(log, "info")
    assert hasattr(log, "warning")
    assert hasattr(log, "error")
    assert hasattr(log, "debug")
