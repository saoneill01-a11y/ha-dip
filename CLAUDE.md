# DIP (Depth In Pond): notes for Claude

DIP is a battery-powered pond water-level sensor for Home Assistant (see README.md). Explain things plainly, keep
answers short, show a render or mockup before anything gets printed or built, and ask before anything that costs
money or can't be undone.

- `case/pond_case.py` builds every printed part (numbers at the top); `case/previews.py` renders previews.
- The "DIP" on the lid uses rounded block letters built in `name_shape` in `case/pond_case.py`, 18 mm tall.
- Power: a plain 18650 holder (76.2 x 21.2 x 20 mm, `HOLDER`) on a platform with one M3 insert; the XIAO ESP32-C6
  charges the cell from its USB-C. No battery-shield boards: their always-on booster drains the cell in a day.
  The box has no charge-port holes: a short USB-C cable stays in the XIAO and charges with the lid off.
- Firmware: `firmware/dip.yaml` (ESPHome; validate with `esphome config`, test with `esphome compile`).
  Home Assistant side: `ha/dip_package.yaml`, a generic package with placeholder pump and phone entity IDs.
- The repo is public so others can build DIP: keep README, the assembly guide (`docs/guide/make_guide.py`) and
  `ha/dip_package.yaml` free of personal details, and in step with the case and firmware.
- Pins (XIAO C6): D1/GPIO1 float (wake pin, 100k pull-up; only GPIO0-7 can wake a C6), D0/GPIO0 battery divider from BAT+,
  D4/GPIO22 Trig, D5/GPIO23 Echo, D3/GPIO21 DS18B20 (4.7k pull-up). GPIO3/GPIO14 drive the antenna switch. ESPHome 2025.7+.
  ESPHome won't build from a path with spaces: copy the yaml and secrets to a plain path to compile. Wiring picture: `docs/guide/d_overview.png`.
- Printing rules: no square vertical corners (1 mm rounds outside, 1 mm fillets inside: `round2d` / `FILLET`),
  and avoid supports when there's a better way (45-degree overhangs, short bridges). Supports are fine where a part
  really needs them; just say so. Check new parts for both.
- STLs are written watertight (`write_stl` merges points that land on the same 32-bit spot and drops only the triangles that collapse; never drop other slivers, it opens edges). Check new parts for open edges before pushing.
- After changing the case, rerun `case/pond_case.py`, `case/previews.py`, then in `docs/guide/`: `make_renders.py`,
  `make_diagrams.py` and `make_guide.py` (copy `case/out/preview_front.png`, `preview_box.png` and
  `preview_esp_mount.png` to `docs/guide/r_front.png`, `r_box_filled.png` and `r_esp_mount.png` first).
