from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.flight_controller import FlightController
from app.models import (
    ConnectRequest,
    HealthResponse,
    StatusResponse,
    TakeoffRequest,
    TelemetrySnapshot,
)
from app.telemetry import TelemetryStore, start_telemetry_tasks

logger = logging.getLogger(__name__)

_DEFAULT_CONNECTION = os.environ.get("MAVSDK_CONNECTION", "udpin://0.0.0.0:14540")


class AppState:
    def __init__(self) -> None:
        self.fc = FlightController()
        self.store = TelemetryStore()
        self.tasks: list[asyncio.Task[None]] = []
        self.connected = False


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.drone_state = AppState()
    logger.info("Drone API ready — POST /connect to connect")
    yield
    state: AppState = app.state.drone_state
    for task in state.tasks:
        task.cancel()
    if state.tasks:
        await asyncio.gather(*state.tasks, return_exceptions=True)
    logger.info("Drone API shut down cleanly")


app = FastAPI(title="Drone GCS API", version="2.0.0", lifespan=lifespan)


def _get_state(request: Request) -> AppState:
    state: AppState = request.app.state.drone_state
    return state


def _require_connected(state: AppState) -> None:
    if not state.connected:
        raise HTTPException(
            status_code=409, detail="Not connected. POST /connect first."
        )


@app.exception_handler(Exception)
async def _generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s", request.url)
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@app.post("/connect", response_model=StatusResponse)
async def connect(body: ConnectRequest, request: Request) -> StatusResponse:
    state = _get_state(request)
    if state.connected:
        return StatusResponse(status="ok", detail="Already connected")
    url = body.url or _DEFAULT_CONNECTION
    state.fc.set_connection_url(url)
    try:
        await state.fc.connect()
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    state.connected = True
    state.store.connected = True
    state.tasks = start_telemetry_tasks(state.fc.drone, state.store)
    return StatusResponse(status="ok", detail=f"Connected to {url}")


@app.post("/disconnect", response_model=StatusResponse)
async def disconnect(request: Request) -> StatusResponse:
    state = _get_state(request)
    for task in state.tasks:
        task.cancel()
    if state.tasks:
        await asyncio.gather(*state.tasks, return_exceptions=True)
    state.tasks = []
    state.connected = False
    state.store.connected = False
    return StatusResponse(status="ok", detail="Disconnected")


@app.post("/arm", response_model=StatusResponse)
async def arm(request: Request) -> StatusResponse:
    state = _get_state(request)
    _require_connected(state)
    await state.fc.arm()
    return StatusResponse(status="ok", detail="Armed")


@app.post("/disarm", response_model=StatusResponse)
async def disarm(request: Request) -> StatusResponse:
    state = _get_state(request)
    _require_connected(state)
    await state.fc.disarm()
    return StatusResponse(status="ok", detail="Disarmed")


@app.post("/takeoff", response_model=StatusResponse)
async def takeoff(body: TakeoffRequest, request: Request) -> StatusResponse:
    state = _get_state(request)
    _require_connected(state)
    await state.fc.takeoff(body.altitude_m)
    return StatusResponse(
        status="ok", detail=f"Takeoff to {body.altitude_m}m initiated"
    )


@app.post("/land", response_model=StatusResponse)
async def land(request: Request) -> StatusResponse:
    state = _get_state(request)
    _require_connected(state)
    await state.fc.land()
    return StatusResponse(status="ok", detail="Landing initiated")


@app.post("/rtl", response_model=StatusResponse)
async def rtl(request: Request) -> StatusResponse:
    state = _get_state(request)
    _require_connected(state)
    await state.fc.rtl()
    return StatusResponse(status="ok", detail="RTL initiated")


@app.get("/telemetry", response_model=TelemetrySnapshot)
async def telemetry(request: Request) -> TelemetrySnapshot:
    state = _get_state(request)
    return state.store.snapshot()
