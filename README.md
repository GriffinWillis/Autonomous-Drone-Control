# Drone GCS — Flight Control & Mission Planning

A web-based Ground Control Station (GCS) for autonomous drone missions, built on PX4 + MAVSDK. Plan waypoint missions on an interactive map and execute them via a REST API connected to the flight computer.

> **Perception/object detection is handled in a separate project.** This repo focuses purely on flight control and mission planning.

## Architecture

```
Web GCS (browser) → REST API (Python backend) → MAVSDK → PX4 (SITL / hardware)
```

| Component | Technology |
|-----------|------------|
| Flight stack | PX4 SITL → real hardware |
| MAVLink control | MAVSDK (Python) |
| API backend | Python (FastAPI) |
| Web frontend | Map-centric UI (Leaflet / MapLibre) |

## Prerequisites

- Ubuntu 24.04 (WSL2 or native)
- Python 3.12+
- [PX4-Autopilot](https://github.com/PX4/PX4-Autopilot) cloned to `~/PX4-Autopilot`
- PX4 build dependencies: `~/PX4-Autopilot/Tools/setup/ubuntu.sh`

## Setup

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements-dev.txt
./venv/bin/pip install -e .
pre-commit install
```

## Running

**1. Start PX4 SITL** (in a separate terminal):

```bash
make -C ~/PX4-Autopilot px4_sitl gz_x500
```

> Shortcut: if you have the `sitl` alias in your `~/.bashrc`, just run `sitl`.

**2. Start the API backend:**

```bash
./venv/bin/python -m app.main
```

The server starts on `http://localhost:8000`. Interactive docs are available at `http://localhost:8000/docs`.

**3. Connect to the drone:**

```bash
curl -X POST http://localhost:8000/connect \
  -H "Content-Type: application/json" \
  -d '{"url": "udpin://0.0.0.0:14540"}'
```

Omit the body to use the default connection (`udpin://0.0.0.0:14540`), or override the default via the `MAVSDK_CONNECTION` env var.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness check |
| `POST` | `/connect` | Connect to drone (optional `url` body) |
| `POST` | `/disconnect` | Disconnect and stop telemetry |
| `POST` | `/arm` | Arm the drone |
| `POST` | `/disarm` | Disarm the drone |
| `POST` | `/takeoff` | Takeoff (`altitude_m` body, default 10 m) |
| `POST` | `/land` | Land in place |
| `POST` | `/rtl` | Return to launch |
| `GET` | `/telemetry` | Poll latest telemetry snapshot |

## Development

| Command | Description |
|---------|-------------|
| `make lint` | Lint with ruff |
| `make fmt` | Format with ruff |
| `make typecheck` | Type check with mypy |
| `make test` | Run tests with coverage |
| `make audit` | Security audit with pip-audit |
| `make all` | Run everything |

## Roadmap

- [x] Phase 1 — MAVLink control (arm, takeoff, hold, land)
- [x] Phase 2 — REST API backend wrapping MAVSDK
- [ ] Phase 3 — Web GCS frontend with interactive map
- [ ] Phase 4 — Waypoint mission planning and upload
- [ ] Phase 5 — Loiter, RTL, and additional mission types
- [ ] Phase 6 — Real hardware support and field testing

## Dependencies

Runtime deps are declared in `pyproject.toml` and pinned in `requirements.txt`. Dev deps are pinned in `requirements-dev.txt`.

To add a runtime dependency: add it to `requirements.in`, run `pip-compile requirements.in`, then update `pyproject.toml`.
