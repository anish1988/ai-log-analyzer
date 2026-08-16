"""
Phase 3.6 - Automation Result Writer.

Stores one complete AI/Jira response per error.

Directory structure:

    /app/automation/responses/
        YYYY-MM-DD/
            <error_id>__<run_id>.json

The run_id is included in the filename so that a retry never
silently overwrites a previous response for the same error.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AutomationResultWriter:
    """
    Writes complete automation results to date-wise JSON files.
    """

    DEFAULT_DIRECTORY = (
        "/app/automation/responses"
    )

    def __init__(
        self,
        base_directory: str | Path | None = None,
    ) -> None:

        self.base_directory = Path(
            base_directory
            or self.DEFAULT_DIRECTORY
        )

    async def write(
        self,
        *,
        run_id: str,
        analysis: dict[str, Any],
        jira: dict[str, Any],
    ) -> Path:
        """
        Write one complete response file.

        Returns
        -------
        Path
            Path of the generated JSON file.
        """

        now = datetime.now(
            timezone.utc
        )

        date_directory = (
            self.base_directory
            / now.strftime("%Y-%m-%d")
        )

        date_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        error_id = self._safe_filename(
            str(
                analysis.get(
                    "error_id",
                    "unknown-error",
                )
            )
        )

        safe_run_id = self._safe_filename(
            run_id
        )

        file_name = (
            f"{error_id}__{safe_run_id}.json"
        )

        output_path = (
            date_directory
            / file_name
        )

        payload = {
            "run_id": run_id,
            "created_at": now.isoformat(),
            "error_id": analysis.get(
                "error_id"
            ),
            "server": analysis.get(
                "server"
            ),
            "log_type": analysis.get(
                "log_type"
            ),
            "analysis": analysis,
            "jira": jira,
        }

        output_path.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
                default=str,
            ),
            encoding="utf-8",
        )

        return output_path

    @staticmethod
    def _safe_filename(
        value: str,
    ) -> str:

        value = value.strip()

        if not value:
            return "unknown"

        return re.sub(
            r"[^A-Za-z0-9_.-]",
            "_",
            value,
        )