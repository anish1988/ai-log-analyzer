"""
AI Analysis API.

This endpoint receives selected errors from the frontend
and starts the LangGraph AI analysis workflow.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.ai_analysis import (
    AIAnalysisRequest,
    AIAnalysisResponse,
)

# IMPORTANT:
#
# Import the existing Step 3.7 graph builder here.
#
# Use the actual function name from your existing workflow.py.
#
# Example:
#
# from app.ai.graph.workflow import build_analysis_graph
#
# Do not create a second graph.

from app.ai.graph.workflow import (
    build_ai_analysis_graph,
)


router = APIRouter(
    prefix="/api/ai",
    tags=["AI Analysis"],
)


@router.post(
    "/analyze",
    response_model=AIAnalysisResponse,
)
async def analyze_errors(
    request: AIAnalysisRequest,
):

    print("=" * 100)
    print("AI ANALYSIS REQUEST")
    print("=" * 100)

    print(
        f"Tier        : {request.tier}"
    )

    print(
        f"Total Errors: {len(request.errors)}"
    )

    print(
        "Selected Error IDs:"
    )

    for error in request.errors:

        print(
            f" - {error.get('error_id')}"
        )

    if not request.errors:

        raise HTTPException(
            status_code=400,

            detail=(
                "At least one error is required "
                "for AI analysis."
            ),
        )

    try:

        graph = build_ai_analysis_graph()

        final_results = []

        # -----------------------------------------------------
        # Phase 3.10:
        #
        # Run one error at a time.
        #
        # This is intentional.
        #
        # Later LangGraph can orchestrate the complete
        # multi-error workflow.
        # -----------------------------------------------------

        for error in request.errors:

            print("=" * 100)
            print("PROCESSING ERROR")
            print("=" * 100)

            print(
                f"Error ID : "
                f"{error.get('error_id')}"
            )

            initial_state = {

                "selected_errors": [
                    error
                ],

                "current_error": error,

                "tier": request.tier,

                "final_results": [],
            }

            result = await graph.ainvoke(
                initial_state
            )

            error_results = result.get(
                "final_results",
                [],
            )

            final_results.extend(
                error_results
            )

        print("=" * 100)
        print("AI ANALYSIS REQUEST COMPLETED")
        print("=" * 100)

        print(
            f"Final Results: "
            f"{len(final_results)}"
        )

        return AIAnalysisResponse(

            success=True,

            total_errors=len(
                final_results
            ),

            results=final_results,
        )

    except Exception as exc:

        print("=" * 100)
        print("AI ANALYSIS ERROR")
        print("=" * 100)

        print(
            repr(exc)
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "AI analysis failed."
            ),
        ) from exc