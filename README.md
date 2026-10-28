# DIP (Depth In Pond)

A battery-powered water-level sensor for the pond, reporting to Home Assistant over Wi-Fi.

- **Level:** a JSN-SR20-Y3.0 ultrasonic sensor looks down a 3" PVC "stilling pipe" standing in the pond, so the
  waterfall, fountain and net can't confuse it. Reports every 20 minutes.
- **Tripwire:** a float switch inside the same pipe wakes the board the moment the water drops too low, so a
  plumbing failure is caught in seconds, not 20 minutes.
- **What Home Assistant does with it:** graphs the level, alerts on low water, and turns the pond pumps off
  (Tuya plug) so they don't run dry, then back on when the level recovers.
- **Power:** one 18650 cell in the same battery holder as BLIPR, ESP32-C3 SuperMini in deep sleep between
  readings. Target: 5-8 months per charge.

## Parts

| Part | Notes |
|---|---|
| ESP32-C3 SuperMini | on hand |
| 18650 battery holder (USB-C + micro-USB, same as BLIPR) + 18650 cell | on hand. Set its slide switch SW1 to **stay on** (not auto-shutdown) |
| JSN-SR20-Y3.0 ultrasonic sensor (dual probes, 48 x 23 mm board, 21.5 mm probes) | on hand. Leave the MODE pad empty (normal Trig/Echo mode, what the firmware uses). The board is labeled 5V: bench-test it on 3V3 first |
| Mini vertical float switch (PP, M10 stem) | 16" leads: spliced onto the 4-core cable inside the pipe cap's chamber |
| DS18B20 waterproof temperature probe (1 m) | on hand; its included 4.7k resistor is the pull-up. Hangs inside the pipe near the bottom; spliced onto the 4-core cable in the cap |
| 4-core outdoor cable, box to pipe cap | carries 3V3, GND (shared by the temperature probe and float), float, temperature data through one gland. The ultrasonic probe leads reach the box on their own. Splices: solder + adhesive-lined heat shrink |
| Resistors | 3 x 100 kOhm (battery reading divider + float pull-up), 4.7 kOhm (temperature probe pull-up) |
| 3" PVC pipe (89 mm OD, 76 mm ID), about 30" long | on hand. 3-4 x 1/4" holes in the bottom 2-3", one 1/8" vent near the top |
| Cinder block + pea gravel | holds the pipe upright in the pond (level it while packing the gravel). Cables run along the back of the coping to the box on the post, under the net |
| 3 x PG7 cable glands | on hand |
| 5 x M2.5 x 6 screws (4 sensor board, 1 SuperMini clamp) | |
| 4 x M3 heat-set inserts + 4 x M3 screws with rubber washers (lid), 3 more inserts + M3 screws (pipe cap top), 2 x M4 screws (float bracket), 1 short stainless screw (locks the cap to the pipe; pilot-drill the PVC) | |

## Wiring

Step-by-step build, soldering and testing: [docs/DIP-assembly-guide.docx](docs/DIP-assembly-guide.docx)
(rebuilt by the scripts in `docs/guide/`).

![Wiring](docs/guide/d_overview.png)

| SuperMini pin | Goes to |
|---|---|
| 3.3 / G | holder 3V pair 1 (+ / -) |
| GPIO4 | middle of the 100k/100k divider: 100k (A) to the holder's + battery contact, 100k (B) to G |
| GPIO6 / GPIO7 | sensor Trig / Echo (sensor 5V and GND pins from holder 3V pair 2) |
| GPIO5 | 4-core wire 3, temperature data (4.7k from wire 1) |
| GPIO3 | 4-core wire 4, float (100k (C) from wire 1). Wakes the board. Float must be OPEN when the water is normal |

4-core wires 1 / 2 (3.3V / GND) go to holder 3V pair 3. The two pull-ups sit at the cable's box end. At the pipe cap:
wire 1 to the probe's red, wire 2 to the probe's black and one float wire, wire 3 to yellow, wire 4 to the other float wire.

## Firmware (`firmware/`) and Home Assistant (`ha/`)

- `firmware/dip.yaml`: ESPHome. Wakes every 20 min (every 2 min while the float is low), takes 5 readings,
  sends the middle one plus the water temperature, sleeps. Copy `secrets.example.yaml` to `secrets.yaml` and fill it in.
  First flash over USB: `esphome run firmware/dip.yaml` (hold BOOT, tap RESET if the board isn't found).
  Test-compiled with ESPHome 2026.10.0.
- **Bench test before wiring it in:** connect the sensor board to the SuperMini with jumpers (3V3, GND, Trig GPIO6,
  Echo GPIO7), flash, and check "Distance to water" reads sensibly against a wall. With a meter, check the sensor
  board's idle current: it stays powered while the ESP32 sleeps, so more than about 1 mA drains the cell in weeks.
  If either is bad, the sensor gets switched by a GPIO instead.
- `ha/dip_package.yaml`: Home Assistant package. Pond level in inches below full, "Pond water low", a critical
  phone alert + pumps off when low, pumps back on 10 min after it recovers, alerts if the sensor goes quiet or its
  battery drops below 20 %, and the "DIP stay awake" switch for wireless updates. Check the entity IDs at
  the top of the file first.
- Calibrate once: with the pond full, copy "Distance to water" into "Pond full distance" in HA.

## Printed parts (`case/`)

`python3 case/pond_case.py` builds every part into `case/out/` (needs `pip install manifold3d numpy`).
`python3 case/previews.py` draws the preview pictures.

| File | What | Print |
|---|---|---|
| `box.stl` | electronics box, stands upright on the pergola post (about 3" x 5.75" x 1.75"): BLIPR's battery-holder mount, 4 screw standoffs for the sensor board, hooks + a screw post for the SuperMini, 3 glands in the bottom end. No charge-port or button holes: charge through the holder's USB-C with the lid off, or take the cell out | as is, back plate down. PETG or ASA |
| `box_lid.stl` | lid with a drip edge, two stiffening ribs underneath, washer seats round the 4 corner screws, and "DIP" cut 0.6 mm into the front in BLIPR's lettering (18 mm tall) | as is (already flipped) |
| `esp_clamp.stl` | small tab that holds the SuperMini's far end down (its USB end slides under two lips first); one M2.5 x 6 screw | flat |
| `gasket.stl` | TPU ring for the rim groove: 1.6 wide x 1.9 tall, stands 0.5 mm proud so the lid squeezes it about 25 % | 95A TPU, flat, 100 % infill |
| `pipe_cap.stl` | slides over the pipe (90 mm bore), holds both probes on a band across the middle; the rest of the plate is open for the float and temperature cables. Slot in the rim where the 3 cables leave sideways (point it at the post), lock-screw hole in the skirt. 45-degree chamfer under the ledge | upside down (rim on the bed); supports only under the probe band |
| `pipe_cap_top.stl` | flat lid: 3 screws into the cap's posts, closes the top of the cable slot. Keeps rain and bugs out (doesn't need to seal: everything in the cap is waterproof) | flat |
| `float_bracket.stl` | holds the float switch inside the pipe (no brace) | as is: already lying on its side |

Cable holes: screw a PG7 cable gland into each (nut inside); tightening its cap seals round the cable, no silicone needed.
Gasket: print `gasket.stl` in TPU, or lay 1.5 mm foam cord in the rim groove.

### Draft v0.1: check before printing
- **Probe hole** is 22 mm (`PROBE_D`): the probes measure 21.5 mm, plus 0.5 mm clearance.
- **Sensor board** screws onto 4 standoffs (M2.5 x 6 into 2.2 mm pilots), holes 3 mm in from each corner
  (`SB_HOLE_INSET`): checked against the real board.
- **SuperMini** has no holes: USB end under two corner lips, far end under `esp_clamp.stl` with one screw. It rests
  on its two short ends only, so solder the wires straight into its pin holes (no header pins underneath).
- The holder's USB-C port faces into the box with room beside it for a plug, so it charges with the lid off.
