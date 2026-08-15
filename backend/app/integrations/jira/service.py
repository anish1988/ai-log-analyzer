"""
Jira service layer.

Responsible for converting one AI analysis result into a Jira issue.

Important:
    This service handles ONE error at a time.

    One AIAnalysisResult
        ->
    One Jira issue
"""

from typing import Any

from app.integrations.jira.client import JiraClient


class JiraService:
    """
    Application-level Jira integration service.
    """

    def __init__(
        self,
        client: JiraClient | None = None,
    ) -> None:

        self.client = client or JiraClient()

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    async def create_ticket(
        self,
        analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Create one Jira ticket from one AI analysis result.

        Parameters
        ----------
        analysis:
            One AIAnalysisResult dictionary.

        Returns
        -------
        dict[str, Any]
            Jira create-issue response.
        """

        self._validate_analysis(
            analysis
        )

        summary = self._build_summary(
            analysis
        )

        description = self._build_description(
            analysis
        )

        print("=" * 100)
        print("JIRA SERVICE")
        print("=" * 100)

        print(
            f"Error ID : "
            f"{analysis.get('error_id', '')}"
        )

        print(
            f"Summary  : "
            f"{summary}"
        )

        print(
            f"Project  : "
            f"{self.client.project_key}"
        )

        print(
            f"Issue Type : "
            f"{self.client.issue_type}"
        )

        print("=" * 100)

        result = await self.client.create_issue(
            summary=summary,
            description=description,
        )

        print(
            f"Jira Issue Key : "
            f"{result.get('key', '')}"
        )

        print(
            f"Jira Issue ID  : "
            f"{result.get('id', '')}"
        )

        print("=" * 100)

        return result

    # =========================================================================
    # VALIDATION
    # =========================================================================

    @staticmethod
    def _validate_analysis(
        analysis: dict[str, Any],
    ) -> None:
        """
        Validate the minimum information required
        to create a Jira ticket.
        """

        if not isinstance(
            analysis,
            dict,
        ):
            raise ValueError(
                "Jira analysis must be a dictionary."
            )

        error_id = (
            analysis.get(
                "error_id",
                "",
            )
            or ""
        ).strip()

        if not error_id:

            raise ValueError(
                "Cannot create Jira ticket: "
                "error_id is missing."
            )

    # =========================================================================
    # SUMMARY
    # =========================================================================

    @staticmethod
    def _build_summary(
        analysis: dict[str, Any],
    ) -> str:
        """
        Build Jira issue summary.

        Example:
            [ERR-00002] Apache Error - AH00163
        """

        error_id = (
            analysis.get(
                "error_id",
                "",
            )
            or ""
        ).strip()

        title = (
            analysis.get(
                "title",
                "",
            )
            or ""
        ).strip()

        log_type = (
            analysis.get(
                "log_type",
                "",
            )
            or ""
        ).strip()

        if title:

            summary = (
                f"[{error_id}] "
                f"{title}"
            )

        elif log_type:

            summary = (
                f"[{error_id}] "
                f"{log_type} error"
            )

        else:

            summary = (
                f"[{error_id}] "
                "AI Log Analysis"
            )

        # Jira summary has a practical size limit.
        return summary[:255]

    # =========================================================================
    # ADF DESCRIPTION
    # =========================================================================

    @classmethod
    def _build_description(
        cls,
        analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build Jira Atlassian Document Format (ADF).

        The description intentionally contains the analysis
        section-by-section rather than only copying
        jira_description.
        """

        content: list[dict[str, Any]] = []

        # ---------------------------------------------------------------------
        # TITLE
        # ---------------------------------------------------------------------

        cls._add_heading(
            content,
            "AI Log Analysis",
            level=2,
        )

        # ---------------------------------------------------------------------
        # ERROR INFORMATION
        # ---------------------------------------------------------------------

        cls._add_heading(
            content,
            "Error Information",
            level=3,
        )

        cls._add_field(
            content,
            "Error ID",
            analysis.get(
                "error_id",
                "",
            ),
        )

        cls._add_field(
            content,
            "Tier",
            analysis.get(
                "tier",
                "",
            ),
        )

        cls._add_field(
            content,
            "Log Type",
            analysis.get(
                "log_type",
                "",
            ),
        )

        cls._add_field(
            content,
            "Server",
            analysis.get(
                "server",
                "",
            ),
        )

        cls._add_field(
            content,
            "File",
            analysis.get(
                "file_name",
                "",
            ),
        )

        cls._add_field(
            content,
            "Severity",
            analysis.get(
                "severity",
                "",
            ),
        )

        cls._add_field(
            content,
            "Timestamp",
            analysis.get(
                "timestamp",
                "",
            ),
        )

        cls._add_field(
            content,
            "Error Signature",
            analysis.get(
                "error_signature",
                "",
            ),
        )

        # ---------------------------------------------------------------------
        # ROOT CAUSE
        # ---------------------------------------------------------------------

        cls._add_heading(
            content,
            "Root Cause",
            level=3,
        )

        cls._add_text_section(
            content,
            analysis.get(
                "root_cause",
                "",
            ),
        )

        # ---------------------------------------------------------------------
        # ROOT CAUSE EVIDENCE
        # ---------------------------------------------------------------------

        cls._add_heading(
            content,
            "Root Cause Evidence",
            level=3,
        )

        cls._add_evidence_list(
            content,
            analysis.get(
                "root_cause_evidence",
                [],
            ),
        )

        # ---------------------------------------------------------------------
        # SOLUTION
        # ---------------------------------------------------------------------

        cls._add_heading(
            content,
            "Solution",
            level=3,
        )

        cls._add_text_section(
            content,
            analysis.get(
                "solution",
                "",
            ),
        )

        # ---------------------------------------------------------------------
        # OPTIMIZATION
        # ---------------------------------------------------------------------

        cls._add_heading(
            content,
            "Optimization",
            level=3,
        )

        cls._add_text_section(
            content,
            analysis.get(
                "optimization",
                "",
            ),
        )

        # ---------------------------------------------------------------------
        # SOURCE CODE ANALYSIS
        # ---------------------------------------------------------------------

        cls._add_heading(
            content,
            "Source Code Analysis",
            level=3,
        )

        cls._add_text_section(
            content,
            analysis.get(
                "source_code_analysis",
                "",
            ),
        )

        cls._add_field(
            content,
            "Source File",
            analysis.get(
                "source_file",
                "",
            ),
        )

        source_line = analysis.get(
            "source_line_number"
        )

        if source_line is not None:

            cls._add_field(
                content,
                "Source Line",
                source_line,
            )

        # ---------------------------------------------------------------------
        # TEST RESULT
        # ---------------------------------------------------------------------

        cls._add_heading(
            content,
            "Test Result",
            level=3,
        )

        cls._add_test_result(
            content,
            analysis.get(
                "test_result",
                {},
            ),
        )

        # ---------------------------------------------------------------------
        # JIRA DESCRIPTION
        # ---------------------------------------------------------------------

        cls._add_heading(
            content,
            "Jira Description",
            level=3,
        )

        cls._add_text_section(
            content,
            analysis.get(
                "jira_description",
                "",
            ),
        )

        # ---------------------------------------------------------------------
        # RAG / HISTORICAL KNOWLEDGE
        # ---------------------------------------------------------------------

        cls._add_heading(
            content,
            "RAG / Historical Knowledge",
            level=3,
        )

        cls._add_field(
            content,
            "Historical Match",
            (
                "Yes"
                if analysis.get(
                    "rag_match",
                    False,
                )
                else "No"
            ),
        )

        cls._add_field(
            content,
            "Knowledge ID",
            analysis.get(
                "rag_knowledge_id"
            ),
        )

        similarity = analysis.get(
            "rag_similarity"
        )

        if similarity is not None:

            cls._add_field(
                content,
                "Similarity",
                similarity,
            )

        cls._add_field(
            content,
            "Confidence",
            analysis.get(
                "confidence",
                "",
            ),
        )

        # ---------------------------------------------------------------------
        # EVIDENCE
        # ---------------------------------------------------------------------

        cls._add_heading(
            content,
            "Evidence",
            level=3,
        )

        cls._add_evidence_list(
            content,
            analysis.get(
                "evidence",
                [],
            ),
        )

        # ---------------------------------------------------------------------
        # STATUS
        # ---------------------------------------------------------------------

        cls._add_heading(
            content,
            "Analysis Status",
            level=3,
        )

        cls._add_field(
            content,
            "Status",
            analysis.get(
                "status",
                "",
            ),
        )

        return {
            "type": "doc",
            "version": 1,
            "content": content,
        }

    # =========================================================================
    # ADF HELPERS
    # =========================================================================

    @staticmethod
    def _add_heading(
        content: list[dict[str, Any]],
        text: str,
        *,
        level: int,
    ) -> None:
        """
        Add an ADF heading.
        """

        content.append(
            {
                "type": "heading",
                "attrs": {
                    "level": level,
                },
                "content": [
                    {
                        "type": "text",
                        "text": str(text),
                    }
                ],
            }
        )

    @staticmethod
    def _add_paragraph(
        content: list[dict[str, Any]],
        text: Any,
    ) -> None:
        """
        Add an ADF paragraph.
        """

        value = str(
            text
            if text is not None
            else ""
        ).strip()

        if not value:
            return

        content.append(
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": value,
                    }
                ],
            }
        )

    @classmethod
    def _add_text_section(
        cls,
        content: list[dict[str, Any]],
        value: Any,
    ) -> None:
        """
        Add potentially multiline text.

        Each non-empty line becomes its own Jira paragraph.
        """

        if value is None:
            return

        text = str(value).strip()

        if not text:
            return

        lines = text.splitlines()

        for line in lines:

            line = line.strip()

            if line:

                cls._add_paragraph(
                    content,
                    line,
                )

    @staticmethod
    def _add_field(
        content: list[dict[str, Any]],
        label: str,
        value: Any,
    ) -> None:
        """
        Add a labelled Jira paragraph.
        """

        if value is None:
            return

        value_text = str(
            value
        ).strip()

        if not value_text:
            return

        content.append(
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": f"{label}: ",
                        "marks": [
                            {
                                "type": "strong",
                            }
                        ],
                    },
                    {
                        "type": "text",
                        "text": value_text,
                    },
                ],
            }
        )

    @classmethod
    def _add_evidence_list(
        cls,
        content: list[dict[str, Any]],
        evidence: Any,
    ) -> None:
        """
        Add evidence as an ADF bullet list.

        Supports:
            - list[str]
            - list[dict]
            - dict
        """

        if not evidence:
            return

        items: list[str] = []

        if isinstance(
            evidence,
            list,
        ):

            for item in evidence:

                if isinstance(
                    item,
                    dict,
                ):

                    parts = []

                    for key, value in item.items():

                        if value is None:
                            continue

                        value_text = str(
                            value
                        ).strip()

                        if value_text:

                            parts.append(
                                f"{key}: "
                                f"{value_text}"
                            )

                    if parts:
                        items.append(
                            " | ".join(parts)
                        )

                else:

                    value = str(
                        item
                    ).strip()

                    if value:
                        items.append(
                            value
                        )

        elif isinstance(
            evidence,
            dict,
        ):

            for key, value in evidence.items():

                if value is None:
                    continue

                value_text = str(
                    value
                ).strip()

                if value_text:

                    items.append(
                        f"{key}: {value_text}"
                    )

        else:

            value = str(
                evidence
            ).strip()

            if value:
                items.append(value)

        if not items:
            return

        list_items = []

        for item in items:

            list_items.append(
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": item,
                                }
                            ],
                        }
                    ],
                }
            )

        content.append(
            {
                "type": "bulletList",
                "content": list_items,
            }
        )

    @classmethod
    def _add_test_result(
        cls,
        content: list[dict[str, Any]],
        test_result: Any,
    ) -> None:
        """
        Add test result information.

        Supports the structured test_result dictionary
        currently used by the AI analysis response.
        """

        if not test_result:
            return

        if isinstance(
            test_result,
            dict,
        ):

            for key, value in test_result.items():

                if value is None:
                    continue

                # Lists such as verification_steps
                # become bullet lists.
                if isinstance(
                    value,
                    list,
                ):

                    cls._add_field(
                        content,
                        key,
                        "",
                    )

                    cls._add_evidence_list(
                        content,
                        value,
                    )

                elif isinstance(
                    value,
                    dict,
                ):

                    cls._add_field(
                        content,
                        key,
                        "",
                    )

                    cls._add_evidence_list(
                        content,
                        value,
                    )

                else:

                    cls._add_field(
                        content,
                        key,
                        value,
                    )

        else:

            cls._add_text_section(
                content,
                test_result,
            )