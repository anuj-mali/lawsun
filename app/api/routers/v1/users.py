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

from app.models.user import UserRole
from app.core.exceptions import (
    DuplicateEmailError,
    UserNotFoundError,
    SelfDeactivationError,
    PermissionError,
)

from app.api.dependencies import (
    CurrentAdmin,
    CurrentSuperuser,
    get_auth_service,
    get_user_repo,
)
from app.repositories import UserRepository
from app.services.auth import AuthService

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
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> UserResponse:
    if payload.role in (UserRole.SUPERUSER, UserRole.ADMIN):
        if current_admin.role != UserRole.SUPERUSER:
            raise PermissionError(
                "Superuser access required to create privileged users"
            )

    existing_user = await user_repo.get_by_email(payload.email)
    if existing_user is not None:
        raise DuplicateEmailError()

    user = await user_repo.create(
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
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    is_active: Annotated[bool | None, Query(default=None)] = None,
    cursor: Annotated[uuid.UUID | None, Query(default=None)] = None,
) -> UserListResponse:
    users, next_cursor = await user_repo.get_all(
        page_size=page_size, cursor=cursor, is_active=is_active
    )
    return UserListResponse(
        items=[UserResponse.model_validate(user) for user in users],
        next_cursor=next_cursor,
    )


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
    current_admin: CurrentAdmin,
    user_id: uuid.UUID,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> MessageResponse:
    if current_admin.id == user_id:
        raise SelfDeactivationError()

    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise UserNotFoundError()

    if user.role in (UserRole.ADMIN, UserRole.SUPERUSER):
        if current_admin.role != UserRole.SUPERUSER:
            raise PermissionError("Only superusers can deactivate privileged users")

    user = await user_repo.deactivate(user)
    return MessageResponse(message="User deactivated successfully.")
