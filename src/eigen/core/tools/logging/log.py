from datetime import datetime
import logging
from typing import Any


# =========================
# Colors
# =========================
class bcolors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    WHITE = "\033[97m"
    GREY = "\033[90m"


# =========================
# Custom log level: OK
# =========================
OK_LEVEL_NUM = 25
logging.addLevelName(OK_LEVEL_NUM, "OK")


def logger_ok(self: logging.Logger, message: str, *args: Any, **kwargs: Any) -> None:
    """Custom log method for OK level (between INFO and WARNING)."""
    if self.isEnabledFor(OK_LEVEL_NUM):
        self._log(OK_LEVEL_NUM, message, args, **kwargs)


logging.Logger.ok = logger_ok  # type: ignore[attr-defined]


# =========================
# Panda-style log helper
# =========================
def apply_panda_style(text: str) -> str:
    """Alternate between white and grey per character."""
    colors = [bcolors.WHITE, bcolors.GREY]
    styled_text = "".join(colors[i % 2] + c for i, c in enumerate(text))
    return styled_text + bcolors.ENDC


def logger_panda(
    self: logging.Logger, message: str, *args: Any, **kwargs: Any
) -> None:
    """Log a message using panda styling at INFO level."""
    if self.isEnabledFor(logging.INFO):
        styled_message = apply_panda_style(message)
        self._log(logging.INFO, styled_message, args, **kwargs)


logging.Logger.panda = logger_panda  # type: ignore[attr-defined]


# =========================
# Formatter
# =========================
class CustomFormatter(logging.Formatter):
    """Colorized formatter with timestamps."""

    COLORS: dict[str, str] = {
        "DEBUG": bcolors.OKBLUE,
        "INFO": bcolors.OKCYAN,
        "OK": bcolors.OKGREEN + bcolors.BOLD,
        "WARNING": bcolors.WARNING,
        "ERROR": bcolors.FAIL,
        "CRITICAL": bcolors.FAIL + bcolors.BOLD,
        "NOTSET": bcolors.ENDC,
    }

    def __init__(
        self,
        fmt: str = "[%(levelname)s] [%(asctime)s] - %(message)s",
        datefmt: str = "%H:%M:%S.%f",
    ) -> None:
        super().__init__(fmt, datefmt)

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:  # noqa: N802
        if datefmt:
            return datetime.fromtimestamp(record.created).strftime(datefmt)
        return (
            datetime.fromtimestamp(record.created).strftime("%H:%M:%S.")
            + f"{int(record.msecs):02d}"
        )

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        color = self.COLORS.get(record.levelname, bcolors.ENDC)
        return f"{color}{base}{bcolors.ENDC}"


# =========================
# Logger setup
# =========================
def setup_logger(name: str = "my_logger") -> logging.Logger:
    """Configure and return a logger with the custom formatter."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # avoid duplicates if called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            CustomFormatter(
                fmt="[%(levelname)s] [%(asctime)s] - %(message)s",
                datefmt="%H:%M:%S.%f",
            )
        )
        logger.addHandler(handler)

    return logger


# =========================
# Utility: query
# =========================
def query(logger: logging.Logger, msg: str) -> str:
    """Prompt the user and log that we asked them."""
    logger.info("querying user")
    print(msg)
    return input(">> ")


# =========================
# Exported logger
# =========================
log = setup_logger()
log.query = lambda msg: query(log, msg)  # type: ignore[attr-defined]

__all__ = ["log"]


# =========================
# Demo
# =========================
if __name__ == "__main__":
    usrin = log.query("ready?")
    log.debug(f"user said '{usrin}'")
    log.ok("all good")
    log.info("hello world")
    log.warning("warn message")
    log.error("oh no")
    log.critical("bad times")
    log.panda("this is a panda log")
