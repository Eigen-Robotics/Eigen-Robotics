import pytest

from eigen.core.client import Listener, Publisher, Subscriber


class DummyMessage:
    def __init__(self, payload: str) -> None:
        self.payload = payload

    @staticmethod
    def encode(msg: "DummyMessage") -> bytes:
        return msg.payload.encode("utf-8")

    @staticmethod
    def decode(data: bytes) -> "DummyMessage":
        return DummyMessage(data.decode("utf-8"))


class ExplodingMessage(DummyMessage):
    @staticmethod
    def decode(data: bytes) -> "DummyMessage":  # type: ignore[override]
        raise ValueError("boom")


class DummySubscription:
    def __init__(self, callback, channel_name: str) -> None:
        self.callback = callback
        self.channel_name = channel_name
        self.queue_capacity: int | None = None

    def set_queue_capacity(self, capacity: int) -> None:
        self.queue_capacity = capacity

    def dispatch(self, data: bytes) -> None:
        self.callback(self.channel_name, data)


class DummyLCM:
    def __init__(self) -> None:
        self.subscriptions: dict[str, DummySubscription] = {}
        self.unsubscribed: list[DummySubscription] = []
        self.published: list[tuple[str, bytes]] = []
        self.subscribe_calls = 0

    def subscribe(self, channel_name, callback):
        self.subscribe_calls += 1
        subscription = DummySubscription(callback, channel_name)
        self.subscriptions[channel_name] = subscription
        return subscription

    def unsubscribe(self, subscription):
        self.unsubscribed.append(subscription)

    def publish(self, channel_name: str, data: bytes) -> None:
        self.published.append((channel_name, data))

    def dispatch(self, channel_name: str, data: bytes) -> None:
        self.subscriptions[channel_name].dispatch(data)


def _assert_instantiable(cls: type) -> None:
    try:

        class _Test(cls):
            pass
    except Exception as e:  # pragma: no cover - safety net
        assert False, f"Importing or subclassing {cls.__name__} failed: {e}"


def test_comm_handler_import() -> None:
    classes_to_check = [
        Subscriber,
        Listener,
        Publisher,
    ]

    for cls in classes_to_check:
        _assert_instantiable(cls)


def test_subscriber_invokes_callback_with_decoded_message() -> None:
    fake_lcm = DummyLCM()
    received: list[tuple[str, str, str]] = []

    Subscriber(
        fake_lcm,
        "STATE",
        DummyMessage,
        lambda t, ch, msg, extra: received.append((ch, msg.payload, extra)),
        callback_args=["extra"],
    )

    fake_lcm.dispatch("STATE", DummyMessage.encode(DummyMessage("ready")))

    assert received == [("STATE", "ready", "extra")]
    assert fake_lcm.subscriptions["STATE"].queue_capacity == 1


def test_subscriber_logs_decode_failure(caplog) -> None:
    fake_lcm = DummyLCM()
    callback_calls: list[tuple] = []

    Subscriber(fake_lcm, "STATE", ExplodingMessage, lambda *args: callback_calls.append(args))

    with caplog.at_level("WARNING"):
        fake_lcm.dispatch("STATE", b"bad payload")

    assert callback_calls == []
    assert any("failed to decode message" in record.message for record in caplog.records)


def test_subscriber_suspend_and_restart() -> None:
    fake_lcm = DummyLCM()
    subscriber = Subscriber(fake_lcm, "STATE", DummyMessage, lambda *args: None)

    first_subscription = subscriber._sub  # type: ignore[attr-defined]
    subscriber.suspend()
    assert subscriber.active is False
    assert fake_lcm.unsubscribed == [first_subscription]

    prior_calls = fake_lcm.subscribe_calls
    subscriber.restart()

    assert subscriber.active is True
    assert fake_lcm.subscribe_calls == prior_calls + 1
    assert subscriber._sub is not first_subscription  # type: ignore[attr-defined]


def test_publisher_publish_respects_enabled_state(caplog) -> None:
    fake_lcm = DummyLCM()
    publisher = Publisher(fake_lcm, "STATE", DummyMessage)
    msg = DummyMessage("payload")

    publisher.publish(msg)
    assert fake_lcm.published == [("STATE", DummyMessage.encode(msg))]

    publisher.suspend()
    with caplog.at_level("WARNING"):
        publisher.publish(msg)
    assert len(fake_lcm.published) == 1
    assert any("not enabled" in record.message for record in caplog.records)

    publisher.restart()
    publisher.publish(msg)
    assert len(fake_lcm.published) == 2


def test_publisher_rejects_wrong_message_type() -> None:
    publisher = Publisher(DummyLCM(), "STATE", DummyMessage)

    with pytest.raises(AssertionError):
        publisher.publish(object())  # type: ignore[arg-type]


def test_listener_tracks_latest_message_and_returns_copy() -> None:
    fake_lcm = DummyLCM()
    listener = Listener(fake_lcm, "POSE", DummyMessage)

    assert listener.received() is False

    fake_lcm.dispatch("POSE", DummyMessage.encode(DummyMessage("pose-1")))

    assert listener.received() is True
    first = listener.get()
    assert isinstance(first, DummyMessage)
    assert first.payload == "pose-1"

    first.payload = "mutated"
    assert listener.get().payload == "pose-1"

    listener.suspend()
    assert listener.received() is False
