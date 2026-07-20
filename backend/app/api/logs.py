"""
POST /api/logs/permission
POST /api/logs/fetch

Register in backend/app/main.py with:
    from app.api.logs import router as logs_router
    app.include_router(logs_router, prefix="/api/logs", tags=["logs"])
"""
from fastapi import APIRouter, HTTPException

from app.schemas.log_analysis import (
    LogFetchResponse,
    PermissionCheckRequest,
    PermissionCheckResponse,
    SearchFiltersRequest,
)
from app.services import log_analysis_service, permission_service

router = APIRouter()


@router.post("/permission", response_model=PermissionCheckResponse)
async def check_permission(request: PermissionCheckRequest) -> PermissionCheckResponse:
    return await permission_service.check_permission(request)


@router.post("/fetch", response_model=LogFetchResponse)
async def fetch_logs(request: SearchFiltersRequest) -> LogFetchResponse:
    print("=" * 80)
    print("Request object:")
    print(request)
    print()

    print("Request dict:")
    print(request.model_dump())   # Pydantic v2
    # print(request.dict())       # Pydantic v1

    print("=" * 80)
    try:
        return await log_analysis_service.fetch_logs(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc