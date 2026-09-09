"""
Phase 4 - Saved Search API.

Saved searches are created ONLY when the user explicitly clicks
"Save Search".

Normal searches do not create saved-search records.

Authentication:
    The current user is resolved by get_current_user().

Security:
    user_id is NEVER accepted from the frontend.
    Ownership is enforced by the repository layer.
"""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import (
    CurrentUser,
    get_current_user,
)
from app.repositories.saved_search_repository import (
    create_saved_search,
    delete_saved_search,
    get_saved_search,
    get_user_saved_searches,
    update_saved_search,
)
from app.schemas.saved_search import (
    SavedSearchCreateRequest,
    SavedSearchListResponse,
    SavedSearchResponse,
    SavedSearchUpdateRequest,
)


router = APIRouter(
    prefix="/api/saved-searches",
    tags=["saved-searches"],
)


def _to_response(
    saved_search: dict,
) -> SavedSearchResponse:
    """
    Convert repository data into the public API response schema.
    """

    return SavedSearchResponse(
        id=saved_search["id"],
        user_id=str(saved_search["user_id"]),
        name=saved_search["name"],
        description=saved_search["description"],
        from_=saved_search["from_date"],
        to=saved_search["to_date"],
        tier=saved_search["tier"],
        servers=saved_search["servers"],
        search_filters=saved_search["search_filters"],
        created_at=saved_search["created_at"],
        updated_at=saved_search["updated_at"],
    )


def _validate_dates(
    from_date: date,
    to_date: date,
) -> None:
    """
    Validate saved-search date range.
    """

    if to_date < from_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="End date cannot be before start date.",
        )


@router.post(
    "",
    response_model=SavedSearchResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_saved_search_api(
    request: SavedSearchCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> SavedSearchResponse:
    """
    Create a saved search for the current user.

    This endpoint is called only when the user explicitly chooses
    "Save Search".
    """

    _validate_dates(
        request.from_,
        request.to,
    )

    try:

        saved_search_id = create_saved_search(
            user_id=current_user.id,
            name=request.name,
            description=request.description,
            from_date=request.from_,
            to_date=request.to,
            tier=request.tier,
            servers=request.servers,
            search_filters=request.search_filters,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    saved_search = get_saved_search(
        user_id=current_user.id,
        saved_search_id=saved_search_id,
    )

    if saved_search is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Saved search was created but could not be retrieved.",
        )

    return _to_response(saved_search)


@router.get(
    "",
    response_model=SavedSearchListResponse,
)
async def list_saved_searches(
    current_user: CurrentUser = Depends(get_current_user),
) -> SavedSearchListResponse:
    """
    Return only saved searches belonging to the current user.
    """

    saved_searches = get_user_saved_searches(
        user_id=current_user.id,
    )

    items = [
        _to_response(saved_search)
        for saved_search in saved_searches
    ]

    return SavedSearchListResponse(
        items=items,
        total=len(items),
    )


@router.get(
    "/{saved_search_id}",
    response_model=SavedSearchResponse,
)
async def get_saved_search_api(
    saved_search_id: int,
    current_user: CurrentUser = Depends(get_current_user),
) -> SavedSearchResponse:
    """
    Return one saved search belonging to the current user.
    """

    saved_search = get_saved_search(
        user_id=current_user.id,
        saved_search_id=saved_search_id,
    )

    if saved_search is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved search not found.",
        )

    return _to_response(saved_search)


@router.put(
    "/{saved_search_id}",
    response_model=SavedSearchResponse,
)
async def update_saved_search_api(
    saved_search_id: int,
    request: SavedSearchUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> SavedSearchResponse:
    """
    Update a saved search belonging to the current user.
    """

    _validate_dates(
        request.from_,
        request.to,
    )

    existing = get_saved_search(
        user_id=current_user.id,
        saved_search_id=saved_search_id,
    )

    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved search not found.",
        )

    try:

        updated = update_saved_search(
            user_id=current_user.id,
            saved_search_id=saved_search_id,
            name=request.name,
            description=request.description,
            from_date=request.from_,
            to_date=request.to,
            tier=request.tier,
            servers=request.servers,
            search_filters=request.search_filters,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved search not found.",
        )

    saved_search = get_saved_search(
        user_id=current_user.id,
        saved_search_id=saved_search_id,
    )

    if saved_search is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved search not found.",
        )

    return _to_response(saved_search)


@router.delete(
    "/{saved_search_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_saved_search_api(
    saved_search_id: int,
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    """
    Delete a saved search belonging to the current user.
    """

    deleted = delete_saved_search(
        user_id=current_user.id,
        saved_search_id=saved_search_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved search not found.",
        )