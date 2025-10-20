def test_import_eigen():
    import eigen
    assert hasattr(eigen, "__version__") or True  # just proving import works

def test_import_robots():
    from eigen import robots
    assert robots is not None

def test_import_sensors():
    from eigen import sensors
    assert sensors is not None

def test_import_types():
    from eigen.types import bullet_dynamics_t, flag_t
    assert bullet_dynamics_t is not None
    assert flag_t is not None

def test_import_cli():
    from eigen import cli
    assert cli is not None

def test_import_core():
    from eigen import core
    assert core is not None

def test_import_types_utils():
    from eigen.types.utils import unpack
    assert unpack is not None