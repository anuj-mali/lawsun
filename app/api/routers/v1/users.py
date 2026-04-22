from __future__ import annotations

from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, Query

from app.schemas.auth import (
    UserListResponse,
    UserResponse,
    UserUpdate,
    UserUpdateRole,
    MessageResponse,
)

from app.core.exceptions import UserNotFoundError

from app.api.dependencies import CurrentAdmin, CurrentSuperuser, get_user_repo
from app.repositories import UserRepository

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UserListResponse)
async def get_users(
    _: CurrentAdmin,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    is_active: Annotated[bool | None, Query(default=None)] = None,
    cursor: Annotated[uuid.UUID | None, Query(default=None)] = None,
) -> UserListResponse:
    users, next_cursor = await user_repo.get_all(
        page_size=page_size, cursor=cursor, is_active=is_active
    )
    return UserListResponse(items=users, next_cursor=next_cursor)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    _: CurrentAdmin,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    user_id: uuid.UUID,
) -> UserResponse:
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise UserNotFoundError()
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    payload: UserUpdate,
    _: CurrentAdmin,
    user_id: uuid.UUID,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> UserResponse:
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise UserNotFoundError()

    user = await user_repo.update(user, **payload.model_dump(exclude_none=True))
    return UserResponse.model_validate(user)


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    payload: UserUpdateRole,
    _: CurrentSuperuser,
    user_id: uuid.UUID,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> UserResponse:
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise UserNotFoundError()
    user = await user_repo.update(user, role=payload.role)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}/deactivate", response_model=MessageResponse)
async def deactivate_user(
    _: CurrentAdmin,
    user_id: uuid.UUID,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> MessageResponse:
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise UserNotFoundError()
    user = await user_repo.deactivate(user)
    return MessageResponse(message="User deactivated successfully.")
