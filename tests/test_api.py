from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api import app


@pytest.fixture
def mock_fc() -> MagicMock:
    instance = MagicMock()
    instance.connect = AsyncMock()
    instance.arm = AsyncMock()
    instance.disarm = AsyncMock()
    instance.takeoff = AsyncMock()
    instance.land = AsyncMock()
    instance.rtl = AsyncMock()
    instance.drone = MagicMock()
    instance.set_connection_url = MagicMock()
    return instance


@pytest.fixture
def client(mock_fc: MagicMock) -> Generator[TestClient, None, None]:
    with (
        patch("app.api.FlightController", return_value=mock_fc),
        patch("app.api.start_telemetry_tasks", return_value=[]),
        TestClient(app) as c,
    ):
        yield c


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_arm_before_connect_returns_409(client: TestClient) -> None:
    assert client.post("/arm").status_code == 409


def test_disarm_before_connect_returns_409(client: TestClient) -> None:
    assert client.post("/disarm").status_code == 409


def test_takeoff_before_connect_returns_409(client: TestClient) -> None:
    assert client.post("/takeoff", json={}).status_code == 409


def test_land_before_connect_returns_409(client: TestClient) -> None:
    assert client.post("/land").status_code == 409


def test_rtl_before_connect_returns_409(client: TestClient) -> None:
    assert client.post("/rtl").status_code == 409


def test_connect_success(client: TestClient, mock_fc: MagicMock) -> None:
    r = client.post("/connect", json={"url": "udpin://0.0.0.0:14540"})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    mock_fc.set_connection_url.assert_called_once_with("udpin://0.0.0.0:14540")
    mock_fc.connect.assert_awaited_once()


def test_connect_no_url_uses_default(client: TestClient, mock_fc: MagicMock) -> None:
    r = client.post("/connect", json={})
    assert r.status_code == 200
    mock_fc.set_connection_url.assert_called_once()


def test_connect_idempotent(client: TestClient, mock_fc: MagicMock) -> None:
    client.post("/connect", json={})
    r = client.post("/connect", json={})
    assert r.status_code == 200
    assert "Already connected" in r.json()["detail"]
    mock_fc.connect.assert_awaited_once()  # only called once


def test_connect_timeout_returns_504(client: TestClient, mock_fc: MagicMock) -> None:
    mock_fc.connect.side_effect = TimeoutError("no heartbeat")
    r = client.post("/connect", json={"url": "udpin://0.0.0.0:14540"})
    assert r.status_code == 504


def test_arm_after_connect(client: TestClient, mock_fc: MagicMock) -> None:
    client.post("/connect", json={})
    r = client.post("/arm")
    assert r.status_code == 200
    mock_fc.arm.assert_awaited_once()


def test_disarm_after_connect(client: TestClient, mock_fc: MagicMock) -> None:
    client.post("/connect", json={})
    r = client.post("/disarm")
    assert r.status_code == 200
    mock_fc.disarm.assert_awaited_once()


def test_takeoff_default_altitude(client: TestClient, mock_fc: MagicMock) -> None:
    client.post("/connect", json={})
    r = client.post("/takeoff", json={})
    assert r.status_code == 200
    mock_fc.takeoff.assert_awaited_once_with(5.0)


def test_takeoff_custom_altitude(client: TestClient, mock_fc: MagicMock) -> None:
    client.post("/connect", json={})
    r = client.post("/takeoff", json={"altitude_m": 20.0})
    assert r.status_code == 200
    mock_fc.takeoff.assert_awaited_once_with(20.0)


def test_land_after_connect(client: TestClient, mock_fc: MagicMock) -> None:
    client.post("/connect", json={})
    r = client.post("/land")
    assert r.status_code == 200
    mock_fc.land.assert_awaited_once()


def test_rtl_after_connect(client: TestClient, mock_fc: MagicMock) -> None:
    client.post("/connect", json={})
    r = client.post("/rtl")
    assert r.status_code == 200
    mock_fc.rtl.assert_awaited_once()


def test_telemetry_disconnected(client: TestClient) -> None:
    r = client.get("/telemetry")
    assert r.status_code == 200
    data = r.json()
    assert data["connected"] is False
    assert data["position"] is None
    assert data["battery"] is None
    assert data["armed"] is None


def test_telemetry_after_connect(client: TestClient) -> None:
    client.post("/connect", json={})
    r = client.get("/telemetry")
    assert r.status_code == 200
    assert r.json()["connected"] is True


def test_disconnect_then_arm_returns_409(
    client: TestClient, mock_fc: MagicMock
) -> None:
    client.post("/connect", json={})
    client.post("/disconnect")
    assert client.post("/arm").status_code == 409
