from eigen.core.client import Subscriber
from eigen.core.client import Listener
from eigen.core.client import Publisher


def _assert_instantiable(cls: type) -> None:
    """Assert that `cls` can be subclassed (i.e. is importable and valid)."""
    try:
        class _Test(cls):
            pass
    except Exception as e:
        assert False, f"Importing or subclassing {cls.__name__} failed: {e}"


def test_comm_handler_import() -> None:
    classes_to_check = [
        Subscriber,
        Listener,
        Publisher,
    ]

    for cls in classes_to_check:
        _assert_instantiable(cls)
