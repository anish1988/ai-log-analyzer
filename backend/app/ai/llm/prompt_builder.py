"""
Prompt construction for AI log analysis.

SEVERITY ASSESSMENT
===================

Determine the severity independently based on:
- the actual error evidence
- impact indicated by the logs
- affected component/system
- historical RAG context when available

Do NOT simply copy the severity supplied in CURRENT ERROR DATA.

Return exactly one severity:
CRITICAL, HIGH, MEDIUM, LOW, or INFO.

If the supplied severity is UNKNOWN or empty, you must still
make your own assessment from the available evidence.
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

        lines = error.get(
            "lines",
            [],
        )

        important_lines = []

        for line in lines:

            if not isinstance(
                line,
                dict,
            ):
                continue

            important_lines.append(
                {
                    "line_number": line.get(
                        "line_number"
                    ),

                    "content": line.get(
                        "raw"
                    ),
                }
            )

        payload = {

            "log_type": log_type,

            "current_error": {

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

                "tier": error.get(
                    "tier"
                ),

                "server": error.get(
                    "server"
                ),

                "file_name": error.get(
                    "file_name"
                ),

                "file_path": error.get(
                    "file_path"
                ),

                "start_line": error.get(
                    "start_line"
                ),

                "end_line": error.get(
                    "end_line"
                ),

                "total_lines": error.get(
                    "total_lines"
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

        return f"""
Perform a detailed root-cause analysis of the supplied
{log_type} error.

Use the system instructions as the analysis contract.

CURRENT ERROR DATA
==================

{json.dumps(
    payload,
    indent=2,
    default=str,
)}

IMPORTANT:
- Use the supplied log lines as primary evidence.
- Do not invent source-code locations.
- Do not treat historical RAG information as automatically correct.
- Clearly identify missing information.
- Return the requested structured response.
"""