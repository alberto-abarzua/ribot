from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



@asynccontextmanager
async def controller_lifespan(_: FastAPI):  # type: ignore # noqa: ANN201
    start_controller()

    yield

    stop_controller()


app = FastAPI(lifespan=controller_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://demo.ribot.dev"],  # Specific domain
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

