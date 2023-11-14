import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.move import router as move_router
from routers.settings import router as settings_router
from utils.general import start_controller, stop_controller


class IgnoreEndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "/settings/status/" not in record.getMessage()


logging.basicConfig(level=logging.INFO)
logging.getLogger("uvicorn.access").addFilter(IgnoreEndpointFilter())


@asynccontextmanager
async def controller_lifespan(_: FastAPI):  # type: ignore # noqa: ANN201
    start_controller()

    yield

    stop_controller()


app = FastAPI(lifespan=controller_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(move_router, prefix="/move")
app.include_router(settings_router, prefix="/settings")
