"""Preview pictures for the pond parts (with stand-in blocks for the boards, battery and a USB-C plug so the fit shows)."""
import os, numpy as np, manifold3d as mf
import pond_case as P
from render import views
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def dummy(name, m):
    P.write_stl(m, f"{d}/_dummy_{name}.stl")
    return f"{d}/_dummy_{name}.stl"


X, Y, F = P.X, P.Y, P.FLOOR
# battery holder stand-in: board 1.6 thick on the pads (port end at the top), an 18650 (18.5 dia) along it
hx0, hx1 = X(0.4), X(P.HOLD_COLS_X[1] + 4.5)
hy0, hy1 = Y(P.HOLD_ROWS_Y[0] - 13.0), Y(P.HOLD_ROWS_Y[1] + 6.3)
holder = P.cube(hx0, hy0, P.PAD_TOP, hx1, hy1, P.PAD_TOP + 1.6)
cell = mf.Manifold.cylinder(65.0, 9.25, 9.25, 48).rotate([-90, 0, 0]).translate([(hx0 + hx1) / 2, Y(P.HOLD_ROWS_Y[0]), P.PAD_TOP + 1.6 + 9.6])
port = P.cube(hx1 - 7.0, Y(P.PORT_Y) - 4.5, P.PAD_TOP - 1.6, hx1 + 0.3, Y(P.PORT_Y) + 4.5, P.PAD_TOP + 1.6)
holder_p = dummy("holder", holder + cell + port)
# a USB-C plug and cable plugged in from the right (shows the clearance with the lid off)
plug = (P.cube(hx1 + 0.3, Y(P.PORT_Y) - 4.2, P.PAD_TOP - 1.4, hx1 + 22, Y(P.PORT_Y) + 4.2, P.PAD_TOP + 5.0)
        + mf.Manifold.cylinder(14, 2.2, 2.2, 24).rotate([0, 90, 0]).translate([hx1 + 22, Y(P.PORT_Y), P.PAD_TOP + 1.8])
        + mf.Manifold.cylinder(30, 2.2, 2.2, 24).translate([hx1 + 36, Y(P.PORT_Y), P.PAD_TOP + 1.8]))
plug_p = dummy("plug", plug)
sx, sy, sw, sd, sz = P.SENSOR_BOARD
bz = F + sz + 1.6                       # top of the sensor board (its plug side faces the lid)
plugs = None
for py in (sy + 10.0, sy + sd - 10.0):  # the two probe plugs (JST XH, 2-pin) standing up, cable bent toward the glands
    cx, cy = X(sx + sw / 2), Y(py)
    p = (P.cube(cx - 3.0, cy - 2.6, bz, cx + 3.0, cy + 2.6, bz + 11.0)
         + mf.Manifold.cylinder(8.0, 1.7, 1.7, 16).translate([cx, cy, bz + 11.0])
         + mf.Manifold.cylinder(30.0, 1.7, 1.7, 16).rotate([90, 0, 0]).translate([cx, cy, bz + 19.0]))
    plugs = p if plugs is None else plugs + p
hx = X(sx) + 1.5                        # the 4 jumper wires on the header, standing up then bending down
plugs = plugs + P.cube(hx - 1.3, Y(sy + sd / 2) - 5.2, bz, hx + 1.3, Y(sy + sd / 2) + 5.2, bz + 16.0)
sensor_p = dummy("sensor", P.cube(X(sx), Y(sy), F + sz, X(sx + sw), Y(sy + sd), F + sz + 1.6) + plugs)
mx, my, mw, md, mz = P.SUPERMINI
mini_p = dummy("mini", P.cube(X(mx), Y(my), F + mz, X(mx + mw), Y(my + md), F + mz + 1.6)
               + P.cube(X(mx + 5), Y(my + md - 7), F + mz + 1.6, X(mx + 13), Y(my + md + 1), F + mz + 4.8))

grey, blue, green, amber, dark = (0.70, 0.73, 0.78), (0.30, 0.50, 0.85), (0.35, 0.65, 0.40), (0.85, 0.62, 0.25), (0.25, 0.25, 0.28)
views([f"{d}/box.stl", holder_p, sensor_p, mini_p, plug_p], f"{d}/preview_box.png",
      [(60, -30, "Box upright, lid off (USB-C cable plugged in)"), (-20, -35, "Bottom end: 3 cable glands")],
      colors=[grey, amber, blue, green, dark], size=(12, 6.4))
views([f"{d}/box_lid.stl", f"{d}/gasket.stl"], f"{d}/preview_lid.png",
      [(-45, -60, "Lid (top), washer seats round the 4 screws"), (40, -60, "Lid underside as printed: 2 stiffening ribs, drip lip + TPU gasket")], colors=[grey, (0.2, 0.2, 0.22)], offsets=[None, (100, 0, 0)], size=(12, 4.8))
# the box closed up as it hangs on the post (lid turned back over), to show the lettering
H_TOP = P.FLOOR + P.IH + P.LID_T
lid_on = P.box_lid().translate([0, -P.OD, -H_TOP]).rotate([180, 0, 0])
P.write_stl(lid_on, f"{d}/_dummy_lid_on.stl")
views([f"{d}/box.stl", f"{d}/_dummy_lid_on.stl"], f"{d}/preview_front.png",
      [(62, -18, "On the post, lid on (DIP in BLIPR's lettering)")], colors=[grey, (0.80, 0.82, 0.86)], size=(6.5, 6.4))
off = [None, (0, 0, 70), (120, 0, 0)]
views([f"{d}/pipe_cap.stl", f"{d}/pipe_cap_top.stl", f"{d}/float_bracket.stl"], f"{d}/preview_pipe.png",
      [(25, -50, "Pipe cap, cap top + rod socket, float bracket"), (-55, -50, "Underneath: the two probe holes")],
      colors=[grey, (0.62, 0.66, 0.74), amber], offsets=off, size=(12, 5.2))
for f in os.listdir(d):
    if f.startswith("_dummy_"):
        os.remove(os.path.join(d, f))
print("ok")
