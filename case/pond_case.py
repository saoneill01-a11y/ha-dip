"""
DIP (Depth In Pond) - 3D-printed parts (draft v0.2: box stands upright, glands in the short bottom end,
no charge-port or button holes; charge with the lid off or take the cell out).

Run:  python3 pond_case.py        (needs: pip install manifold3d numpy)
Writes STL files to out/:
  box          electronics box for the pergola post (battery holder, ESP32-C3 SuperMini, sensor board)
  box_lid      gasketed lid with a drip edge
  pipe_cap     sits on top of the 3" PVC stilling pipe, holds the two ultrasonic probes
  pipe_cap_top closes the cap's cable chamber and takes the 1/2" PVC drop rod
  float_bracket  holds the float switch inside the pipe (one M4 screw through the pipe wall)

All sizes in mm. Change a number below and re-run.

Box coordinates (as it hangs upright on the post):
  X = left -> right across the post face
  Y = up from the BOTTOM wall (the short end that faces the ground: the three cable glands)
  Z = out from the post (the floor of the box is against the post; the lid faces you)
"""
import os
import numpy as np
import manifold3d as mf

SEG = 64

# ------------------------------------------------------------------ box
WALL = 3.2          # thicker than BLIPR so the rim can carry a gasket groove
FLOOR = 2.4         # back plate (against the post); same as BLIPR so the holder pads are the same height
IW, ID, IH = 72.0, 140.0, 40.0   # inside width (X), height up the post (Y), depth out from the post (Z)
# IH 40 (was 34): the sensor board's two probe plugs and its 4 jumper wires stand straight up off the board's
# connector side, which faces the lid. 40 leaves about 25 mm above the board even under a lid rib.
R_OUT = 6.0
OW, OD = IW + 2 * WALL, ID + 2 * WALL
x0, y0 = WALL, WALL                # inside origin

# battery holder: the same 4-pad mount as BLIPR's base (Sean's CAD): 25.0 x 94.7 mm hole pattern,
# round pads (8 mm here, 10 on BLIPR), top 7.4 mm above the outside of the floor, 2.9 mm screw holes.
# It stands up the left side. Its USB-C port faces IN (to the right) so a cable plugs in with the lid off;
# the cell lifts straight out of the holder too. No holes in the walls for the port or the button.
HOLD_COLS_X = (4.5, 29.5)          # pad columns (4.5 mm from the left wall, as BLIPR's 4.5 mm wall gap)
HOLD_ROWS_Y = (30.0, 124.7)        # pad rows; the port end of the holder is at the top
PAD_D, PAD_TOP, PAD_HOLE_D = 8.0, 7.4, 2.9   # 8 mm pads (10 hit parts under the holder), 2.9 mm holes (2.8 was too tight)
PORT_FROM_TOP_HOLE = 21.45         # USB-C port centre below the top pad row (measured from BLIPR's base)
PORT_Y = HOLD_ROWS_Y[1] - PORT_FROM_TOP_HOLE
PLUG_ZONE = (34.0, PORT_Y - 9.0, IW, PORT_Y + 12.0)   # kept clear right of the port for the plug and cable

# boards held in drop-in cradles (no screw holes needed): (x, y, w, d, ledge height above floor)
SENSOR_BOARD = (41.0, 12.0, 23.0, 48.0, 7.0)     # JSN-SR20-Y1 driver board, 23 x 48 standing up, plug side toward the lid
# The sensor board screws down onto 4 standoffs (its parts side faces the back plate, so 7 mm clears its button and
# chips). Holes are 3 mm in from each corner (from the seller's photo: MEASURE yours and change SB_HOLE_INSET).
SB_HOLE_INSET = 3.0
SB_POST_D, SB_PILOT_D = 5.5, 2.2   # M2.5 x 6 screws thread straight into the 2.2 mm pilot (same as BLIPR's sensor boards)
SUPERMINI = (43.0, 70.0, 18.0, 22.5, 6.0)        # ESP32-C3 SuperMini, 18 x 22.5 (USB-C at the top)
# The SuperMini has no screw holes: its USB end slides under two corner lips (either side of the USB-C socket),
# then a printed tab (esp_clamp.stl) screws down over its other end with one M2.5 x 6 into a post.
# The board rests on its two short ends only, so wires soldered into the pin holes along its long edges are clear.
SM_CLR, SM_HOOK_IN, SM_LIP_T, SM_REST = 0.4, 3.5, 2.0, 1.5
SM_LIP_OVER = 1.2     # how far each lip reaches over the board's end; it only sticks out from the back wall, so it
                      # prints without supports (no part reaches out sideways past an upright)
SM_POST_R, SM_PILOT_D, SM_TAB_T, SM_TAB_W, SM_TAB_OVER = 3.4, 2.2, 2.0, 12.0, 1.8
CRADLE_WALL, CRADLE_LEDGE, CRADLE_CLR, CRADLE_LIP = 1.8, 1.6, 0.4, 2.0

# cable glands (PG7: 12.5 mm hole) in the bottom end, centred on the wall height
GLANDS_X = (IW / 2 - 17.0, IW / 2, IW / 2 + 17.0)
GLAND_D, GLAND_Z = 12.6, FLOOR + IH / 2
VENT_D, VENT_X, VENT_Z = 2.0, 10.5, FLOOR + IH - 7.0   # tiny breather in the bottom end

# lid screws: M3 heat-set inserts (same as BLIPR) in 8 mm corner columns, given by their inside-corner (x, y)
COL = 8.0
INSERT_D, INSERT_DEPTH, SCREW_CLEAR = 4.1, 7.5, 3.4
COLS = [(0, 0), (IW - COL, 0), (0, ID - COL), (IW - COL, ID - COL)]   # four corners only
# two ribs under the lid keep it flat between the corner screws, so the gasket is squeezed all the way round
RIB_W, RIB_H = 1.8, 5.0
RIBS_X = (IW * 0.30, IW * 0.70)     # run up the box (inside X); clear of the battery (9 mm below) and the plug

# gasket: a printed TPU ring sits in a groove in the box rim and stands 0.5 mm proud; the flat lid squeezes it
# about 25 % (right for 95A TPU). 1.5 mm foam cord in the groove works too.
GROOVE_W, GROOVE_D = 1.8, 1.4
GASKET_W, GASKET_H = 1.6, 1.9
LID_T, LID_LIP, LID_OVER = 3.0, 4.0, 1.6           # lid thickness, drip lip height, overhang past the walls
# "DIP" cut into the lid's front face in BLIPR's lettering (same rounded block letters as BLIPR's lid, scaled up:
# BLIPR's are 12 mm tall with a 2.4 mm stroke; the stroke scales with the height so the letters keep their shape)
NAME_TEXT = "DIP"
NAME_H, NAME_DEPTH = 18.0, 0.6
NAME_STROKE = 2.4 * NAME_H / 12.0
NAME_Y = 0.62                      # letters centred this far up the lid (0 = bottom, 1 = top)

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
TEMP_WIRE_D = 5.0     # DS18B20 probe cable up through the plate
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


def col_hole(cx, cy):
    """Insert hole centre for a column: its middle, nudged 0.8 mm toward any wall it touches."""
    hx = cx + COL / 2 + (-0.8 if cx == 0 else 0.8 if cx == IW - COL else 0)
    hy = cy + COL / 2 + (-0.8 if cy == 0 else 0.8 if cy == ID - COL else 0)
    return X(hx), Y(hy)


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


def supermini_mount():
    """Two corner hooks at the USB end + a screw post at the other end (see SM_* above)."""
    x, y, w, d, lz = SUPERMINI
    c, wall = SM_CLR, 1.8
    bx0, bx1, by0, by1 = X(x), X(x + w), Y(y), Y(y + d)        # board outline
    zb, zt = FLOOR + lz, FLOOR + lz + 1.6                       # board underside / top
    adds, cuts = [], []
    lip0, lip1 = zt + 0.3, zt + 0.3 + SM_LIP_T                  # the lip over the board's top, 0.3 mm play
    for side in (0, 1):                                         # USB-end corner posts, either side of the socket
        if side == 0:
            ox0, ox1, ix0, ix1 = bx0 - c - wall, bx0 - c, bx0 - c, bx0 + SM_HOOK_IN
        else:
            ox0, ox1, ix0, ix1 = bx1 + c, bx1 + c + wall, bx1 - SM_HOOK_IN, bx1 + c
        adds.append(cube(ox0, by1 - 4.0, FLOOR - 0.2, ox1, by1 + c + wall, lip1))          # side wall
        adds.append(cube(min(ox0, ix0), by1 + c, FLOOR - 0.2, max(ox1, ix1), by1 + c + wall, lip1))  # back wall
        adds.append(cube(ix0, by1 - SM_REST, FLOOR - 0.2, ix1, by1 + c + 0.01, zb))       # rest under the corner
        adds.append(cube(ix0, by1 - SM_LIP_OVER, lip0, ix1, by1 + c + 0.01, lip1))        # lip, from the back wall
    # far end: a rest under the board's end + the screw post just beyond it
    cx = (bx0 + bx1) / 2
    py = by0 - c - SM_POST_R
    adds.append(cube(cx - 5.0, by0 - c - 0.5, FLOOR - 0.2, cx + 5.0, by0 + SM_REST, zb))
    adds.append(cyl(zt - FLOOR + 0.2, SM_POST_R, cx, py, FLOOR - 0.2))
    cuts.append(cyl(zt - FLOOR, SM_PILOT_D / 2, cx, py, FLOOR + 1.0, 32))
    return adds, cuts


def esp_clamp():
    """The tab that holds the SuperMini's far end down: one M2.5 x 6 through it into the post. Print flat."""
    c = SM_CLR
    py_to_edge = c + SM_POST_R                                  # post centre to the board's end
    L = SM_POST_R + 1.5 + py_to_edge + SM_TAB_OVER
    tab = rrect(SM_TAB_W, L, 2.0).extrude(SM_TAB_T)
    hole = cyl(SM_TAB_T + 2, 2.9 / 2, SM_TAB_W / 2, SM_POST_R + 1.5, -1, 32)
    return tab - hole


def box():
    H = FLOOR + IH
    shell = rbox(0, 0, 0, OW, OD, H, R_OUT) - rbox(WALL, WALL, FLOOR, IW, ID, IH + 1, R_OUT - WALL)
    adds, cuts = [shell], []
    # ears for the post (top and bottom ends of the back plate), two screw holes each
    for ey in (-EAR_W, OD):
        ay = ey if ey < 0 else OD - R_OUT                     # each ear reaches R_OUT into the box's back plate
        adds.append(rbox(6.0, ay, 0, OW - 12.0, EAR_W + R_OUT, EAR_T, 4.0))
        for ex in (OW * 0.28, OW * 0.72):
            cuts.append(cyl(EAR_T + 2, EAR_HOLE_D / 2, ex, ey + EAR_W / 2, -1))
    # lid screw columns
    for cx, cy in COLS:
        adds.append(cube(X(cx), Y(cy), FLOOR - 0.2, X(cx + COL), Y(cy + COL), H))
        cuts.append(cyl(INSERT_DEPTH + 0.5, INSERT_D / 2, *col_hole(cx, cy), H - INSERT_DEPTH))
    # battery-holder pads
    for px in HOLD_COLS_X:
        for py in HOLD_ROWS_Y:
            adds.append(cyl(PAD_TOP - FLOOR + 0.2, PAD_D / 2, X(px), Y(py), FLOOR - 0.2))
            cuts.append(cyl(PAD_TOP - FLOOR + 1, PAD_HOLE_D / 2, X(px), Y(py), FLOOR))
    # board cradles
    sm_adds, sm_cuts = supermini_mount()
    adds += sm_adds
    cuts += sm_cuts
    # sensor board standoffs
    sx, sy, sw, sd, sz = SENSOR_BOARD
    sb_holes = [(sx + ix, sy + iy) for ix in (SB_HOLE_INSET, sw - SB_HOLE_INSET) for iy in (SB_HOLE_INSET, sd - SB_HOLE_INSET)]
    for hx, hy in sb_holes:
        adds.append(cyl(sz + 0.2, SB_POST_D / 2, X(hx), Y(hy), FLOOR - 0.2))
        cuts.append(cyl(sz, SB_PILOT_D / 2, X(hx), Y(hy), FLOOR + 1.0, 32))
    m = union(adds)
    # bottom-end openings: glands and a breather (no charge port or button holes)
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


def name_shape(cx, cy):
    """NAME_TEXT as a flat outline in BLIPR's rounded block letters, centred on (cx, cy), reading normally
    from the front of the box (X to the right, Y up)."""
    H, sw = NAME_H, NAME_STROKE
    k = H / 12.0                      # BLIPR's letter shapes were drawn 12 mm tall
    r = 3.0 * k

    def box2(u0, v0, u1, v1):
        return mf.CrossSection.square([u1 - u0, v1 - v0]).translate([u0, v0])

    def ring(u0, v0, u1, v1):
        w, h = u1 - u0, v1 - v0
        return (rrect(w, h, r).translate([u0, v0])
                - rrect(w - 2 * sw, h - 2 * sw, max(r - sw, 0.4)).translate([u0 + sw, v0 + sw]))

    stem = box2(0, 0, sw, H)
    glyphs = {                        # (width, outline) per letter, same proportions as BLIPR's B, L, I, P, R
        "D": (8.4 * k, stem + ring(0, 0, 8.4 * k, H)),
        "I": (sw, stem),
        "P": (8.0 * k, stem + ring(0, H * 0.42 - sw / 2, 8.0 * k, H)),
    }
    gap = 2.6 * k
    chosen = [glyphs[ch] for ch in NAME_TEXT]
    total = sum(w for w, _ in chosen) + gap * (len(chosen) - 1)
    out, u = None, cx - total / 2
    for w, shape in chosen:
        g = shape.translate([u, cy - H / 2])
        out = g if out is None else out + g
        u += w + gap
    return out


def box_lid():
    """Printed top-face down. Built here in box coordinates, then flipped onto the bed."""
    H = FLOOR + IH
    o = LID_OVER
    plate = rbox(-o, -o, H, OW + 2 * o, OD + 2 * o, LID_T, R_OUT + o)
    lip = (rbox(-o, -o, H - LID_LIP, OW + 2 * o, OD + 2 * o, LID_LIP + 0.1, R_OUT + o)
           - rbox(-0.3, -0.3, H - LID_LIP - 1, OW + 0.6, OD + 0.6, LID_LIP + 2, R_OUT + 0.3))
    mid = WALL / 2
    m = plate + lip                     # flat underside: it presses the gasket down
    for rx in RIBS_X:                   # stiffening ribs, inside the walls, clear of the gasket
        m = m + cube(X(rx) - RIB_W / 2, Y(COL + 4), H - RIB_H, X(rx) + RIB_W / 2, Y(ID - COL - 4), H + 0.1)
    for cx, cy in COLS:
        hx, hy = col_hole(cx, cy)
        m = m - cyl(LID_T + 2, SCREW_CLEAR / 2, hx, hy, H - 1)
        m = m - cyl(1.2, 3.6, hx, hy, H + LID_T - 1.2)          # seat for a rubber/nylon sealing washer
    # DIP lettering cut into the front face (on the print bed, so the letters come out crisp)
    m = m - name_shape(OW / 2, OD * NAME_Y).extrude(NAME_DEPTH + 1).translate([0, 0, H + LID_T - NAME_DEPTH])
    return m.rotate([180, 0, 0]).translate([0, OD, H + LID_T])


def rim_ring(width):
    """A closed band of the given width running down the middle of the box rim (the groove's centre line)."""
    mid = WALL / 2
    out = rrect(OW - 2 * (mid - width / 2), OD - 2 * (mid - width / 2), R_OUT - mid + width / 2).translate([mid - width / 2, mid - width / 2])
    inn = rrect(OW - 2 * (mid + width / 2), OD - 2 * (mid + width / 2), R_OUT - mid - width / 2).translate([mid + width / 2, mid + width / 2])
    return out - inn


def gasket():
    """TPU gasket for the box rim groove. Print flat as is, 100 % infill, 2 perimeters."""
    return rim_ring(GASKET_W).extrude(GASKET_H)


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
    # water-temperature probe cable up through the plate (clear of the probes and the screw bosses)
    m = m - cyl(PLATE_T + 2, TEMP_WIRE_D / 2, -20, ri - 14, SKIRT_H - 1)
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
        fh.write(b"DIP pond sensor".ljust(80, b" "))
        fh.write(np.uint32(len(f)).tobytes())
        fh.write(data.tobytes())
    return len(f)


PARTS = {"box": box, "box_lid": box_lid, "gasket": gasket, "esp_clamp": esp_clamp, "pipe_cap": pipe_cap, "pipe_cap_top": pipe_cap_top, "float_bracket": float_bracket}

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    for name, fn in PARTS.items():
        m = fn()
        bb = m.bounding_box()
        n = write_stl(m, os.path.join(out, name + ".stl"))
        print("  %-13s %6d triangles, genus %d, size %.1f x %.1f x %.1f mm, status %s" % (
            name, n, m.genus(), bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2], m.status()))
