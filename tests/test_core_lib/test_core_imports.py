import eigen.core


def test_eigen_core_import() -> None:
    assert eigen.core is not None


def test_version_exists():
    from eigen import __version__

    assert __version__ is not None
