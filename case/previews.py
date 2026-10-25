"""Preview pictures for the pond parts (with stand-in blocks for the boards and battery so the fit shows)."""
import os, numpy as np, manifold3d as mf
import pond_case as P
from render import views, load_stl
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

def dummy(name, m):
    P.write_stl(m, f"{d}/_dummy_{name}.stl"); return f"{d}/_dummy_{name}.stl"

X, Y, F = P.X, P.Y, P.FLOOR
# battery holder stand-in: board 1.6 thick on the pads, an 18650 (18.5 dia) along it
hx0, hx1 = X(P.HOLD_X0 - 6.3), X(P.HOLD_X0 + P.HOLD_PITCH_X + 9.0)
hy0, hy1 = Y(0.3), Y(P.HOLD_Y0 + P.HOLD_PITCH_Y + 4.5)
holder = P.cube(hx0, hy0, P.PAD_TOP, hx1, hy1, P.PAD_TOP + 1.6)
cell = mf.Manifold.cylinder(65.0, 9.25, 9.25, 48).rotate([0, 90, 0]).translate([X(P.HOLD_X0 + 15), (hy0 + hy1) / 2, P.PAD_TOP + 1.6 + 9.6])
holder_p = dummy("holder", holder + cell)
sx, sy, sw, sd, sz = P.SENSOR_BOARD
sensor_p = dummy("sensor", P.cube(X(sx), Y(sy), F + sz, X(sx + sw), Y(sy + sd), F + sz + 1.6) + P.cube(X(sx + 18), Y(sy + 1), F + sz - 6, X(sx + 28), Y(sy + 4), F + sz))
mx, my, mw, md, mz = P.SUPERMINI
mini_p = dummy("mini", P.cube(X(mx), Y(my), F + mz, X(mx + mw), Y(my + md), F + mz + 1.6) + P.cube(X(mx + mw - 7), Y(my + 5), F + mz + 1.6, X(mx + mw + 1), Y(my + 13), F + mz + 4.8))

grey, blue, green, amber = (0.70, 0.73, 0.78), (0.30, 0.50, 0.85), (0.35, 0.65, 0.40), (0.85, 0.62, 0.25)
views([f"{d}/box.stl", holder_p, sensor_p, mini_p], f"{d}/preview_box.png",
      [(55, -60, "Box, lid off (battery holder, sensor board, ESP32)"), (-25, -20, "Bottom wall: charge port, button, 3 glands")],
      colors=[grey, amber, blue, green], size=(13, 5.2))
views([f"{d}/box_lid.stl"], f"{d}/preview_lid.png", [(-45, -60, "Lid (top), washer seats round the screws"), (40, -60, "Lid underside as printed: gasket tongue, drip lip")], size=(11, 4.4))
off = [None, (0, 0, 70), (120, 0, 0)]
views([f"{d}/pipe_cap.stl", f"{d}/pipe_cap_top.stl", f"{d}/float_bracket.stl"], f"{d}/preview_pipe.png",
      [(25, -50, "Pipe cap, cap top + rod socket, float bracket"), (-55, -50, "Underneath: the two probe holes")],
      colors=[grey, (0.62, 0.66, 0.74), amber], offsets=off, size=(12, 5.2))
print("ok")
