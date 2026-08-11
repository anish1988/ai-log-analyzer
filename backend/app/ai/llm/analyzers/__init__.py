"""
Log analyzer factory.
"""

from app.ai.llm.analyzers.base import BaseLogAnalyzer
from app.ai.llm.analyzers.mysql import MySQLLogAnalyzer
from app.ai.llm.analyzers.telephony import TelephonyLogAnalyzer
from app.ai.llm.analyzers.web import WebLogAnalyzer
from app.ai.llm.llm_service import LLMService


class AnalyzerFactory:

    @staticmethod
    def get_analyzer(
        log_type: str,
        llm_service: LLMService,
    ) -> BaseLogAnalyzer:

        normalized = (
            log_type
            .strip()
            .lower()
        )

        if normalized.startswith(
            (
                "laravel",
                "apache",
                "web",
            )
        ):

            return WebLogAnalyzer(
                llm_service
            )

        if normalized.startswith(
            (
                "asterisk",
                "vicidial",
                "telephony",
                "agi",
            )
        ):

            return TelephonyLogAnalyzer(
                llm_service
            )

        if normalized.startswith(
            (
                "mysql",
                "mariadb",
                "database",
            )
        ):

            return MySQLLogAnalyzer(
                llm_service
            )

        raise ValueError(
            f"No AI analyzer configured for "
            f"log type '{log_type}'."
        )