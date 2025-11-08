from __future__ import annotations

from typing import Any, Callable

import pytest

from eigen import types as eigen_types


def _make_time(sec: int, nanosec: int) -> eigen_types.time_t:
    stamp = eigen_types.time_t()
    stamp.sec = sec
    stamp.nanosec = nanosec
    return stamp


TYPE_FIXTURES: list[tuple[str, type[Any], dict[str, Any | Callable[[], Any]]]] = [
    ("bool_t", eigen_types.bool_t, {"data": True}),
    ("byte_t", eigen_types.byte_t, {"data": -12}),
    ("char_t", eigen_types.char_t, {"data": 65}),
    (
        "color_rgba_t",
        eigen_types.color_rgba_t,
        {"r": 0.1, "g": 0.5, "b": 0.9, "a": 1.0},
    ),
    (
        "double_array_t",
        eigen_types.double_array_t,
        {"m": 3, "n": 2, "data": [1.5, -2.5, 3.5]},
    ),
    (
        "double_vector_t",
        eigen_types.double_vector_t,
        {"n": 3, "data": [0.25, 1.25, 2.25]},
    ),
    ("empty_t", eigen_types.empty_t, {}),
    (
        "example_t",
        eigen_types.example_t,
        {
            "timestamp": 123456789,
            "position": [1.0, -2.0, 3.0],
            "orientation": [0.0, 0.1, 0.2, 0.3],
            "num_ranges": 3,
            "ranges": [100, 200, -300],
            "name": "sensor-1",
            "enabled": True,
        },
    ),
    ("float_32_t", eigen_types.float_32_t, {"data": 3.14159}),
    ("float_64_t", eigen_types.float_64_t, {"data": 2.718281828}),
    (
        "float_array_t",
        eigen_types.float_array_t,
        {"m": 2, "n": 4, "data": [10.5, -0.25]},
    ),
    (
        "float_vector_t",
        eigen_types.float_vector_t,
        {"n": 4, "data": [1.0, 2.0, 3.0, 4.0]},
    ),
    (
        "header_t",
        eigen_types.header_t,
        {"stamp": lambda: _make_time(99, 123456), "frame_id": "base_link"},
    ),
    (
        "int64_vector_t",
        eigen_types.int64_vector_t,
        {"n": 3, "data": [1, 2, 3]},
    ),
    ("int_16_t", eigen_types.int_16_t, {"data": 12345}),
    ("int_32_t", eigen_types.int_32_t, {"data": 2_000_000_000}),
    ("int_64_t", eigen_types.int_64_t, {"data": -9_223_372_000}),
    ("int_8_t", eigen_types.int_8_t, {"data": -64}),
    ("string_t", eigen_types.string_t, {"data": "Eigen Robotics"}),
    ("time_t", eigen_types.time_t, {"sec": 42, "nanosec": 12345}),
    ("uint_8_t", eigen_types.uint_8_t, {"data": 250}),
]


def _build_message(type_cls: type[Any], overrides: dict[str, Any | Callable[[], Any]]):
    message = type_cls()
    for attr, raw_value in overrides.items():
        value = raw_value() if callable(raw_value) else raw_value
        if isinstance(value, list):
            value = list(value)
        elif isinstance(value, tuple):
            value = list(value)
        setattr(message, attr, value)
    return message


def _slot_names(value: Any) -> tuple[str, ...] | None:
    slots = getattr(value.__class__, "__slots__", None)
    if slots is None:
        return None
    if isinstance(slots, str):
        return (slots,)
    return tuple(slots)


def _assert_fields_equal(expected: Any, actual: Any):
    expected_slots = _slot_names(expected)
    actual_slots = _slot_names(actual)
    if expected_slots is not None and actual_slots is not None:
        for slot in expected_slots:
            _assert_fields_equal(getattr(expected, slot), getattr(actual, slot))
        return

    if isinstance(expected, (list, tuple)) or isinstance(actual, (list, tuple)):
        expected_seq = list(expected) if isinstance(expected, (list, tuple)) else [expected]
        actual_seq = list(actual) if isinstance(actual, (list, tuple)) else [actual]
        assert len(expected_seq) == len(actual_seq)
        for exp_item, act_item in zip(expected_seq, actual_seq):
            _assert_fields_equal(exp_item, act_item)
        return

    if isinstance(expected, float) or isinstance(actual, float):
        assert actual == pytest.approx(expected)
        return

    assert actual == expected


@pytest.fixture(params=TYPE_FIXTURES, ids=lambda param: param[0])
def type_instance(request):
    _, type_cls, payload = request.param
    return type_cls, _build_message(type_cls, payload)


def test_all_generated_types_are_covered():
    from eigen.types import generated

    exported = set(generated.__all__)
    covered = {name for name, _, _ in TYPE_FIXTURES}
    assert covered == exported


def test_encode_decode_roundtrip(type_instance):
    type_cls, message = type_instance
    decoded = type_cls.decode(message.encode())
    _assert_fields_equal(message, decoded)


def test_decode_rejects_wrong_fingerprint(type_instance):
    type_cls, message = type_instance
    encoded = bytearray(message.encode())
    encoded[0] ^= 0xFF
    with pytest.raises(ValueError):
        type_cls.decode(bytes(encoded))
