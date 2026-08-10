"""
Embedding Text Builder.

Creates the semantic representation that will be converted
into a vector and stored in the RAG knowledge base.
"""

from typing import Any

from app.ai.graph.state import SelectedError


def build_embedding_text(
    error: SelectedError,
    *,
    root_cause: str = "",
    solution: str = "",
    optimization: str = "",
) -> str:
    """
    Build the semantic text used to create the RAG embedding.

    The text intentionally includes:

        - log type
        - server
        - file
        - error title
        - severity
        - error content
        - important log lines
        - root cause
        - solution
        - optimization

    This gives the embedding model enough context to identify
    similar historical problems.
    """

    lines = error.get("lines", [])

    important_lines: list[str] = []

    for line in lines:

        line_number = line.get("line_number")

        raw = line.get("raw", "")

        if raw:

            important_lines.append(
                f"Line {line_number}: {raw}"
            )

    parts: list[str] = []

    parts.append(
        f"Log Type: {error.get('log_type', '')}"
    )

    parts.append(
        f"Tier: {error.get('tier', '')}"
    )

    parts.append(
        f"Server: {error.get('server', '')}"
    )

    parts.append(
        f"File: {error.get('file_name', '')}"
    )

    parts.append(
        f"Severity: {error.get('severity', '')}"
    )

    parts.append(
        f"Error Title: {error.get('title', '')}"
    )

    parts.append(
        f"Error Content: {error.get('error_content', '')}"
    )

    if important_lines:

        parts.append(
            "Important Log Lines:\n"
            + "\n".join(important_lines)
        )

    if root_cause:

        parts.append(
            f"Root Cause: {root_cause}"
        )

    if solution:

        parts.append(
            f"Solution: {solution}"
        )

    if optimization:

        parts.append(
            f"Optimization: {optimization}"
        )

    return "\n\n".join(
        part
        for part in parts
        if part.strip()
    )