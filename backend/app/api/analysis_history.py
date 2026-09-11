from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.dependencies import CurrentUser, get_current_user
from app.repositories.analysis_history_repository import (
    get_analysis_results,
    get_analysis_run,
    get_analysis_runs,
)

from app.schemas.analysis_history import (
    AnalysisResultResponse,
    AnalysisRunDetailResponse,
    AnalysisRunListResponse,
    AnalysisRunResponse,
)


router = APIRouter(
    prefix="/api/analysis-history",
    tags=["analysis-history"],
)


@router.get(
    "",
    response_model=AnalysisRunListResponse,
)
async def list_analysis_runs(
    current_user: CurrentUser = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AnalysisRunListResponse:
    """
    Return analysis-history runs belonging to the current user.
    """

    runs = get_analysis_runs(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )

    return AnalysisRunListResponse(
        items=[
            AnalysisRunResponse.model_validate(run)
            for run in runs
        ],
        total=len(runs),
    )


@router.get(
    "/{run_id}",
    response_model=AnalysisRunDetailResponse,
)
async def get_analysis_run_detail(
    run_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
) -> AnalysisRunDetailResponse:
    """
    Return one analysis run and all of its analysis results.

    Ownership is enforced using the current user's ID.
    """

    run = get_analysis_run(
        analysis_run_id=run_id,
        user_id=current_user.id,
    )

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis run was not found.",
        )

    results = get_analysis_results(
        analysis_run_id=run_id,
    )

    return AnalysisRunDetailResponse(
        run=AnalysisRunResponse.model_validate(run),
        results=[
            AnalysisResultResponse.model_validate(result)
            for result in results
        ],
    )