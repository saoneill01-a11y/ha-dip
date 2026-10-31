# DIP (Depth In Pond): notes for Claude

Sean's DIP ("Depth In Pond"), his battery-powered pond water-level sensor for Home Assistant (see README.md). Sean is a network engineer
and target shooter, not a programmer: explain things plainly, keep answers short, show a render or mockup
before anything gets printed or built, and ask before anything that costs money or can't be undone.

- `case/pond_case.py` builds every printed part (numbers at the top); `case/previews.py` renders previews.
- The "DIP" on the lid uses BLIPR's rounded block letters (copied from `name_cuts` in BLIPR's `case/blipr_case.py`), scaled to 18 mm.
- The battery-holder mount copies BLIPR's base (saoneill01-a11y/rangebook-blipr,
  `case/user_edits/base_from_sean_2026-10-22.stl`). The box has no charge-port or button holes: the holder's
  USB-C faces into the box and Sean charges it with the lid off (keep the plug clearance, `PLUG_ZONE`).
- Firmware: `firmware/dip.yaml` (ESPHome; validate with `esphome config`, test with `esphome compile`). HA side: `ha/dip_package.yaml`
  is the public, generic package (placeholder pump/phone IDs). Sean's own install is `packages/pond.yaml` in his Home Assistant repo.
- The repo is meant to be public so others can build DIP: keep README, the assembly guide (`docs/guide/make_guide.py`) and
  `ha/dip_package.yaml` free of Sean's personal details, and in step with the case, firmware and his HA setup.
- Pins: GPIO3 float (wake pin, 100k pull-up), GPIO4 battery divider, GPIO6 Trig, GPIO7 Echo, GPIO5 DS18B20 water temperature (4.7k pull-up). Wiring picture: `docs/wiring.svg` (render to PNG with cairosvg).
- Sean's printing rules: no square vertical corners (1 mm rounds outside, 1 mm fillets inside: `round2d` / `FILLET`),
  and avoid supports when there's a better way (45-degree overhangs, short bridges). He can print supports, so they
  are fine where a part really needs them; just say so. Check new parts for both.
- STLs are written watertight (`write_stl` merges near-duplicate points and drops zero-area slivers).
- Commit as Sean; push to `main` after each piece of work.
