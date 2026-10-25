# Pond sensor

A battery-powered water-level sensor for the pond, reporting to Home Assistant over Wi-Fi.

- **Level:** a JSN-SR20-Y1 ultrasonic sensor looks down a 3" PVC "stilling pipe" standing in the pond, so the
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
| JSN-SR20-Y1 ultrasonic sensor (dual probes, 48 x 23 mm board) | ordered |
| Mini vertical float switch (PP, M10 stem) | 16" leads: extend with outdoor 2-core cable, solder + adhesive-lined heat shrink |
| Resistors | 360 kOhm (sensor low-power mode), 2 x 100 kOhm (battery voltage reading) |
| 3" PVC pipe, about 30" long | on hand. 3-4 x 1/4" holes in the bottom 2-3", one 1/8" vent near the top |
| 1/2" PVC drop rod from the pergola beam | about 7 ft; measure in place |
| 3 x PG7 cable glands | on hand |
| M3 heat-set inserts, M3 screws + rubber washers, 2 x M4 screws/nuts | |

## Printed parts (`case/`)

`python3 case/pond_case.py` builds every part into `case/out/` (needs `pip install manifold3d numpy`).
`python3 case/previews.py` draws the preview pictures.

| File | What | Print |
|---|---|---|
| `box.stl` | electronics box, stands upright on the pergola post (about 3" x 5.75" x 1.5"): BLIPR's battery-holder mount, cradles for the sensor board and SuperMini, 3 glands in the bottom end. No charge-port or button holes: charge through the holder's USB-C with the lid off, or take the cell out | as is, back plate down. PETG or ASA |
| `box_lid.stl` | flat-bottomed lid with a drip edge and washer seats round the 6 screws | as is (already flipped) |
| `gasket.stl` | TPU ring for the rim groove: 1.6 wide x 1.9 tall, stands 0.5 mm proud so the lid squeezes it about 25 % | 95A TPU, flat, 100 % infill |
| `pipe_cap.stl` | slides over the 3" pipe, holds both probes, cable chamber above | as is |
| `pipe_cap_top.stl` | closes the chamber, socket for the 1/2" rod (M4 set screw) | as is |
| `float_bracket.stl` | holds the float switch inside the pipe | as is |

Cable holes: screw a PG7 cable gland into each (nut inside); tightening its cap seals round the cable, no silicone needed.
Gasket: print `gasket.stl` in TPU, or lay 1.5 mm foam cord in the rim groove.

### Draft v0.1: check before printing
- **Probe hole** is a guess (18.6 mm, `PROBE_D`): measure the probes when they arrive.
- **Rod** assumes 1/2" schedule 40 PVC (21.3 mm OD, `ROD_OD`); 1/2" EMT is 17.9.
- **Sensor board and SuperMini** sit in edge cradles, so their hole positions don't matter.
- The holder's USB-C port faces into the box with room beside it for a plug, so it charges with the lid off.
