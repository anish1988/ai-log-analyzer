"""
Phase 3.4 - Existing Error Analysis Workflow Adapter.

This module connects the standalone Phase 3 automation pipeline
to the existing AI analysis workflow.

IMPORTANT:
    Do NOT duplicate RAG or LLM logic here.

The existing LangGraph workflow remains the single source of truth
for:

    Error preparation
        ↓
    Embedding generation
        ↓
    RAG retrieval
        ↓
    RAG decision
        ↓
    Historical solution reuse
        OR
    Log-type specific LLM analysis
        ↓
    Final AI result
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


from app.ai.graph.workflow import (
    build_ai_analysis_graph,
)

from app.repositories.analysis_history_repository import (
    create_analysis_result,
    create_analysis_run,
    mark_analysis_run_completed,
    mark_analysis_run_failed,
)

SYSTEM_USER_ID = "27102c37-77e9-4b9d-8bd4-eeec02fb72bc"

class ErrorAnalysisRunner:
    """
    Adapter between Phase 3 automation and the existing
    LangGraph AI analysis workflow.

    This class does NOT implement:
        - embeddings
        - RAG
        - RAG decision
        - LLM calls
        - analyzers

    All of those remain inside the existing AI workflow.
    """

    def __init__(self) -> None:
        self.graph = build_ai_analysis_graph()

    async def analyze(
        self,
        *,
        errors: list[dict[str, Any]],
        request_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Send parsed errors to the existing LangGraph workflow.

        Parameters
        ----------
        errors:
            Parsed errors produced by the existing parser.

        request_id:
            Optional automation request/run identifier.

        Returns
        -------
        dict:
            Final LangGraph state.
        """

        resolved_request_id = (
            request_id
            or f"AUTO-AI-{uuid4()}"
        )
        # ---------------------------------------------------------
        # CREATE ANALYSIS HISTORY RUN
        #
        # Automation analyses are owned by the fixed system user.
        # ---------------------------------------------------------

        analysis_run_id = create_analysis_run(
            request_id=resolved_request_id,
            user_id=SYSTEM_USER_ID,
            source_type="automation",
            status="processing",
            total_errors=len(errors),
            log_type=(
                errors[0].get("log_type")
                if errors
                else None
            ),
            servers=sorted(
                {
                    error.get("server")
                    for error in errors
                    if error.get("server")
                }
            ),
            log_files=sorted(
                {
                    error.get("file_name")
                    for error in errors
                    if error.get("file_name")
                }
            ),
            custom_prompt=None,
            automation_run_id=resolved_request_id,
            metadata={
                "source": "phase_3_automation",
            },
        )

        if not errors:
            mark_analysis_run_completed(
                analysis_run_id=analysis_run_id,
                completed_errors=0,
                failed_errors=0,
            )

            return {
                "request_id": resolved_request_id,
                "analysis_run_id": str(
                    analysis_run_id
                ),
                "selected_errors": [],
                "final_results": [],
                "status": "completed",
                "progress": 100,
                "error": None,
            }

        print("=" * 100)
        print("PHASE 3.4 - ERROR ANALYSIS RUNNER")
        print("=" * 100)

        print(
            f"Request ID    : "
            f"{resolved_request_id}"
        )

        print(
            f"Selected Errors : "
            f"{len(errors)}"
        )

        print("=" * 100)

        # ---------------------------------------------------------
        # Build the exact state expected by the existing LangGraph.
        #
        # This is the same state shape currently constructed by
        # app/api/ai_analysis.py.
        # ---------------------------------------------------------

        initial_state = {
            "request_id": resolved_request_id,

            "selected_errors": errors,

            "current_error_index": 0,

            "current_error": None,

            "final_results": [],

            "progress_events": [],

            "messages": [],

            "status": "processing",

            "progress": 0,

            "error": None,
        }

        # ---------------------------------------------------------
        # EXISTING LANGGRAPH
        #
        # No duplicated RAG / LLM implementation.
        # ---------------------------------------------------------

        print(
            "Starting existing LangGraph..."
        )

        try:
            result = await self.graph.ainvoke(
                initial_state
            )

            # ---------------------------------------------------------
            # PERSIST ANALYSIS RESULTS
            #
            # Store one history record for each AI-analyzed error.
            # ---------------------------------------------------------

            final_results = result.get(
                "final_results",
                [],
            )

            for raw_result in final_results:
                timestamp_value = raw_result.get(
                    "timestamp"
                )

                timestamp = (
                    datetime.fromisoformat(
                        timestamp_value.replace(
                            "Z",
                            "+00:00",
                        )
                    )
                    if timestamp_value
                    else None
                )

                create_analysis_result(
                    analysis_run_id=analysis_run_id,
                    error_id=raw_result.get(
                        "error_id"
                    ),
                    error_signature=raw_result.get(
                        "error_summary"
                    ),
                    tier=raw_result.get("tier"),
                    log_type=raw_result.get(
                        "log_type"
                    ),
                    server=raw_result.get(
                        "server"
                    ),
                    file_name=raw_result.get(
                        "file_name"
                    ),
                    file_path=raw_result.get(
                        "file_path"
                    ),
                    title=raw_result.get("title"),
                    severity=raw_result.get(
                        "severity"
                    ),
                    timestamp=timestamp,
                    start_line=raw_result.get(
                        "start_line"
                    ),
                    end_line=raw_result.get(
                        "end_line"
                    ),
                    source=raw_result.get(
                        "source"
                    ),
                    rag_match=raw_result.get(
                        "rag_match",
                        False,
                    ),
                    rag_knowledge_id=raw_result.get(
                        "rag_knowledge_id"
                    ),
                    rag_similarity=raw_result.get(
                        "rag_similarity"
                    ),
                    confidence=raw_result.get(
                        "confidence"
                    ),
                    analysis_status=raw_result.get(
                        "status"
                    ),
                    error_summary=raw_result.get(
                        "error_summary"
                    ),
                    root_cause=raw_result.get(
                        "root_cause"
                    ),
                    solution=raw_result.get(
                        "solution"
                    ),
                    optimization=raw_result.get(
                        "optimization"
                    ),
                    source_code_analysis=raw_result.get(
                        "source_code_analysis"
                    ),
                    source_file=raw_result.get(
                        "source_file"
                    ),
                    source_line_number=raw_result.get(
                        "source_line_number"
                    ),
                    jira_description=raw_result.get(
                        "jira_description"
                    ),
                    root_cause_evidence=raw_result.get(
                        "root_cause_evidence"
                    ),
                    test_result=raw_result.get(
                        "test_result"
                    ),
                    evidence=raw_result.get(
                        "evidence"
                    ),
                    source_code_location=raw_result.get(
                        "source_code_location",
                        {},
                    ),
                    missing_information=raw_result.get(
                        "missing_information",
                        [],
                    ),
                    request_payload={
                        "request_id": resolved_request_id,
                        "selected_errors": errors,
                    },
                    response_payload=raw_result,
                )

            mark_analysis_run_completed(
                analysis_run_id=analysis_run_id,
                completed_errors=len(final_results),
                failed_errors=(
                    len(errors) - len(final_results)
                ),
            )
            result["analysis_run_id"] = str(
                analysis_run_id
            )

        except Exception as exc:
            mark_analysis_run_failed(
                analysis_run_id=analysis_run_id,
                error_message=str(exc),
                completed_errors=0,
                failed_errors=len(errors),
            )

            raise

        # ---------------------------------------------------------
        # LANGGRAPH / PERSISTENCE COMPLETED

        # ---------------------------------------------------------
        # PERSIST ANALYSIS RESULTS
        #
        # Store one history record for each AI-analyzed error.
        # ---------------------------------------------------------



        print("=" * 100)
        print("PHASE 3.4 - LANGGRAPH COMPLETED")
        print("=" * 100)

        print(
            f"Request ID     : "
            f"{resolved_request_id}"
        )

        print(
            f"Final Results  : "
            f"{len(result.get('final_results', []))}"
        )

        print(
            f"Status         : "
            f"{result.get('status')}"
        )

        print("=" * 100)

        return result