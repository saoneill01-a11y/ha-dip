# Pond sensor: notes for Claude

Sean's battery-powered pond water-level sensor for Home Assistant (see README.md). Sean is a network engineer
and target shooter, not a programmer: explain things plainly, keep answers short, show a render or mockup
before anything gets printed or built, and ask before anything that costs money or can't be undone.

- `case/pond_case.py` builds every printed part (numbers at the top); `case/previews.py` renders previews.
- The battery-holder mount and its port/button openings copy BLIPR's base
  (saoneill01-a11y/rangebook-blipr, `case/user_edits/base_from_sean_2026-10-22.stl`): keep them in step.
- Firmware will be ESPHome (deep sleep, 20 min wake, float switch as a wake pin), added later.
- Commit as Sean; push to `main` after each piece of work.
