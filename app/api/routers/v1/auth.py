from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import (
    CurrentUser,
    get_auth_service,
)
from app.core.exceptions import UserNotFoundError
from app.schemas.auth import (
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
    try:
        token = await auth_service.request_password_reset(payload.email)  # noqa: F841
    except UserNotFoundError:
        pass

    return MessageResponse(
        message="If an account exists for this email, a reset link has been sent."
    )


@router.post("/password-reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    payload: PasswordResetConfirm,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> MessageResponse:
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
