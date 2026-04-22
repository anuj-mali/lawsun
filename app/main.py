from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routers.auth import router as auth_router
from app.core.exceptions import AppError

app = FastAPI()
app.include_router(auth_router)


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.get("/health")
def health():
    return {"status": "ok"}
