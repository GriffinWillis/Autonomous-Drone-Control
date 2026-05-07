  Step 1 — Build and open Colosseum Blocks environment:
    Open Unreal Engine 5.6
    Open project: C:\Dev\Colosseum\Unreal\Environments\BlocksV2\Blocks.uproject
    When prompted to rebuild the Colosseum plugin, click Yes
    Wait for the editor to fully load before pressing Play

  Step 2 — Create settings.json on Windows:
    Location: C:\Users\<YourUsername>\Documents\AirSim\settings.json
    Content: (see Phase 2 below — use the WSL2 variant)

  Step 3 — Windows Firewall:
    Open Windows Defender Firewall → Advanced Settings
    Add inbound rules for:
      TCP port 4560  (Colosseum ↔ PX4 simulator link)
      UDP port 14540 (MAVLink control port)

  Step 4 — Find your WSL2 host IP (run this in PowerShell each session):
    ipconfig
    Look for "vEthernet (WSL)" adapter → IPv4 Address (e.g. 172.31.64.1)
    This changes on reboot — must be checked each time.
