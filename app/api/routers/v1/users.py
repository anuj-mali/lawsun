from __future__ import annotations

from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, Query, status

from app.schemas.auth import (
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
    UserUpdateRole,
    MessageResponse,
)

from app.api.dependencies import (
    CurrentAdmin,
    CurrentSuperuser,
    get_auth_service,
    get_user_service,
)
from app.services.auth import AuthService
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    payload: UserCreate,
    current_admin: CurrentAdmin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    user = await user_service.create(
        requester=current_admin,
        email=payload.email,
        hashed_password=auth_service.hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        middle_name=payload.middle_name,
        role=payload.role,
    )

    return UserResponse.model_validate(user)


@router.get("/", response_model=UserListResponse)
async def get_users(
    _: CurrentAdmin,
    user_service: Annotated[UserService, Depends(get_user_service)],
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    is_active: Annotated[bool | None, Query()] = None,
    cursor: Annotated[uuid.UUID | None, Query()] = None,
) -> UserListResponse:
    users, next_cursor = await user_service.get_all(
        page_size=page_size, cursor=cursor, is_active=is_active
    )
    return UserListResponse(
        items=[UserResponse.model_validate(user) for user in users],
        next_cursor=next_cursor,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    _: CurrentAdmin,
    user_service: Annotated[UserService, Depends(get_user_service)],
    user_id: uuid.UUID,
) -> UserResponse:
    user = await user_service.get_by_id(user_id)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    payload: UserUpdate,
    _: CurrentAdmin,
    user_id: uuid.UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    user = await user_service.update(user_id, **payload.model_dump(exclude_unset=True))
    return UserResponse.model_validate(user)


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    payload: UserUpdateRole,
    _: CurrentSuperuser,
    user_id: uuid.UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    user = await user_service.update(user_id, role=payload.role)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}/deactivate", response_model=MessageResponse)
async def deactivate_user(
    current_admin: CurrentAdmin,
    user_id: uuid.UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> MessageResponse:
    await user_service.deactivate(user_id, requester=current_admin)
    return MessageResponse(message="User deactivated successfully.")
