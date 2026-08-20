"""
AI analysis configuration.
"""

from __future__ import annotations

import os


def is_rag_enabled() -> bool:
    """
    Return whether the RAG pipeline is enabled.

    Defaults to enabled so existing behavior is preserved.
    """

    value = os.getenv(
        "AI_RAG_ENABLED",
        "true",
    )

    return value.strip().lower() in {
        "true",
        "1",
        "yes",
        "on",
    }