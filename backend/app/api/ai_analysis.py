"""
AI Analysis API.

This endpoint receives selected errors from the frontend
and executes the LangGraph AI analysis workflow.
"""

from uuid import uuid4

from app.schemas.ai_analysis import (
    AIAnalysisRequest,
    AIAnalysisResponse,
    AIAnalysisResultResponse,
    AIProgressEventResponse,
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
)


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