# DIP (Depth In Pond): notes for Claude

Sean's DIP ("Depth In Pond"), his battery-powered pond water-level sensor for Home Assistant (see README.md). Sean is a network engineer
and target shooter, not a programmer: explain things plainly, keep answers short, show a render or mockup
before anything gets printed or built, and ask before anything that costs money or can't be undone.

- `case/pond_case.py` builds every printed part (numbers at the top); `case/previews.py` renders previews.
- The "DIP" on the lid uses BLIPR's rounded block letters (copied from `name_cuts` in BLIPR's `case/blipr_case.py`), scaled to 18 mm.
- The battery-holder mount copies BLIPR's base (saoneill01-a11y/rangebook-blipr,
  `case/user_edits/base_from_sean_2026-10-22.stl`). The box has no charge-port or button holes: the holder's
  USB-C faces into the box and Sean charges it with the lid off (keep the plug clearance, `PLUG_ZONE`).
- Firmware: `firmware/dip.yaml` (ESPHome; validate with `esphome config`, test with `esphome compile`). HA side: `ha/dip_package.yaml`.
- Pins: GPIO3 float (wake pin, 100k pull-up), GPIO4 battery divider, GPIO6 Trig, GPIO7 Echo, GPIO5 DS18B20 water temperature (4.7k pull-up). Wiring picture: `docs/wiring.svg` (render to PNG with cairosvg).
- Commit as Sean; push to `main` after each piece of work.
