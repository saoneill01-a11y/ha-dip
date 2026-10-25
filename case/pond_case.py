"""
Pond water-level sensor - 3D-printed parts (draft v0.1).

Run:  python3 pond_case.py        (needs: pip install manifold3d numpy)
Writes STL files to out/:
  box          electronics box for the pergola post (battery holder, ESP32-C3 SuperMini, sensor board)
  box_lid      gasketed lid with a drip edge
  pipe_cap     sits on top of the 3" PVC stilling pipe, holds the two ultrasonic probes
  pipe_cap_top closes the cap's cable chamber and takes the 1/2" PVC drop rod
  float_bracket  holds the float switch inside the pipe (one M4 screw through the pipe wall)

All sizes in mm. Change a number below and re-run.

Box coordinates (as it hangs on the post):
  X = left -> right along the post face
  Y = up from the BOTTOM wall (the bottom wall faces the ground: cable glands, charge port, power button)
  Z = out from the post (the floor of the box is against the post; the lid faces you)
"""
import os
import numpy as np
import manifold3d as mf

SEG = 64

# ------------------------------------------------------------------ box
WALL = 3.2          # thicker than BLIPR so the rim can carry a gasket groove
FLOOR = 2.4         # back plate (against the post); same as BLIPR so the holder pads are the same height
IW, ID, IH = 186.0, 68.0, 34.0   # inside width (X), depth (Y, bottom -> top), height (Z)
R_OUT = 6.0
OW, OD = IW + 2 * WALL, ID + 2 * WALL
x0, y0 = WALL, WALL                # inside origin

# battery holder: the same 4-pad mount as BLIPR's base (Sean's CAD): 25.0 x 94.7 mm hole pattern,
# 10 mm round pads, top 7.4 mm above the outside of the floor, 2.8 mm screw holes.
# The holder's charge port and power button face the bottom wall (down = rain can't fall in).
HOLD_X0 = 16.0                     # first pad hole, X (inside coords)
HOLD_PITCH_X, HOLD_PITCH_Y = 94.7, 25.0
HOLD_Y0 = 4.5                      # pad row nearest the bottom wall (same 4.5 mm as BLIPR's wall gap)
PAD_D, PAD_TOP, PAD_HOLE_D = 10.0, 7.4, 2.8
# openings for the holder, measured from BLIPR's base (relative to the first pad hole)
PORT_DX, PORT_W, PORT_Z0, PORT_Z1 = 21.45, 14.5, 2.4, 10.9      # charge port
BTN_DX, BTN_W, BTN_H, BTN_Z = 85.95, 14.0, 10.0, 11.9           # holder power button slot

# boards held in drop-in cradles (no screw holes needed): (x, y, w, d, ledge height above floor)
SENSOR_BOARD = (20.0, 40.0, 48.0, 23.0, 8.0)     # JSN-SR20-Y1 driver board, 48 x 23
SUPERMINI = (82.0, 42.0, 22.5, 18.0, 6.0)        # ESP32-C3 SuperMini, 22.5 x 18 (USB-C toward +X)
CRADLE_WALL, CRADLE_LEDGE, CRADLE_CLR, CRADLE_LIP = 1.8, 1.6, 0.4, 2.0

# cable glands (PG7: 12.5 mm hole) in the bottom wall, centred on the wall height
GLANDS_X = (135.0, 152.0, 169.0)
GLAND_D, GLAND_Z = 12.6, 17.0
VENT_D, VENT_X, VENT_Z = 2.0, 125.0, 28.0         # tiny breather in the bottom wall

# lid screws: M3 heat-set inserts (same as BLIPR) in corner columns + 2 on the top wall
COL = 8.0
INSERT_D, INSERT_DEPTH, SCREW_CLEAR = 4.1, 7.5, 3.4
MID_COLS_X = (IW / 3, 2 * IW / 3)

# gasket: groove in the box rim, tongue under the lid (print the gasket in TPU, or lay 1.5 mm foam cord)
GROOVE_W, GROOVE_D = 1.8, 1.4
TONGUE_W, TONGUE_H = 1.0, 0.9
LID_T, LID_LIP, LID_OVER = 3.0, 4.0, 1.6           # lid thickness, drip lip height, overhang past the walls

# post-mount ears on the back plate
EAR_W, EAR_T, EAR_HOLE_D = 16.0, 4.0, 5.2

# ------------------------------------------------------------------ pipe cap
PIPE_OD = 88.9        # 3" schedule 40 PVC outside diameter
PIPE_ID = 77.9        # inside diameter (for the float bracket's curved back)
CAP_CLR = 0.8         # diameter clearance over the pipe
CAP_WALL = 3.0
SKIRT_H = 28.0        # how far the cap slides down over the pipe
PLATE_T = 4.0
PROBE_D = 18.6        # PROBE HOLE: measure your probe body and change this (probes push up from below)
PROBE_SPACING = 44.0  # centre to centre
CHAMBER_H = 26.0      # space above the plate for the probe backs and cables
FLOAT_WIRE_D = 5.0
ROD_OD = 21.3         # 1/2" schedule 40 PVC outside diameter (EMT 1/2" is 17.9: change it)
ROD_CLR, ROD_DEPTH, ROD_BOSS_WALL = 0.5, 32.0, 3.5
CAP_SCREW_R = 0.0     # set below

# ------------------------------------------------------------------ float bracket
FLOAT_STEM_HOLE = 10.6   # M10 stem
FLOAT_OFFSET = 19.0      # stem centre from the pipe wall (float body is about 24 mm across)
FB_W, FB_H, FB_T = 32.0, 42.0, 4.0
SHELF_T = 5.0
M4_CLEAR = 4.4


def cube(x0_, y0_, z0_, x1, y1, z1):
    return mf.Manifold.cube([x1 - x0_, y1 - y0_, z1 - z0_]).translate([x0_, y0_, z0_])


def cyl(h, r, x=0.0, y=0.0, z=0.0, seg=SEG):
    return mf.Manifold.cylinder(h, r, r, seg).translate([x, y, z])


def rrect(w, d, r):
    r = max(min(r, w / 2 - 0.01, d / 2 - 0.01), 0.01)
    pts = [mf.CrossSection.circle(r, SEG).translate([cx, cy]) for cx in (r, w - r) for cy in (r, d - r)]
    return mf.CrossSection.batch_hull(pts)


def rbox(x, y, z, w, d, h, r):
    return rrect(w, d, r).extrude(h).translate([x, y, z])


def union(parts):
    return mf.Manifold.batch_boolean(parts, mf.OpType.Add)


def X(v): return x0 + v
def Y(v): return y0 + v


def cradle(x, y, w, d, ledge_z):
    """Four corner brackets: the board drops in, rests on a ledge and is held at its edges."""
    cw, cl = CRADLE_WALL, CRADLE_CLR
    ox0, oy0 = X(x) - cl - cw, Y(y) - cl - cw
    ox1, oy1 = X(x + w) + cl + cw, Y(y + d) + cl + cw
    top = FLOOR + ledge_z + 1.6 + CRADLE_LIP          # board 1.6 mm + lip
    body = cube(ox0, oy0, FLOOR - 0.2, ox1, oy1, top)
    pocket = cube(X(x) - cl, Y(y) - cl, FLOOR + ledge_z, X(x + w) + cl, Y(y + d) + cl, top + 1)
    under = cube(X(x) + CRADLE_LEDGE, Y(y) + CRADLE_LEDGE, FLOOR, X(x + w) - CRADLE_LEDGE, Y(y + d) - CRADLE_LEDGE, top + 1)
    m = body - pocket - under
    # keep only the corners: cut the middle of each side away
    kx, ky = min(9.0, w / 3), min(9.0, d / 3)
    m = m - cube(X(x) + kx, oy0 - 1, FLOOR, X(x + w) - kx, oy1 + 1, top + 1)
    m = m - cube(ox0 - 1, Y(y) + ky, FLOOR, ox1 + 1, Y(y + d) - ky, top + 1)
    return m


def box():
    H = FLOOR + IH
    shell = rbox(0, 0, 0, OW, OD, H, R_OUT) - rbox(WALL, WALL, FLOOR, IW, ID, IH + 1, R_OUT - WALL)
    adds, cuts = [shell], []
    # ears for the post (left and right ends of the back plate)
    for ex in (-EAR_W, OW):
        ax = ex if ex < 0 else OW - R_OUT                     # each ear reaches R_OUT into the box's back plate
        adds.append(rbox(ax, 6.0, 0, EAR_W + R_OUT, OD - 12.0, EAR_T, 4.0))
        for ey in (OD * 0.25, OD * 0.75):
            cuts.append(cyl(EAR_T + 2, EAR_HOLE_D / 2, ex + EAR_W / 2, ey, -1))
    # lid screw columns
    cols = [(0, 0), (IW - COL, 0), (0, ID - COL), (IW - COL, ID - COL)] + [(mx - COL / 2, ID - COL) for mx in MID_COLS_X]
    for cx, cy in cols:
        adds.append(cube(X(cx), Y(cy), FLOOR - 0.2, X(cx + COL), Y(cy + COL), H))
        hx = X(cx + COL / 2 + (-0.8 if cx == 0 else 0.8 if cx == IW - COL else 0))
        hy = Y(cy + COL / 2 + (-0.8 if cy == 0 else 0.8))
        cuts.append(cyl(INSERT_DEPTH + 0.5, INSERT_D / 2, hx, hy, H - INSERT_DEPTH))
    # battery-holder pads
    for i in range(2):
        for j in range(2):
            px, py = X(HOLD_X0 + i * HOLD_PITCH_X), Y(HOLD_Y0 + j * HOLD_PITCH_Y)
            adds.append(cyl(PAD_TOP - FLOOR + 0.2, PAD_D / 2, px, py, FLOOR - 0.2))
            cuts.append(cyl(PAD_TOP - FLOOR + 1, PAD_HOLE_D / 2, px, py, FLOOR))
    # board cradles
    for b in (SENSOR_BOARD, SUPERMINI):
        adds.append(cradle(*b))
    m = union(adds)
    # bottom-wall openings: charge port, power-button slot, glands, vent
    px = X(HOLD_X0 + PORT_DX)
    cuts.append(cube(px - PORT_W / 2, -1, PORT_Z0, px + PORT_W / 2, WALL + 1, PORT_Z1))
    bx = X(HOLD_X0 + BTN_DX)
    slot = rrect(BTN_W, BTN_H, BTN_H / 2).extrude(WALL + 2).rotate([-90, 0, 0])
    cuts.append(slot.translate([bx - BTN_W / 2, -1, BTN_Z + BTN_H / 2]))
    for gx in GLANDS_X:
        cuts.append(cyl(WALL + 2, GLAND_D / 2, 0, 0, 0).rotate([-90, 0, 0]).translate([X(gx), -1, GLAND_Z]))
    cuts.append(cyl(WALL + 2, VENT_D / 2, 0, 0, 0, 24).rotate([-90, 0, 0]).translate([X(VENT_X), -1, VENT_Z]))
    # gasket groove, centred in the rim
    mid = WALL / 2
    ring = (rrect(OW - 2 * (mid - GROOVE_W / 2), OD - 2 * (mid - GROOVE_W / 2), R_OUT - mid + GROOVE_W / 2)
            .translate([mid - GROOVE_W / 2, mid - GROOVE_W / 2]))
    inner = (rrect(OW - 2 * (mid + GROOVE_W / 2), OD - 2 * (mid + GROOVE_W / 2), R_OUT - mid - GROOVE_W / 2)
             .translate([mid + GROOVE_W / 2, mid + GROOVE_W / 2]))
    cuts.append((ring - inner).extrude(GROOVE_D + 1).translate([0, 0, H - GROOVE_D]))
    return m - union(cuts)


def box_lid():
    """Printed top-face down. Built here in box coordinates, then flipped onto the bed."""
    H = FLOOR + IH
    o = LID_OVER
    plate = rbox(-o, -o, H, OW + 2 * o, OD + 2 * o, LID_T, R_OUT + o)
    lip = (rbox(-o, -o, H - LID_LIP, OW + 2 * o, OD + 2 * o, LID_LIP + 0.1, R_OUT + o)
           - rbox(-0.3, -0.3, H - LID_LIP - 1, OW + 0.6, OD + 0.6, LID_LIP + 2, R_OUT + 0.3))
    mid = WALL / 2
    t_out = (rrect(OW - 2 * (mid - TONGUE_W / 2), OD - 2 * (mid - TONGUE_W / 2), R_OUT - mid + TONGUE_W / 2)
             .translate([mid - TONGUE_W / 2, mid - TONGUE_W / 2]))
    t_in = (rrect(OW - 2 * (mid + TONGUE_W / 2), OD - 2 * (mid + TONGUE_W / 2), R_OUT - mid - TONGUE_W / 2)
            .translate([mid + TONGUE_W / 2, mid + TONGUE_W / 2]))
    tongue = (t_out - t_in).extrude(TONGUE_H + 0.1).translate([0, 0, H - TONGUE_H])
    m = plate + lip + tongue
    cols = [(0, 0), (IW - COL, 0), (0, ID - COL), (IW - COL, ID - COL)] + [(mx - COL / 2, ID - COL) for mx in MID_COLS_X]
    for cx, cy in cols:
        hx = X(cx + COL / 2 + (-0.8 if cx == 0 else 0.8 if cx == IW - COL else 0))
        hy = Y(cy + COL / 2 + (-0.8 if cy == 0 else 0.8))
        m = m - cyl(LID_T + 2, SCREW_CLEAR / 2, hx, hy, H - 1)
        m = m - cyl(1.2, 3.6, hx, hy, H + LID_T - 1.2)          # seat for a rubber/nylon sealing washer
    return m.rotate([180, 0, 0]).translate([0, OD, H + LID_T])


def pipe_cap():
    ri = (PIPE_OD + CAP_CLR) / 2
    ro = ri + CAP_WALL
    total = SKIRT_H + PLATE_T + CHAMBER_H
    m = cyl(total, ro) - cyl(SKIRT_H + 0.01, ri, z=-0.01) - cyl(CHAMBER_H + 1, ri, z=SKIRT_H + PLATE_T)
    # probe holes (probes push up from below and are held by their own nut/flange or a dab of silicone)
    for sx in (-PROBE_SPACING / 2, PROBE_SPACING / 2):
        m = m - cyl(PLATE_T + 2, PROBE_D / 2, sx, 0, SKIRT_H - 1)
    # float-switch wire up through the plate
    m = m - cyl(PLATE_T + 2, FLOAT_WIRE_D / 2, 0, -ri + 10, SKIRT_H - 1)
    # air vent in the skirt (so the water inside can rise and fall)
    m = m - cyl(10, 1.6, 0, 0, 0).rotate([90, 0, 0]).translate([0, -ri + 1, SKIRT_H - 6])
    # three screw bosses inside the chamber for the top
    global CAP_SCREW_R
    CAP_SCREW_R = ri - 4.5
    for a in (90, 210, 330):
        bx, by = CAP_SCREW_R * np.cos(np.radians(a)), CAP_SCREW_R * np.sin(np.radians(a))
        boss = cyl(CHAMBER_H, 5.0, bx, by, SKIRT_H + PLATE_T - 0.1) ^ cyl(CHAMBER_H, ri + 0.5, 0, 0, SKIRT_H)
        m = m + boss
        m = m - cyl(INSERT_DEPTH + 0.5, INSERT_D / 2, bx, by, total - INSERT_DEPTH)
    return m


def pipe_cap_top():
    ri = (PIPE_OD + CAP_CLR) / 2
    ro = ri + CAP_WALL
    t = 4.0
    plug = cyl(2.0, ri - 0.3, z=-2.0) - cyl(4, ri - 3.3, z=-3)         # plug ring locates it in the chamber
    for a in (90, 210, 330):                                           # notched round the screw bosses
        plug = plug - cyl(4, 5.6, (ri - 4.5) * np.cos(np.radians(a)), (ri - 4.5) * np.sin(np.radians(a)), -3)
    m = cyl(t, ro) + plug
    br = ROD_OD / 2 + ROD_CLR / 2 + ROD_BOSS_WALL
    m = m + cyl(ROD_DEPTH + t, br) + cyl(10, br + 6)                  # socket boss + a stiff collar at its foot
    m = m - cyl(ROD_DEPTH + 1, ROD_OD / 2 + ROD_CLR / 2, 0, 0, t)     # rod socket
    m = m - cyl(t + 4, 7.0, 0, 0, -3)                                   # cables pass up into the rod
    # set screw (M4) across the socket
    m = m - cyl(br + 2, M4_CLEAR / 2 - 0.6, 0, 0, 0).rotate([0, 90, 0]).translate([0, 0, t + ROD_DEPTH * 0.6])
    for a in (90, 210, 330):
        bx, by = CAP_SCREW_R * np.cos(np.radians(a)), CAP_SCREW_R * np.sin(np.radians(a))
        m = m - cyl(t + 6, SCREW_CLEAR / 2, bx, by, -3)
    return m


def float_bracket():
    """Curved back fits the pipe's inside wall; the float stem goes through the shelf, float hanging below."""
    r = PIPE_ID / 2
    back = (cyl(FB_H, r, 0, 0, 0, 160) - cyl(FB_H + 2, r - FB_T, 0, 0, -1, 160)) ^ cube(-FB_W / 2, -r - 1, 0, FB_W / 2, -r + 10, FB_H)
    shelf = cube(-FB_W / 2, -r + FB_T - 0.5, FB_H - SHELF_T, FB_W / 2, -r + FLOAT_OFFSET + 12, FB_H) ^ cyl(FB_H, r - 0.5, 0, 0, 0, 160)
    gusset = mf.Manifold.hull(cube(-1.5, -r + FB_T - 0.5, FB_H - SHELF_T, 1.5, -r + FLOAT_OFFSET + 6, FB_H - SHELF_T + 0.1)
                              + cube(-1.5, -r + FB_T - 0.5, FB_H * 0.35, 1.5, -r + FB_T + 0.5, FB_H - SHELF_T))
    m = back + shelf + gusset
    m = m - cyl(SHELF_T + 2, FLOAT_STEM_HOLE / 2, 0, -r + FLOAT_OFFSET, FB_H - SHELF_T - 1)
    m = m - cyl(20, M4_CLEAR / 2, 0, 0, 0).rotate([90, 0, 0]).translate([-FB_W / 4, -r + 12, FB_H * 0.3])
    m = m - cyl(20, M4_CLEAR / 2, 0, 0, 0).rotate([90, 0, 0]).translate([FB_W / 4, -r + 12, FB_H * 0.3])
    # print standing on its shelf's top face: flip so the shelf top is on the bed
    return m.rotate([180, 0, 0]).translate([0, 0, FB_H])


def write_stl(m, path):
    mesh = m.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3].astype(np.float32)
    f = np.asarray(mesh.tri_verts)
    tri = v[f]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    data = np.zeros(len(f), dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    data["n"], data["v"] = n, tri.reshape(-1, 9)
    with open(path, "wb") as fh:
        fh.write(b"pond sensor".ljust(80, b" "))
        fh.write(np.uint32(len(f)).tobytes())
        fh.write(data.tobytes())
    return len(f)


PARTS = {"box": box, "box_lid": box_lid, "pipe_cap": pipe_cap, "pipe_cap_top": pipe_cap_top, "float_bracket": float_bracket}

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    for name, fn in PARTS.items():
        m = fn()
        bb = m.bounding_box()
        n = write_stl(m, os.path.join(out, name + ".stl"))
        print("  %-13s %6d triangles, genus %d, size %.1f x %.1f x %.1f mm, status %s" % (
            name, n, m.genus(), bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2], m.status()))
