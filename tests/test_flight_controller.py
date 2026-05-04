from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.flight_controller import TAKEOFF_ALTITUDE_M, FlightController


@pytest.fixture()
def mock_drone() -> MagicMock:
    drone = MagicMock()
    drone.connect = AsyncMock()

    async def _connected() -> object:
        state = MagicMock()
        state.is_connected = True
        yield state

    drone.core.connection_state = _connected
    drone.action.arm = AsyncMock()
    drone.action.set_takeoff_altitude = AsyncMock()
    drone.action.takeoff = AsyncMock()
    drone.action.land = AsyncMock()

    async def _position() -> object:
        pos = MagicMock()
        pos.relative_altitude_m = -TAKEOFF_ALTITUDE_M
        yield pos

    drone.telemetry.position = _position
    return drone


async def test_connect_succeeds(mock_drone: MagicMock) -> None:
    with patch("app.flight_controller.System", return_value=mock_drone):
        fc = FlightController("udpin://0.0.0.0:14540")
        await fc.connect()
    mock_drone.connect.assert_awaited_once_with(system_address="udpin://0.0.0.0:14540")


async def test_arm_calls_mavsdk(mock_drone: MagicMock) -> None:
    with patch("app.flight_controller.System", return_value=mock_drone):
        fc = FlightController()
        await fc.arm()
    mock_drone.action.arm.assert_awaited_once()


async def test_takeoff_sets_altitude_then_calls_takeoff(mock_drone: MagicMock) -> None:
    with patch("app.flight_controller.System", return_value=mock_drone):
        fc = FlightController()
        await fc.takeoff(TAKEOFF_ALTITUDE_M)
    mock_drone.action.set_takeoff_altitude.assert_awaited_once_with(TAKEOFF_ALTITUDE_M)
    mock_drone.action.takeoff.assert_awaited_once()


async def test_land_calls_mavsdk(mock_drone: MagicMock) -> None:
    with patch("app.flight_controller.System", return_value=mock_drone):
        fc = FlightController()
        await fc.land()
    mock_drone.action.land.assert_awaited_once()


async def test_demo_flight_sequence(mock_drone: MagicMock) -> None:
    with (
        patch("app.flight_controller.System", return_value=mock_drone),
        patch("app.flight_controller.HOLD_SECONDS", 0),
    ):
        fc = FlightController()
        await fc.connect()
        await fc.run_demo_flight()

    mock_drone.action.arm.assert_awaited_once()
    mock_drone.action.takeoff.assert_awaited_once()
    mock_drone.action.land.assert_awaited_once()
