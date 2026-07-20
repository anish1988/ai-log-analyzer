"""
Before any SSH happens, confirm the current user/session may reach every
server implied by the tier + server selection.

TODO: replace `_check_ssh_permission` with a real check (vault/short-lived
cert lookup, a cached admin-approval flag, etc). Stubbed as granted for now
so the rest of the pipeline is testable end to end.
"""
from app.config.servers import ServerConfig, get_selectable_servers, get_server_by_id
from app.schemas.log_analysis import PermissionCheckRequest, PermissionCheckResponse


async def _check_ssh_permission(server: ServerConfig) -> bool:
    return True


async def check_permission(request: PermissionCheckRequest) -> PermissionCheckResponse:
    eligible_ids = {s.id for s in get_selectable_servers(request.tier)}
    candidates = [
        server for sid in request.servers
        if sid in eligible_ids and (server := get_server_by_id(sid)) is not None
    ]

    if not candidates:
        return PermissionCheckResponse(
            granted=False,
            message="No valid servers were selected for the chosen tier.",
        )

    denied: list[str] = []
    for server in candidates:
        if not await _check_ssh_permission(server):
            denied.append(server.id)

    if denied:
        return PermissionCheckResponse(
            granted=False,
            message=f"Permission is required for: {', '.join(denied)}.",
        )

    return PermissionCheckResponse(granted=True)