from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ConnectRequest(BaseModel):
    url: str | None = Field(
        default=None,
        description="MAVLink connection URL. Falls back to MAVSDK_CONNECTION env var.",
    )


class TakeoffRequest(BaseModel):
    altitude_m: float = Field(default=5.0, gt=0.0, le=120.0)


class StatusResponse(BaseModel):
    status: Literal["ok"]
    detail: str = ""


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str = "2.0.0"


class PositionSnapshot(BaseModel):
    latitude_deg: float
    longitude_deg: float
    absolute_altitude_m: float
    relative_altitude_m: float


class BatterySnapshot(BaseModel):
    remaining_percent: float
    voltage_v: float


class TelemetrySnapshot(BaseModel):
    connected: bool
    position: PositionSnapshot | None = None
    battery: BatterySnapshot | None = None
    flight_mode: str | None = None
    armed: bool | None = None
    landed_state: str | None = None
    timestamp: float | None = None
