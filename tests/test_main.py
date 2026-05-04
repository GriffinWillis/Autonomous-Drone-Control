from unittest.mock import AsyncMock, patch

from app.main import main


def test_main_runs_flight() -> None:
    with patch("app.main.FlightController") as mock_fc:
        instance = mock_fc.return_value.__aenter__.return_value
        instance.run_demo_flight = AsyncMock()
        mock_fc.return_value.__aexit__ = AsyncMock(return_value=False)
        main()
    instance.run_demo_flight.assert_awaited_once()
