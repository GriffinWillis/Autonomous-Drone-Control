from app.models import BatterySnapshot, PositionSnapshot
from app.telemetry import TelemetryStore


def test_snapshot_defaults() -> None:
    store = TelemetryStore()
    snap = store.snapshot()
    assert snap.connected is False
    assert snap.position is None
    assert snap.battery is None
    assert snap.flight_mode is None
    assert snap.armed is None
    assert snap.landed_state is None
    assert snap.timestamp is None


def test_snapshot_reflects_position_update() -> None:
    store = TelemetryStore()
    store.position = PositionSnapshot(
        latitude_deg=37.0,
        longitude_deg=-122.0,
        absolute_altitude_m=100.0,
        relative_altitude_m=10.0,
    )
    snap = store.snapshot()
    assert snap.position is not None
    assert snap.position.latitude_deg == 37.0
    assert snap.position.longitude_deg == -122.0


def test_snapshot_reflects_armed_state() -> None:
    store = TelemetryStore()
    store.armed = True
    store.connected = True
    snap = store.snapshot()
    assert snap.armed is True
    assert snap.connected is True


def test_snapshot_reflects_battery() -> None:
    store = TelemetryStore()
    store.battery = BatterySnapshot(remaining_percent=85.0, voltage_v=12.4)
    snap = store.snapshot()
    assert snap.battery is not None
    assert snap.battery.remaining_percent == 85.0
    assert snap.battery.voltage_v == 12.4


def test_snapshot_reflects_flight_mode_and_landed_state() -> None:
    store = TelemetryStore()
    store.flight_mode = "HOLD"
    store.landed_state = "IN_AIR"
    store.timestamp = 1000.0
    snap = store.snapshot()
    assert snap.flight_mode == "HOLD"
    assert snap.landed_state == "IN_AIR"
    assert snap.timestamp == 1000.0
