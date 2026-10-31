# DIP (Depth In Pond): notes for Claude

DIP is a battery-powered pond water-level sensor for Home Assistant (see README.md). Explain things plainly, keep
answers short, show a render or mockup before anything gets printed or built, and ask before anything that costs
money or can't be undone.

- `case/pond_case.py` builds every printed part (numbers at the top); `case/previews.py` renders previews.
- The "DIP" on the lid uses rounded block letters built in `name_shape` in `case/pond_case.py`, 18 mm tall.
- The battery-holder mount is a 4-pad, 25.0 x 94.7 mm hole pattern. The box has no charge-port or button holes: the
  holder's USB-C faces into the box and it charges with the lid off (keep the plug clearance, `PLUG_ZONE`).
- Firmware: `firmware/dip.yaml` (ESPHome; validate with `esphome config`, test with `esphome compile`).
  Home Assistant side: `ha/dip_package.yaml`, a generic package with placeholder pump and phone entity IDs.
- The repo is public so others can build DIP: keep README, the assembly guide (`docs/guide/make_guide.py`) and
  `ha/dip_package.yaml` free of personal details, and in step with the case and firmware.
- Pins: GPIO3 float (wake pin, 100k pull-up), GPIO4 battery divider, GPIO6 Trig, GPIO7 Echo, GPIO5 DS18B20 water temperature (4.7k pull-up). Wiring picture: `docs/guide/d_overview.png`.
- Printing rules: no square vertical corners (1 mm rounds outside, 1 mm fillets inside: `round2d` / `FILLET`),
  and avoid supports when there's a better way (45-degree overhangs, short bridges). Supports are fine where a part
  really needs them; just say so. Check new parts for both.
- STLs are written watertight (`write_stl` merges near-duplicate points and drops zero-area slivers).
- After changing the case, rerun `case/pond_case.py`, `case/previews.py`, then in `docs/guide/`: `make_renders.py`,
  `make_diagrams.py` and `make_guide.py` (copy `case/out/preview_front.png`, `preview_box.png` and
  `preview_esp_mount.png` to `docs/guide/r_front.png`, `r_box_filled.png` and `r_esp_mount.png` first).
