# Drone Autonomy Prototype

An end-to-end autonomous drone pipeline built in simulation, targeting real hardware deployment. The system integrates perception, tracking, decision-making, and MAVLink control into a closed-loop autonomy stack.

## Architecture

```
Camera/Input → Perception → Tracking → Decision Layer → Control (MAVLink)
```

| Component | Technology |
|-----------|-----------|
| Flight stack | PX4 SITL → real hardware |
| MAVLink control | MAVSDK (Python) |
| Perception | YOLOv8 (Ultralytics) |
| Tracking | YOLO built-in / ByteTrack |
| Decision logic | Rule-based state machine |

## Prerequisites

- Ubuntu 24.04 (WSL2 or native)
- Python 3.12+
- [PX4-Autopilot](https://github.com/PX4/PX4-Autopilot) cloned alongside this repo
- PX4 build dependencies installed (`~/PX4-Autopilot/Tools/setup/ubuntu.sh`)
- Colosseum + Unreal Engine 5 on Windows (for simulation)

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
```

## Simulation Startup (Colosseum + PX4 SITL)

Follow these steps in order every session.

**1. Windows — Start Colosseum**

Open UE5, load `C:\Dev\Colosseum\Unreal\Environments\BlocksV2\Blocks.uproject`, press Play.

**2. WSL2 — Start PX4 SITL**

```bash
make sim
```

Wait until the console shows `Ready for takeoff!`

**3. WSL2 — Run the autonomy stack** (new terminal)

```bash
make run
```

**Between runs:** `Ctrl+C` PX4, then repeat steps 2–3.

## Development

| Command | Description |
|---------|-------------|
| `make lint` | Lint with ruff |
| `make fmt` | Format with ruff |
| `make typecheck` | Type check with mypy |
| `make test` | Run tests with coverage |
| `make audit` | Security audit with pip-audit |
| `make all` | Run everything |

```bash
pre-commit install
```

## Development Phases

- [x] **Phase 1** — MAVLink control (arm, takeoff, hold, land)
- [ ] **Phase 2** — YOLOv8 perception on video input
- [ ] **Phase 3** — Persistent object tracking with IDs
- [ ] **Phase 4** — Integrated perception + control loop
- [ ] **Phase 5** — Rule-based decision logic (track, search, idle states)
- [ ] **Phase 6** — Simulated geolocation / target GPS approximation

## Dependency Management

Runtime dependencies are declared in `pyproject.toml` and pinned in `requirements.txt`.
Dev dependencies are pinned in `requirements-dev.txt`.

To add a runtime dependency:

1. Add it to `requirements.in` (loose constraint)
2. Regenerate: `pip-compile requirements.in`
3. Update `pyproject.toml` `dependencies` to match
