from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    CurrentAdmin,
    CurrentUser,
    get_auth_service,
    get_user_repo,
)
from app.core.exceptions import DuplicateEmailError
from app.repositories import UserRepository
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    LoginResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChange,
    MessageResponse,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


# Users
@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: UserCreate,
    _: CurrentAdmin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> UserResponse:
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


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponse:
    return await auth_service.login(payload.email, payload.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    return await auth_service.refresh(payload.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    payload: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> MessageResponse:
    await auth_service.logout(payload.refresh_token)
    return MessageResponse(message="Logged out successfully.")


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(user)


# Password
@router.post("/password-reset/request", response_model=MessageResponse)
async def request_password_reset(
    payload: PasswordResetRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> MessageResponse:
    # TODO: Send email with reset link
    token = await auth_service.request_password_reset(payload.email)  # noqa: F841
    return MessageResponse(
        message="If an account exists for this email, a reset link has been sent."
    )


@router.post("/password-reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    payload: PasswordResetConfirm,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    await auth_service.confirm_password_reset(payload.token, payload.new_password)
    return MessageResponse(message="Password has been reset successfully.")


@router.post("/me/password", response_model=MessageResponse)
async def change_password(
    payload: PasswordChange,
    user: CurrentUser,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> MessageResponse:
    await auth_service.change_password(
        user, payload.current_password, payload.new_password
    )
    return MessageResponse(
        message="Password has been changed successfully. Please login with your new password."
    )
