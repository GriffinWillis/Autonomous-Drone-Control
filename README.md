# Drone Autonomy Prototype

An end-to-end autonomous drone pipeline built in simulation, targeting real hardware deployment. Integrates perception, tracking, decision-making, and MAVLink control into a closed-loop autonomy stack.

## Architecture

```
Camera/Input → Perception → Tracking → Decision Layer → Control (MAVLink)
```

| Component | Technology |
|-----------|------------|
| Flight stack | PX4 SITL → real hardware |
| MAVLink control | MAVSDK (Python) |
| Perception | YOLOv8 (Ultralytics) |
| Tracking | YOLO built-in / ByteTrack |
| Decision logic | Rule-based state machine |

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

**2. Run the autonomy stack:**

```bash
./venv/bin/python -m app.main
```

The default connection is `udpin://0.0.0.0:14540`. Override with:

```bash
MAVSDK_CONNECTION=udpin://0.0.0.0:14540 ./venv/bin/python -m app.main
```

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
- [ ] Phase 2 — YOLOv8 perception on video input
- [ ] Phase 3 — Persistent object tracking with IDs
- [ ] Phase 4 — Integrated perception + control loop
- [ ] Phase 5 — Rule-based decision logic (track, search, idle states)
- [ ] Phase 6 — Simulated geolocation / target GPS approximation

## Dependencies

Runtime deps are declared in `pyproject.toml` and pinned in `requirements.txt`. Dev deps are pinned in `requirements-dev.txt`.

To add a runtime dependency: add it to `requirements.in`, run `pip-compile requirements.in`, then update `pyproject.toml`.
