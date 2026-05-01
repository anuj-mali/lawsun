from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.schemas.ministry import (
    MinistryCreate,
    MinistryResponse,
    MinistryUpdate,
    MinistryListResponse,
)
from app.schemas.auth import MessageResponse

from app.api.dependencies import (
    CurrentUser,
    CurrentAdmin,
    CurrentSuperuser,
    get_ministry_service,
)
from app.services.ministry import MinistryService

router = APIRouter(prefix="/ministry", tags=["ministry"])


@router.get("/", response_model=MinistryListResponse)
async def get_ministries(
    _: CurrentUser,
    ministry_service: Annotated[MinistryService, Depends(get_ministry_service)],
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    is_active: Annotated[bool | None, Query()] = None,
    cursor: Annotated[uuid.UUID | None, Query()] = None,
):
    ministries, next_cursor = await ministry_service.get_all(
        page_size=page_size, cursor=cursor, is_active=is_active
    )
    return MinistryListResponse(
        items=[MinistryResponse.model_validate(ministry) for ministry in ministries],
        next_cursor=next_cursor,
    )


@router.get("/{ministry_id}", response_model=MinistryResponse)
async def get_ministry(
    _: CurrentUser,
    ministry_service: Annotated[MinistryService, Depends(get_ministry_service)],
    ministry_id: uuid.UUID,
):
    ministry = await ministry_service.get(ministry_id)
    return MinistryResponse.model_validate(ministry)


@router.post("/", response_model=MinistryResponse, status_code=status.HTTP_201_CREATED)
async def create_ministry(
    payload: MinistryCreate,
    _: CurrentAdmin,
    ministry_service: Annotated[MinistryService, Depends(get_ministry_service)],
) -> MinistryResponse:
    ministry = await ministry_service.create(
        name=payload.name,
        short_name=payload.short_name,
        description=payload.description,
    )
    return MinistryResponse.model_validate(ministry)


@router.patch("/{ministry_id}", response_model=MinistryResponse)
async def update_ministry(
    payload: MinistryUpdate,
    _: CurrentAdmin,
    ministry_id: uuid.UUID,
    ministry_service: Annotated[MinistryService, Depends(get_ministry_service)],
) -> MinistryResponse:
    ministry = await ministry_service.update(
        ministry_id, **payload.model_dump(exclude_unset=True)
    )
    return MinistryResponse.model_validate(ministry)


@router.patch("/{ministry_id}/deactivate", response_model=MessageResponse)
async def deactivate_ministry(
    _: CurrentAdmin,
    ministry_id: uuid.UUID,
    ministry_service: Annotated[MinistryService, Depends(get_ministry_service)],
) -> MessageResponse:
    await ministry_service.deactivate(ministry_id)
    return MessageResponse(message="Ministry deactivated successfully.")


@router.delete(
    "/{ministry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_ministry(
    _: CurrentSuperuser,
    ministry_id: uuid.UUID,
    ministry_service: Annotated[MinistryService, Depends(get_ministry_service)],
) -> None:
    await ministry_service.hard_delete(ministry_id)
