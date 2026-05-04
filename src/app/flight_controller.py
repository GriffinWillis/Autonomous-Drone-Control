from __future__ import annotations

import asyncio
import logging
from types import TracebackType

from mavsdk import System

logger = logging.getLogger(__name__)

TAKEOFF_ALTITUDE_M: float = 5.0
HOLD_SECONDS: float = 5.0
CONNECTION_TIMEOUT_S: float = 30.0


class FlightController:
    def __init__(self, connection_url: str = "udpin://0.0.0.0:14540") -> None:
        self._url = connection_url
        self._drone = System()

    async def __aenter__(self) -> FlightController:
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass

    async def connect(self) -> None:
        logger.info("Connecting to %s", self._url)
        await self._drone.connect(system_address=self._url)
        async with asyncio.timeout(CONNECTION_TIMEOUT_S):
            async for state in self._drone.core.connection_state():
                if state.is_connected:
                    logger.info("Drone connected")
                    return
        raise TimeoutError(f"No heartbeat within {CONNECTION_TIMEOUT_S}s")

    async def wait_until_ready(self) -> None:
        logger.info("Waiting for global position and home position fix...")
        async for health in self._drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                logger.info("Position fix acquired — ready to fly")
                return

    async def arm(self) -> None:
        logger.info("Arming...")
        await self._drone.action.arm()

    async def takeoff(self, altitude_m: float = TAKEOFF_ALTITUDE_M) -> None:
        await self._drone.action.set_takeoff_altitude(altitude_m)
        logger.info("Taking off to %.1f m", altitude_m)
        await self._drone.action.takeoff()

    async def wait_for_altitude(self, target_m: float) -> None:
        async for position in self._drone.telemetry.position():
            if position.relative_altitude_m >= target_m * 0.95:
                return

    async def land(self) -> None:
        logger.info("Landing...")
        await self._drone.action.land()

    async def run_demo_flight(self) -> None:
        await self.wait_until_ready()
        await self.arm()
        await self.takeoff(TAKEOFF_ALTITUDE_M)
        await self.wait_for_altitude(TAKEOFF_ALTITUDE_M)
        logger.info("Holding for %.0f s", HOLD_SECONDS)
        await asyncio.sleep(HOLD_SECONDS)
        await self.land()
