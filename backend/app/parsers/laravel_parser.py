from abc import ABC, abstractmethod

from app.schemas.web_log_analysis import WebLogFileSchema


class BaseLogParser(ABC):

    @abstractmethod
    def parse(
        self,
        *,
        server: str,
        log_type: str,
        file_name: str,
        file_path: str,
        raw_lines: list[str],
    ) -> WebLogFileSchema:
        """
        Convert raw log lines into structured JSON.
        """
        raise NotImplementedError