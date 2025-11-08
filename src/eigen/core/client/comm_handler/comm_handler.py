from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from lcm import LCM


class CommHandler(ABC):
    """Base interface for every communication primitive."""

    def __init__(self, channel_name: str, comm_type: str) -> None:
        self.channel_name = channel_name
        self.comm_type = comm_type
        self.active = True

    def __repr__(self) -> str:
        return self.channel_name

    def shutdown(self) -> None:
        """Provide a common alias for ``suspend``."""
        self.suspend()

    @abstractmethod
    def get_info(self) -> dict:
        """Return a dictionary describing the handler."""

    @abstractmethod
    def suspend(self) -> None:
        """Suspend the handler."""

    @abstractmethod
    def restart(self) -> None:
        """Restart the handler."""


class LCMCommHandler(CommHandler):
    """Shared functionality for handlers that rely on a live LCM instance."""

    def __init__(
        self,
        lcm: LCM | Any,  # Accept dummy transports in tests.
        channel_name: str,
        channel_type: type,
        comm_type: str,
    ) -> None:
        super().__init__(channel_name, comm_type)
        self._lcm: LCM | Any = lcm
        self.channel_type = channel_type

    def __repr__(self) -> str:
        return f"{self.channel_name}[{self.channel_type.__name__}]"
