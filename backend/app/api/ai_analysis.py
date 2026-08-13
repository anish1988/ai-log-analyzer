"""
AI Analysis API.

This endpoint receives selected errors from the frontend
and executes the LangGraph AI analysis workflow.
"""

from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.schemas.ai_analysis import (
    AIAnalysisRequest,
    AIAnalysisResponse,
    AIAnalysisResultResponse,
    AIProgressEventResponse,
)

from app.ai.graph.workflow import (
    build_ai_analysis_graph,
)


router = APIRouter(
    prefix="/api/ai",
    tags=["AI Analysis"],
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