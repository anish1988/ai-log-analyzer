"""
Parser for structured LLM responses.

The LLM should eventually return JSON matching our
AI analysis schema.

This parser provides one controlled boundary between
the LLM and the rest of the application.
"""

import json
from typing import Any


class LLMResponseParser:

    @staticmethod
    def parse(
        response: str,
    ) -> dict[str, Any]:

        if not response.strip():

            raise ValueError(
                "LLM returned an empty response."
            )

        try:

            data = json.loads(
                response
            )

        except json.JSONDecodeError as exc:

            raise ValueError(
                "LLM returned invalid JSON."
            ) from exc

        if not isinstance(
            data,
            dict,
        ):

            raise ValueError(
                "LLM response must be a JSON object."
            )

        return data