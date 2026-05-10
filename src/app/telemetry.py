from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from mavsdk import System

from app.models import BatterySnapshot, PositionSnapshot, TelemetrySnapshot

logger = logging.getLogger(__name__)


@dataclass
class TelemetryStore:
    connected: bool = False
    position: PositionSnapshot | None = None
    battery: BatterySnapshot | None = None
    flight_mode: str | None = None
    armed: bool | None = None
    landed_state: str | None = None
    timestamp: float | None = None

    def snapshot(self) -> TelemetrySnapshot:
        return TelemetrySnapshot(
            connected=self.connected,
            position=self.position,
            battery=self.battery,
            flight_mode=self.flight_mode,
            armed=self.armed,
            landed_state=self.landed_state,
            timestamp=self.timestamp,
        )


async def _poll_position(drone: System, store: TelemetryStore) -> None:
    async for pos in drone.telemetry.position():
        store.position = PositionSnapshot(
            latitude_deg=pos.latitude_deg,
            longitude_deg=pos.longitude_deg,
            absolute_altitude_m=pos.absolute_altitude_m,
            relative_altitude_m=pos.relative_altitude_m,
        )
        store.timestamp = time.time()


async def _poll_battery(drone: System, store: TelemetryStore) -> None:
    async for bat in drone.telemetry.battery():
        remaining = bat.remaining_percent
        # MAVSDK returns 0.0-1.0; normalize to 0-100
        if remaining <= 1.0:
            remaining *= 100.0
        store.battery = BatterySnapshot(
            remaining_percent=remaining,
            voltage_v=bat.voltage_v,
        )
        store.timestamp = time.time()


async def _poll_flight_mode(drone: System, store: TelemetryStore) -> None:
    async for mode in drone.telemetry.flight_mode():
        store.flight_mode = str(mode).split(".")[-1]
        store.timestamp = time.time()


async def _poll_armed(drone: System, store: TelemetryStore) -> None:
    async for armed in drone.telemetry.armed():
        store.armed = armed
        store.timestamp = time.time()


async def _poll_landed_state(drone: System, store: TelemetryStore) -> None:
    async for state in drone.telemetry.landed_state():
        store.landed_state = str(state).split(".")[-1]
        store.timestamp = time.time()


_Poller = Callable[[System, TelemetryStore], Coroutine[Any, Any, None]]

_POLLERS: list[_Poller] = [
    _poll_position,
    _poll_battery,
    _poll_flight_mode,
    _poll_armed,
    _poll_landed_state,
]


async def _guarded(poller: _Poller, drone: System, store: TelemetryStore) -> None:
    try:
        await poller(drone, store)
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("Telemetry poller %s crashed", poller.__name__)


def start_telemetry_tasks(
    drone: System, store: TelemetryStore
) -> list[asyncio.Task[None]]:
    return [
        asyncio.create_task(
            _guarded(poller, drone, store),
            name=f"telemetry:{poller.__name__}",
        )
        for poller in _POLLERS
    ]


__all__ = ["TelemetryStore", "start_telemetry_tasks"]
