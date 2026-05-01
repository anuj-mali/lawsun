from .auth import router as auth_router
from .users import router as users_router
from .ministry import router as ministry_router

from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["v1"])
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(ministry_router)

__all__ = ["router"]
