# Pond sensor: notes for Claude

Sean's battery-powered pond water-level sensor for Home Assistant (see README.md). Sean is a network engineer
and target shooter, not a programmer: explain things plainly, keep answers short, show a render or mockup
before anything gets printed or built, and ask before anything that costs money or can't be undone.

- `case/pond_case.py` builds every printed part (numbers at the top); `case/previews.py` renders previews.
- The battery-holder mount copies BLIPR's base (saoneill01-a11y/rangebook-blipr,
  `case/user_edits/base_from_sean_2026-10-22.stl`). The box has no charge-port or button holes: the holder's
  USB-C faces into the box and Sean charges it with the lid off (keep the plug clearance, `PLUG_ZONE`).
- Firmware will be ESPHome (deep sleep, 20 min wake, float switch as a wake pin), added later.
- Commit as Sean; push to `main` after each piece of work.
