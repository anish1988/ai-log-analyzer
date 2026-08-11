"""
Prompt construction for AI log analysis.

This file provides the common prompt structure.

Log-type-specific instructions are provided by the
individual analyzer classes.
"""

import json
from typing import Any


class PromptBuilder:

    @staticmethod
    def build_user_prompt(
        *,
        error: dict[str, Any],
        log_type: str,
        historical_context: dict[str, Any] | None = None,
    ) -> str:
        """
        Build the user-side analysis prompt.

        The prompt contains the actual error information.

        Historical RAG information is optional because:

            LLM_REQUIRED
                → no historical match may exist.

            REVIEW
                → historical information should be included.
        """

        lines = error.get(
            "lines",
            [],
        )

        important_lines = []

        for line in lines:

            if isinstance(
                line,
                dict,
            ):

                important_lines.append(
                    {
                        "line_number": line.get(
                            "line_number"
                        ),
                        "raw": line.get(
                            "raw"
                        ),
                    }
                )

        payload = {
            "log_type": log_type,

            "error": {
                "error_id": error.get(
                    "error_id"
                ),

                "title": error.get(
                    "title"
                ),

                "severity": error.get(
                    "severity"
                ),

                "timestamp": error.get(
                    "timestamp"
                ),

                "server": error.get(
                    "server"
                ),

                "file_name": error.get(
                    "file_name"
                ),

                "start_line": error.get(
                    "start_line"
                ),

                "end_line": error.get(
                    "end_line"
                ),

                "error_content": error.get(
                    "error_content"
                ),

                "important_log_lines": (
                    important_lines
                ),
            },

            "historical_rag_context": (
                historical_context
            ),
        }

        return (
            "Analyze the following log error.\n\n"
            "The response must follow the required "
            "structured analysis format.\n\n"
            "Input data:\n"
            f"{json.dumps(payload, indent=2, default=str)}"
        )