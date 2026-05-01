from __future__ import annotations


class AppError(Exception):
    status_code: int = 500
    message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.__class__.message
        super().__init__(self.message)


# 400 Bad Request
class BadRequestError(AppError):
    status_code = 400
    message = "Bad Request"


class InvalidCursorError(BadRequestError):
    message = "Invalid or expired cursor"


class WeakPasswordError(BadRequestError):
    message = "Password does not meet the requirements"


# 401 Unauthorized
class AuthenticationError(AppError):
    status_code = 401
    message = "Authentication required"


class InvalidCredentialsError(AuthenticationError):
    message = "Invalid email or password"


class TokenExpiredError(AuthenticationError):
    message = "Token has expired"


class InvalidTokenError(AuthenticationError):
    message = "Invalid token"


# 403 Forbidden
class PermissionError(AppError):
    status_code = 403
    message = "You do not have permission to perform this action"


class AccountDisabledError(PermissionError):
    message = "This account has been disabled"


class SelfDeactivationError(PermissionError):
    message = "You cannot deactivate your own account"


# 404 Not Found
class NotFoundError(AppError):
    status_code = 404
    message = "Resource not found"


class UserNotFoundError(NotFoundError):
    message = "User not found"


class DocumentNotFoundError(NotFoundError):
    message = "Document not found"


class ConversationNotFoundError(NotFoundError):
    message = "Conversation not found"


class MinistryNotFoundError(NotFoundError):
    message = "Ministry not found"


# 409 Conflict
class ConflictError(AppError):
    status_code = 409
    message = "Resource already exists"


class DuplicateEmailError(ConflictError):
    message = "A user with this email already exists"


class DuplicateDocumentError(ConflictError):
    message = "This document has already been ingested"


class DuplicateMinistryError(ConflictError):
    message = "A ministry with this name already exists"


# 422 Unprocessable Entity
class UnprocessableEntityError(AppError):
    status_code = 422
    message = "Unable to process request"


class IngestionError(UnprocessableEntityError):
    message = "Document ingestion failed"


# 503 Service Unavailable
class ServiceUnavailableError(AppError):
    status_code = 503
    message = "Service temporarily unavailable"


class RedisUnavailableError(ServiceUnavailableError):
    message = "Authentication service is temporarily unavailable"
