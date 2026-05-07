import asyncio
import logging
import os

from app.flight_controller import FlightController

logger = logging.getLogger(__name__)

_DEFAULT_CONNECTION = "udpout://127.0.0.1:14541"


async def _run() -> None:
    url = os.environ.get("MAVSDK_CONNECTION", _DEFAULT_CONNECTION)
    async with FlightController(url) as fc:
        await fc.run_demo_flight()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(_run())


if __name__ == "__main__":
    main()
