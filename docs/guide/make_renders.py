"""Part renders for the DIP assembly guide. Run after case/pond_case.py: python make_renders.py"""
import os, sys
here = os.path.dirname(os.path.abspath(__file__))
case = os.path.join(here, "..", "..", "case")
sys.path.insert(0, case)
from render import views
o = os.path.join(case, "out")
g, a, dk = (0.70, 0.73, 0.78), (0.85, 0.62, 0.25), (0.25, 0.25, 0.28)
parts = [
    ("box.stl", [(60, -30, "Box, open side up"), (-20, -35, "Bottom end: 3 gland holes")], (11, 5)),
    ("box_lid.stl", [(-45, -60, "Lid, outside"), (40, -60, "Lid, inside")], (11, 4.6)),
    ("esp_clamp.stl", [(45, -40, "SuperMini clamp tab")], (5, 4)),
    ("gasket.stl", [(60, -30, "Gasket (TPU)")], (5, 4)),
    ("pipe_cap.stl", [(25, -50, "Pipe cap, top side (cable slot at left)"), (-55, -50, "Underneath: the two probe holes")], (11, 5)),
    ("pipe_cap_top.stl", [(40, -40, "Pipe cap top")], (5, 4)),
    ("float_bracket.stl", [(30, -40, "Float bracket")], (5, 4)),
]
for f, v, size in parts:
    views([os.path.join(o, f)], os.path.join(here, "r_" + f.replace(".stl", ".png")), v, colors=[a if "float" in f else g], size=size)
print("ok")
