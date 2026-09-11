"""
AI Analysis API.

This endpoint receives selected errors from the frontend
and executes the LangGraph AI analysis workflow.
"""

from uuid import UUID, uuid4
from datetime import datetime

from app.schemas.ai_analysis import (
    AIAnalysisRequest,
    AIAnalysisResponse,
    AIAnalysisResultResponse,
    AIProgressEventResponse,
)

from app.repositories.analysis_history_repository import (
    create_analysis_run,
    create_analysis_result,
    get_analysis_results,
    mark_analysis_run_completed,
    mark_analysis_run_failed,
    update_analysis_result_jira,
)

from app.ai.graph.workflow import (
    build_ai_analysis_graph,
)

import asyncio
import json

from fastapi import (
    APIRouter,
    HTTPException,
    Request,
)

from fastapi.responses import (
    StreamingResponse,
)

from app.ai.graph.progress import (
    get_progress_publisher,
)

from app.schemas.ai_analysis import (
    AIKnowledgeVerificationRequest,
    JiraTicketCreateRequest,
    JiraTicketCreateResponse,
)
from app.integrations.jira.service import (
    JiraService,
)


DEVELOPMENT_USER_ID = "033e0e0b-528f-44c4-956f-ff48fff628c0"

router = APIRouter(
    prefix="/api/ai",
    tags=["AI Analysis"],
)

# =============================================================================
# AI ANALYSIS PROGRESS STREAM
# =============================================================================


@router.get(
    "/progress/{request_id}",
)
async def stream_analysis_progress(
    request_id: str,
    request: Request,
):
    """
    Stream real-time AI analysis progress using
    Server-Sent Events (SSE).

    The client subscribes using the same request_id
    supplied to POST /api/ai/analyze.
    """

    print("=" * 100)
    print("AI PROGRESS STREAM CONNECTED")
    print("=" * 100)

    print(
        f"Request ID : {request_id}"
    )

    publisher = get_progress_publisher()

    queue = await publisher.subscribe(
        request_id
    )

    async def event_generator():

        try:

            # -------------------------------------------------------------
            # Initial connection event
            # -------------------------------------------------------------

            connected_event = {
                "type": "connected",
                "request_id": request_id,
                "message": (
                    "AI progress stream connected."
                ),
            }

            yield (
                "event: connected\n"
                f"data: {json.dumps(connected_event)}\n\n"
            )

            # -------------------------------------------------------------
            # Stream progress events
            # -------------------------------------------------------------

            while True:

                # Stop if browser disconnected.
                if await request.is_disconnected():

                    print(
                        "AI progress client disconnected:"
                        f" {request_id}"
                    )

                    break

                try:

                    event = await asyncio.wait_for(
                        queue.get(),
                        timeout=15.0,
                    )

                except asyncio.TimeoutError:

                    # -----------------------------------------------------
                    # SSE heartbeat
                    #
                    # Keeps proxies/browser connections alive while an
                    # LLM operation is taking longer to produce an event.
                    # -----------------------------------------------------

                    yield (
                        ": heartbeat\n\n"
                    )

                    continue

                event_data = event.model_dump(
                    mode="json"
                )

                yield (
                    "event: progress\n"
                    f"data: {json.dumps(event_data)}\n\n"
                )

                # ---------------------------------------------------------
                # Request completed
                # ---------------------------------------------------------

                if (
                    event.task_id
                    == "finalize_analysis"
                    and event.status.value
                    == "completed"
                    and event.progress
                    == 100
                ):

                    completed_event = {
                        "type": "completed",
                        "request_id": request_id,
                    }

                    yield (
                        "event: completed\n"
                        f"data: {json.dumps(completed_event)}\n\n"
                    )

                    break

        except asyncio.CancelledError:

            print(
                "AI progress stream cancelled:"
                f" {request_id}"
            )

            raise

        finally:

            await publisher.unsubscribe(
                request_id,
                queue,
            )

            print("=" * 100)
            print("AI PROGRESS STREAM CLOSED")
            print("=" * 100)

            print(
                f"Request ID : {request_id}"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
# =============================================================================
# AI ANALYSIS
# =============================================================================


@router.post(
    "/analyze",
    response_model=AIAnalysisResponse,
)
async def analyze_errors(
    request: AIAnalysisRequest,
) -> AIAnalysisResponse:

    print("=" * 100)
    print("AI ANALYSIS REQUEST")
    print("=" * 100)

    # -------------------------------------------------------------------------
    # REQUEST ID
    # -------------------------------------------------------------------------

    request_id = (
        request.request_id
        or f"AI-{uuid4()}"
    )

    # -------------------------------------------------------------------------
    # SELECTED ERRORS
    # -------------------------------------------------------------------------

    selected_errors = [
        error.model_dump()
        for error in request.selected_errors
    ]

    custom_prompt = request.custom_prompt

    print(
        f"Request ID   : {request_id}"
    )

    print(
        f"Total Errors : {len(selected_errors)}"
    )

    print(
        "Selected Error IDs:"
    )

    for error in selected_errors:

        print(
            f" - {error.get('error_id')}"
        )

    # -------------------------------------------------------------------------
    # VALIDATION
    # -------------------------------------------------------------------------

    if not selected_errors:

        raise HTTPException(
            status_code=400,
            detail=(
                "At least one error is required "
                "for AI analysis."
            ),
        )

    try:

        # ---------------------------------------------------------------------
        # BUILD GRAPH
        # ---------------------------------------------------------------------

        graph = build_ai_analysis_graph()

        # ---------------------------------------------------------------------
        # INITIAL STATE
        # ---------------------------------------------------------------------

        initial_state = {

            "request_id": request_id,

            "selected_errors": selected_errors,

            "custom_prompt": custom_prompt,

            "current_error_index": 0,

            "current_error": None,

            "final_results": [],

            "progress_events": [],

            "messages": [],

            "status": "processing",

            "progress": 0,

            "error": None,
        }

        # ---------------------------------------------------------------------
        # CREATE ANALYSIS HISTORY RUN
        # ---------------------------------------------------------------------

        analysis_run_id = create_analysis_run(
            request_id=request_id,
            user_id=DEVELOPMENT_USER_ID,
            source_type="manual",
            status="processing",
            total_errors=len(selected_errors),
            log_type=(
                selected_errors[0].get("log_type")
                if selected_errors
                else None
            ),
            servers=list(
                {
                    error.get("server")
                    for error in selected_errors
                    if error.get("server")
                }
            ),
            log_files=list(
                {
                    error.get("file_name")
                    for error in selected_errors
                    if error.get("file_name")
                }
            ),
            custom_prompt=custom_prompt,
            metadata=request.metadata,
        )

        # ---------------------------------------------------------------------
        # RUN LANGGRAPH
        # ---------------------------------------------------------------------

        result = await graph.ainvoke(
            initial_state
        )

        # ---------------------------------------------------------------------
        # FINAL RESULTS
        # ---------------------------------------------------------------------

        final_results = result.get(
            "final_results",
            [],
        )

        # ---------------------------------------------------------------------
        # PROGRESS EVENTS
        # ---------------------------------------------------------------------

        progress_events = result.get(
            "progress_events",
            [],
        )

        # ---------------------------------------------------------------------
        # CONVERT RESULT MODELS
        # ---------------------------------------------------------------------

        result_models = [
            AIAnalysisResultResponse.model_validate(
                item
            )
            for item in final_results
        ]

                # ---------------------------------------------------------------------
        # PERSIST ANALYSIS RESULTS
        # ---------------------------------------------------------------------

        for result_model, raw_result in zip(
            result_models,
            final_results,
        ):
            create_analysis_result(
                analysis_run_id=analysis_run_id,
                error_id=result_model.error_id,
                error_signature=(
                    result_model.error_summary
                ),
                tier=result_model.tier,
                log_type=result_model.log_type,
                server=result_model.server,
                file_name=result_model.file_name,
                file_path=(
                    next(
                        (
                            error.get("file_path")
                            for error in selected_errors
                            if error.get("error_id")
                            == result_model.error_id
                        ),
                        None,
                    )
                ),
                title=result_model.title,
                severity=result_model.severity,
                timestamp=(
                    datetime.fromisoformat(
                        result_model.timestamp.replace(
                            "Z",
                            "+00:00",
                        )
                    )
                    if result_model.timestamp
                    else None
                ),
                start_line=result_model.start_line,
                end_line=result_model.end_line,
                source=result_model.source,
                rag_match=result_model.rag_match,
                rag_knowledge_id=result_model.rag_knowledge_id,
                rag_similarity=result_model.rag_similarity,
                confidence=result_model.confidence,
                analysis_status=result_model.status,
                error_summary=result_model.error_summary,
                root_cause=result_model.root_cause,
                solution=result_model.solution,
                optimization=result_model.optimization,
                source_code_analysis=(
                    result_model.source_code_analysis
                ),
                source_file=result_model.source_file,
                source_line_number=(
                    result_model.source_line_number
                ),
                jira_description=result_model.jira_description,
                root_cause_evidence=(
                    result_model.root_cause_evidence
                ),
                test_result=result_model.test_result,
                evidence=result_model.evidence,
                source_code_location=(
                    raw_result.get(
                        "source_code_location",
                        {},
                    )
                ),
                missing_information=(
                    raw_result.get(
                        "missing_information",
                        [],
                    )
                ),
             #   request_payload={
             #       "request_id": request_id,
             #      "selected_error": next(
             #           (
             #               error
             #               for error in selected_errors
             #               if error.get("error_id")
             #               == result_model.error_id
             #           ),
             #          {},
             #       ),
             #      "custom_prompt": custom_prompt,
             #   },
                request_payload=request.model_dump(),
                response_payload=raw_result,
            )

        progress_event_models = [
            AIProgressEventResponse(
                task_id=event.task_id,
                status=(
                    event.status.value
                    if hasattr(
                        event.status,
                        "value",
                    )
                    else str(
                        event.status
                    )
                ),
                progress=event.progress,
                message=event.message,
            )
            for event in progress_events
        ]

        # ---------------------------------------------------------------------
        # COMPLETED ERRORS
        # ---------------------------------------------------------------------

        completed_errors = len(
            result_models
        )

        # ---------------------------------------------------------------------
        # MARK ANALYSIS RUN COMPLETED
        # ---------------------------------------------------------------------

        mark_analysis_run_completed(
            analysis_run_id=analysis_run_id,
            completed_errors=completed_errors,
            failed_errors=(
                len(selected_errors)
                - completed_errors
            ),
        )

        # ---------------------------------------------------------------------
        # FINAL STATUS
        # ---------------------------------------------------------------------

        final_status = result.get(
            "status",
            "completed",
        )

        if final_status not in {
            "processing",
            "completed",
            "error",
        }:

            final_status = "completed"

        # ---------------------------------------------------------------------
        # RESPONSE
        # ---------------------------------------------------------------------

        response = AIAnalysisResponse(

            request_id=request_id,

            analysis_run_id=str(
                analysis_run_id
            ),    

            status=final_status,

            current_task=result.get(
                "current_task",
                "",
            ),

            progress=result.get(
                "progress",
                100,
            ),

            total_errors=len(
                selected_errors
            ),

            completed_errors=completed_errors,

            final_results=result_models,

            progress_events=(
                progress_event_models
            ),

            messages=result.get(
                "messages",
                [],
            ),

            error=result.get(
                "error"
            ),
        )

        print("=" * 100)
        print("AI ANALYSIS REQUEST COMPLETED")
        print("=" * 100)

        print(
            f"Request ID     : {request_id}"
        )

        print(
            f"Total Errors   : "
            f"{len(selected_errors)}"
        )

        print(
            f"Final Results  : "
            f"{len(result_models)}"
        )

        print(
            f"Final Progress : "
            f"{response.progress}%"
        )

        print(
            f"Final Status   : "
            f"{response.status}"
        )

        print("=" * 100)

        return response

    except HTTPException:

        raise

    except Exception as exc:

        print("=" * 100)
        print("AI ANALYSIS ERROR")
        print("=" * 100)

        print(
            repr(exc)
        )

        print("=" * 100)

        # ---------------------------------------------------------------------
        # MARK ANALYSIS RUN FAILED
        # ---------------------------------------------------------------------

        if "analysis_run_id" in locals():
            try:
                mark_analysis_run_failed(
                    analysis_run_id=analysis_run_id,
                    error_message=str(exc),
                    completed_errors=0,
                    failed_errors=len(selected_errors),
                )
            except Exception as persistence_exc:
                print(
                    "Failed to update analysis history run: "
                    f"{persistence_exc!r}"
                )

        raise HTTPException(
            status_code=500,
            detail="AI analysis failed.",
        ) from exc


# =============================================================================
# VERIFY RAG KNOWLEDGE
# =============================================================================

@router.patch(
    "/knowledge/{knowledge_id}/verify",
)
async def verify_knowledge(
    knowledge_id: int,
    request: AIKnowledgeVerificationRequest,
):
    """
    Mark an AI analysis result as verified/resolved.

    This does NOT trigger LLM analysis.
    It only updates the existing RAG knowledge record.
    """

    import os

    import psycopg

    host = os.getenv(
        "POSTGRES_HOST",
        "postgres",
    )

    port = int(
        os.getenv(
            "POSTGRES_PORT",
            "5432",
        )
    )

    database = os.getenv(
        "POSTGRES_DB",
        "ai_log_analyzer",
    )

    user = os.getenv(
        "POSTGRES_USER",
        "postgres",
    )

    password = os.getenv(
        "POSTGRES_PASSWORD",
        "postgres",
    )

    try:

        connection = await psycopg.AsyncConnection.connect(
            host=host,
            port=port,
            dbname=database,
            user=user,
            password=password,
        )

        try:

            async with connection.cursor() as cursor:

                await cursor.execute(
                    """
                    UPDATE ai_knowledge_items
                    SET
                        verified = %(verified)s,
                        resolution_status = %(resolution_status)s,
                        verification_notes = %(verification_notes)s,
                        updated_at = NOW()
                    WHERE id = %(knowledge_id)s
                    RETURNING
                        id,
                        verified,
                        resolution_status,
                        verification_notes,
                        updated_at
                    """,
                    {
                        "knowledge_id": knowledge_id,

                        "verified": request.verified,

                        "resolution_status": (
                            request.resolution_status
                        ),

                        "verification_notes": (
                            request.verification_notes
                        ),
                    },
                )

                row = await cursor.fetchone()

                if row is None:

                    raise HTTPException(
                        status_code=404,
                        detail=(
                            f"Knowledge ID "
                            f"{knowledge_id} not found."
                        ),
                    )

                await connection.commit()

                return {
                    "success": True,
                    "knowledge_id": row[0],
                    "verified": row[1],
                    "resolution_status": row[2],
                    "verification_notes": row[3],
                    "updated_at": row[4],
                }

        finally:

            await connection.close()

    except HTTPException:

        raise

    except Exception as exc:

        print("=" * 100)
        print("RAG KNOWLEDGE VERIFICATION ERROR")
        print("=" * 100)

        print(
            repr(exc)
        )

        print("=" * 100)

        raise HTTPException(
            status_code=500,
            detail="Failed to verify RAG knowledge.",
        ) from exc



# =============================================================================
# JIRA TICKET
# =============================================================================


@router.post(
    "/jira/ticket",
    response_model=JiraTicketCreateResponse,
)
async def create_jira_ticket(
    request: JiraTicketCreateRequest,
):
    """
    Create one Jira ticket for one AI analysis result.

    Important:
        This endpoint intentionally processes only one error.

        It does NOT accept:
            - selected_errors
            - final_results
            - multiple analysis results

        Therefore one frontend Jira button creates one Jira ticket.
    """

    analysis = request.analysis
    analysis_run_id = request.analysis_run_id

    error_id = (
        analysis.error_id
        or ""
    ).strip()

    if not error_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "Cannot create Jira ticket: "
                "error_id is missing."
            ),
        )
    try:
        analysis_results = get_analysis_results(
            analysis_run_id=UUID(analysis_run_id),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid analysis_run_id.",
        ) from exc

    persisted_result = next(
        (
            result
            for result in analysis_results
            if result.get("error_id") == error_id
        ),
        None,
    )

    if persisted_result is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Analysis result was not found "
                "for the supplied analysis_run_id "
                "and error_id."
            ),
        )

    try:

        jira_service = JiraService()

        jira_result = (
            await jira_service.create_ticket(
                analysis=analysis.model_dump()
            )
        )

        issue_key = (
            jira_result.get(
                "key",
                "",
            )
            or ""
        )

        issue_id = (
            jira_result.get(
                "id",
                "",
            )
            or ""
        )

        if not issue_key:

            raise RuntimeError(
                "Jira created the issue but "
                "did not return an issue key."
            )

        # ---------------------------------------------------------------------
        # Jira browse URL
        # ---------------------------------------------------------------------

        jira_base_url = (
            jira_service.client.base_url
            .rstrip("/")
        )

        issue_url = (
            f"{jira_base_url}/browse/"
            f"{issue_key}"
        )

        # ---------------------------------------------------------------------
        # UPDATE ANALYSIS HISTORY WITH JIRA DETAILS
        # ---------------------------------------------------------------------
        try:
            jira_updated = update_analysis_result_jira(
                result_id=persisted_result["id"],
                jira_issue_key=issue_key,
                jira_issue_id=issue_id,
                jira_issue_url=issue_url,
                jira_status=jira_result.get("status"),
                jira_payload=jira_result,
            )

            if not jira_updated:
                print(
                    "Analysis history Jira update skipped: "
                    f"result_id={persisted_result['id']}"
                )

        except Exception as persistence_exc:
            print(
                "Failed to update analysis history with Jira details: "
                f"{persistence_exc!r}"
            )

        print("=" * 100)
        print("JIRA TICKET CREATED")
        print("=" * 100)

        print(
            f"Error ID   : {error_id}"
        )

        print(
            f"Issue Key  : {issue_key}"
        )

        print(
            f"Issue ID   : {issue_id}"
        )

        print(
            f"Issue URL  : {issue_url}"
        )

        print("=" * 100)

        return JiraTicketCreateResponse(
            success=True,
            error_id=error_id,
            issue_key=issue_key,
            issue_id=issue_id,
            issue_url=issue_url,
            message=(
                "Jira ticket created successfully."
            ),
        )

    except HTTPException:

        raise

    except Exception as exc:

        print("=" * 100)
        print("JIRA TICKET CREATION FAILED")
        print("=" * 100)

        print(
            f"Error ID : {error_id}"
        )

        print(
            repr(exc)
        )

        print("=" * 100)

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to create Jira ticket: "
                f"{str(exc)}"
            ),
        ) from exc