"""
Base interface for log-type-specific AI analyzers.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseLogAnalyzer(ABC):

    @abstractmethod
    def get_system_prompt(
        self,
    ) -> str:
        """
        Return system instructions for this log type.
        """

        raise NotImplementedError

    @abstractmethod
    async def analyze(
        self,
        *,
        error: dict[str, Any],
        historical_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze one error.
        """

        raise NotImplementedError