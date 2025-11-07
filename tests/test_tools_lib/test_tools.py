import logging

from eigen.core.tools import log
from eigen.core.tools.logging.log import (
    CustomFormatter,
    OK_LEVEL_NUM,
    apply_panda_style,
    bcolors,
    log as default_log,
    setup_logger,
)


def test_logging_import() -> None:
    assert hasattr(log, "info")
    assert hasattr(log, "warning")
    assert hasattr(log, "error")
    assert hasattr(log, "debug")


def test_setup_logger_is_idempotent() -> None:
    logger = setup_logger("pytest-eigen-log")
    handler_count = len(logger.handlers)

    logger_again = setup_logger("pytest-eigen-log")

    assert len(logger_again.handlers) == handler_count
    assert isinstance(logger_again.handlers[0].formatter, CustomFormatter)


def test_apply_panda_style_alternates_colors() -> None:
    styled = apply_panda_style("AB")

    assert styled.startswith(bcolors.WHITE + "A" + bcolors.GREY + "B")
    assert styled.endswith(bcolors.ENDC)


def test_ok_level_logs_with_custom_levelname(caplog) -> None:
    logger = setup_logger("pytest-ok-level")

    with caplog.at_level(OK_LEVEL_NUM):
        logger.ok("system online")

    matching = [record for record in caplog.records if record.levelno == OK_LEVEL_NUM]
    assert matching, "Expected OK-level log record"
    assert matching[0].levelname == "OK"
    assert "system online" in matching[0].message


def test_log_query_prompts_and_returns_input(monkeypatch, capsys, caplog) -> None:
    responses = iter(["42"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    with caplog.at_level(logging.INFO):
        answer = default_log.query("Ready?")

    captured = capsys.readouterr()
    assert "Ready?" in captured.out
    assert answer == "42"
    assert any("querying user" in record.message for record in caplog.records)
