"""
DIP (Depth In Pond) - 3D-printed parts (v0.4: XIAO ESP32-C6 and a plain 18650 holder; box stands upright, glands in the short bottom end,
no charge-port holes; charge with the lid off through the XIAO, or take the cell out).

Run:  python3 pond_case.py        (needs: pip install manifold3d numpy)
Writes STL files to out/:
  box          electronics box that hangs on a post (18650 holder, XIAO ESP32-C6, sensor board)
  box_lid      gasketed lid with a drip edge
  pipe_cap     sits on top of the 3" PVC stilling pipe, holds the two ultrasonic probes
  pipe_cap_top closes the cap's cable chamber; the cables leave sideways through a slot in the cap's rim
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
WALL = 3.2          # thick enough for the rim to carry a gasket groove
FLOOR = 2.4         # back plate (against the post)
IW, ID, IH = 72.0, 140.0, 40.0   # inside width (X), height up the post (Y), depth out from the post (Z)
# IH 40 (was 34): the sensor board's two probe plugs and its 4 jumper wires stand straight up off the board's
# connector side, which faces the lid. 40 leaves about 25 mm above the board even under a lid rib.
R_OUT = 6.0
OW, OD = IW + 2 * WALL, ID + 2 * WALL
x0, y0 = WALL, WALL                # inside origin

# battery holder: a plain single-18650 holder with wire leads, 76.2 x 21.2 x 20 mm, one hole in the middle of its
# floor. It stands up the left side on a platform; one M3 screw through that hole into a heat-set insert in the
# platform holds it, and a low rail along its right side stops it turning. Its ends stay open for the wires.
HOLDER = (1.0, 30.0, 21.2, 76.2, 20.0)   # x, y, width, length, height of the holder
PLAT_H = 7.0                       # platform top above the floor: room for the 5.7 mm insert under the holder
PLAT_INSET = 1.0                   # platform stops this far short of the holder's ends (wire room)
RAIL_W, RAIL_H, RAIL_CLR = 1.8, 4.0, 0.4   # locating rail beside the holder, above the platform
HOLDER_INSERT_D, HOLDER_INSERT_DEPTH = 4.1, 6.0

# boards held in drop-in cradles (no screw holes needed): (x, y, w, d, ledge height above floor)
SENSOR_BOARD = (48.0, 14.0, 23.0, 48.0, 7.0)     # JSN-SR20-Y1 driver board, 23 x 48 standing up, plug side toward the lid
# v0.3 (Oct 31, 2026): moved 7 mm right (against the right wall) and 2 mm up so its wire plugs clear the battery
# holder's lower pad. It can't go higher: the SuperMini's screw post is 0.8 mm above its top edge.
# The sensor board screws down onto 4 standoffs (its parts side faces the back plate, so 7 mm clears its button and
# chips). Holes are 3 mm in from each corner (from the seller's photo: MEASURE yours and change SB_HOLE_INSET).
SB_HOLE_INSET = 3.0
SB_POST_D, SB_PILOT_D = 5.5, 2.2   # M2.5 x 6 screws thread straight into the 2.2 mm pilot
SUPERMINI = (43.1, 70.0, 17.8, 21.0, 6.0)        # Seeed XIAO ESP32-C6, 17.8 x 21 (USB-C at the top)
# v0.4: XIAO ESP32-C6 (charges the cell itself). Its R and B buttons sit in the USB-end corners and its antenna and
# antenna socket along the far end, so nothing presses on those: the USB end sits between two corner stops, and
# the clamp tab reaches over the far end, clear of the antenna, and presses on the metal shield can.
XIAO_PCB, XIAO_CAN = 1.0, 2.5      # board thickness, shield can height above it (MEASURE yours)
XIAO_CAN_IN = 3.5                  # the can starts this far in from the far end
# cable clip: two posts the short USB-C cable's free end pushes between, near the top of the box
CLIP_X, CLIP_Y, CLIP_GAP, CLIP_R, CLIP_H = 52.0, 118.0, 3.8, 2.5, 14.0
# The SuperMini has no screw holes: its USB end slides under two corner lips (either side of the USB-C socket),
# then a printed tab (esp_clamp.stl) screws down over its other end with one M2.5 x 6 into a post.
# The board rests on its two short ends only, so wires soldered into the pin holes along its long edges are clear.
SM_CLR, SM_HOOK_IN, SM_LIP_T, SM_REST = 0.4, 3.5, 2.0, 1.5
SM_LIP_OUT = 2.5      # each lip leaves the back wall at board-top height and slopes out and UP at 45 degrees, so
                      # it prints without supports; it catches the board's end edge (0.4 mm play). 2 mm thick at its tip.
SM_POST_R, SM_PILOT_D, SM_TAB_T, SM_TAB_W, SM_TAB_OVER = 3.4, 2.2, 2.0, 12.0, 1.8
CRADLE_WALL, CRADLE_LEDGE, CRADLE_CLR, CRADLE_LIP = 1.8, 1.6, 0.4, 2.0

# cable glands (PG7: 12.5 mm hole) in the bottom end. v0.3: 22 mm apart (were 17) so the 19.5 mm lock nuts
# (point to point) can turn, and 4 mm nearer the back plate so the nuts pass under the short bottom lid posts.
GLAND_PITCH = 22.0
GLANDS_X = (IW / 2 - GLAND_PITCH, IW / 2, IW / 2 + GLAND_PITCH)
GLAND_D, GLAND_Z = 12.6, FLOOR + 16.0
VENT_D, VENT_X, VENT_Z = 2.0, 10.5, FLOOR + IH - 7.0   # tiny breather in the bottom end

# lid screws: M3 heat-set inserts in 8 mm corner columns, given by their inside-corner (x, y)
COL = 8.0
INSERT_D, INSERT_DEPTH, SCREW_CLEAR = 4.1, 7.5, 3.4
COLS = [(0, 0), (IW - COL, 0), (0, ID - COL), (IW - COL, ID - COL)]   # four corners only
# v0.3: the two bottom columns stop short so the outer gland nuts fit under them. Their undersides slope up at
# 45 degrees away from the side wall (printable without supports): the lowest point, at the wall, is SHORT_COL_Z.
SHORT_COL_Z = FLOOR + 24.6
# two ribs under the lid keep it flat between the corner screws, so the gasket is squeezed all the way round
RIB_W, RIB_H = 1.8, 5.0
RIBS_X = (IW * 0.30, IW * 0.70)     # run up the box (inside X); clear of the battery (9 mm below) and the plug

# gasket: a printed TPU ring sits in a groove in the box rim and stands 0.5 mm proud; the flat lid squeezes it
# about 25 % (right for 95A TPU). 1.5 mm foam cord in the groove works too.
GROOVE_W, GROOVE_D = 1.8, 1.4
GASKET_W, GASKET_H = 1.6, 1.9
LID_T, LID_LIP, LID_OVER = 3.0, 4.0, 1.6           # lid thickness, drip lip height, overhang past the walls
# "DIP" cut into the lid's front face in rounded block letters (drawn 12 mm tall with a 2.4 mm stroke and scaled
# up; the stroke scales with the height so the letters keep their shape)
NAME_TEXT = "DIP"
NAME_H, NAME_DEPTH = 18.0, 0.6
NAME_STROKE = 2.4 * NAME_H / 12.0
NAME_Y = 0.62                      # letters centred this far up the lid (0 = bottom, 1 = top)

# post-mount ears on the back plate
EAR_W, EAR_T, EAR_HOLE_D = 16.0, 4.0, 5.2

# ------------------------------------------------------------------ pipe cap
PIPE_OD = 89.0        # 3" PVC, measured
PIPE_ID = 76.0        # inside diameter, measured (for the float bracket's curved back)
CAP_CLR = 1.0         # diameter clearance over the pipe (cap bore 90 mm)
CAP_WALL = 3.0
SKIRT_H = 28.0        # how far the cap slides down over the pipe
PLATE_T = 4.0
PROBE_D = 22.0        # probe hole: measured probes are 21.5 mm, plus 0.5 mm clearance (probes push up from below)
PROBE_SPACING = 44.0  # centre to centre
CHAMBER_H = 26.0      # space above the plate for the probe backs and cables
PLATE_BAND = 31.0     # the plate keeps a solid band this wide across the probes; the rest is open for the cables
PLATE_LEDGE = 4.0     # and a ledge this wide round the wall
CAP_TOP_T = 4.0       # flat cap top
CABLE_SLOT = (8.0, 8.0)     # cable exit: a slot down from the cap's rim (width, depth); the flat top closes it over the cables
POST_FILLET = 3.0     # radius where the cap's screw posts meet the wall
LOCK_SCREW_D = 3.5    # one screw through the skirt into the pipe so the cap can't twist or lift (pilot-drill the PVC)
CAP_SCREW_R = (PIPE_OD + CAP_CLR) / 2 - 3.0   # cap-top screws: posts set into the cap wall, full height to the rim

# ------------------------------------------------------------------ float bracket
FLOAT_STEM_HOLE = 10.6   # M10 stem
FLOAT_OFFSET = 19.0      # stem centre from the pipe wall (float body is about 24 mm across)
FB_W, FB_H, FB_T = 32.0, 42.0, 4.0
SHELF_T = 5.0
M4_CLEAR = 4.4
# outside float bracket: hugs the OUTSIDE of the pipe, with two upright slots so the float height adjusts by 2"
# (M4 screws through the slots and the pipe wall, washers outside, nuts inside). The slots sit either side of the
# float, so a screwdriver reaches them past it.
FBO_W, FBO_H, FBO_ADJ = 46.0, 78.0, 50.8
FBO_SLOT_X, FBO_SLOT_Z0 = 16.0, 8.0     # slot centres from the middle; bottom of the slot travel


def cube(x0_, y0_, z0_, x1, y1, z1):
    return mf.Manifold.cube([x1 - x0_, y1 - y0_, z1 - z0_]).translate([x0_, y0_, z0_])


def nseg(r):
    """Enough sides for a smooth round: at least SEG, and no side longer than about 0.5 mm on big circles."""
    return max(SEG, int(np.ceil(2 * np.pi * r / 0.5 / 4)) * 4)


def cyl(h, r, x=0.0, y=0.0, z=0.0, seg=None):
    return mf.Manifold.cylinder(h, r, r, seg or nseg(r)).translate([x, y, z])


def rrect(w, d, r):
    r = max(min(r, w / 2 - 0.01, d / 2 - 0.01), 0.01)
    pts = [mf.CrossSection.circle(r, SEG).translate([cx, cy]) for cx in (r, w - r) for cy in (r, d - r)]
    return mf.CrossSection.batch_hull(pts)


def rbox(x, y, z, w, d, h, r):
    return rrect(w, d, r).extrude(h).translate([x, y, z])


FILLET = 1.0          # vertical corners on posts, columns and rests: 1 mm rounds (outside) and fillets (inside)


def sq(x0_, y0_, x1, y1):
    return mf.CrossSection.square([x1 - x0_, y1 - y0_]).translate([x0_, y0_])


def round2d(cs, r=None):
    """Round every corner of a flat outline: fillets in the inside corners, then rounds on the outside ones."""
    r = FILLET if r is None else r
    j = mf.JoinType.Round
    n = 96
    return cs.offset(r, j, 2.0, n).offset(-r, j, 2.0, n).offset(-r, j, 2.0, n).offset(r, j, 2.0, n)


def prism(cs, z0_, z1):
    return cs.extrude(z1 - z0_).translate([0, 0, z0_])


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
    """XIAO mount: rests under both short ends, two corner stops at the USB end, screw post + clamp at the far end."""
    x, y, w, d, lz = SUPERMINI
    c, wall = SM_CLR, 2.0
    bx0, bx1, by0, by1 = X(x), X(x + w), Y(y), Y(y + d)        # board outline
    zb = FLOOR + lz                                             # board underside
    ztop = zb + XIAO_PCB + 1.5                                  # stops stand 1.5 mm above the board's top face
    adds, cuts = [], []
    for side in (0, 1):                                         # USB-end corner stops (outside the board, buttons clear)
        if side == 0:
            L = sq(bx0 - c - wall, by1 - 2.0, bx0 - c, by1 + c + wall) + sq(bx0 - c - wall, by1 + c, bx0 + 3.0, by1 + c + wall)
            rest = sq(bx0 - c, by1 - SM_REST, bx0 + 3.0, by1 + c + 0.01)
        else:
            L = sq(bx1 + c, by1 - 2.0, bx1 + c + wall, by1 + c + wall) + sq(bx1 - 3.0, by1 + c, bx1 + c + wall, by1 + c + wall)
            rest = sq(bx1 - 3.0, by1 - SM_REST, bx1 + c, by1 + c + 0.01)
        adds.append(prism(round2d(L + rest, 0.6), FLOOR - 0.2, zb))
        adds.append(prism(round2d(L, 0.6), zb - 0.01, ztop))
    # far end: a rest under the board's end + the screw post just beyond it
    cx = (bx0 + bx1) / 2
    py = by0 - c - SM_POST_R
    far = sq(cx - 5.0, by0 - c - 0.5, cx + 5.0, by0 + SM_REST) + mf.CrossSection.circle(SM_POST_R, SEG).translate([cx, py])
    adds.append(prism(round2d(far), FLOOR - 0.2, zb))
    post_top = zb + XIAO_PCB + XIAO_CAN                         # the tab lies flat across the post and the can
    adds.append(cyl(post_top - FLOOR + 0.2, SM_POST_R, cx, py, FLOOR - 0.2))
    cuts.append(cyl(post_top - FLOOR, SM_PILOT_D / 2, cx, py, FLOOR + 1.0, 32))
    # cable clip
    for sx_ in (-1, 1):
        adds.append(cyl(CLIP_H + 0.2, CLIP_R, X(CLIP_X) + sx_ * (CLIP_GAP / 2 + CLIP_R), Y(CLIP_Y), FLOOR - 0.2))
    return adds, cuts


def esp_clamp():
    """The tab that holds the SuperMini's far end down: one M2.5 x 6 through it into the post. Print flat."""
    c = SM_CLR
    py_to_edge = c + SM_POST_R                                  # post centre to the board's end
    L = SM_POST_R + 1.5 + py_to_edge + XIAO_CAN_IN + 2.5   # reaches 2.5 mm onto the shield can
    tab = rrect(SM_TAB_W, L, 2.0).extrude(SM_TAB_T)
    hole = cyl(SM_TAB_T + 2, 2.9 / 2, SM_TAB_W / 2, SM_POST_R + 1.5, -1, 32)
    return tab - hole


def box():
    H = FLOOR + IH
    shell = rbox(0, 0, 0, OW, OD, H, R_OUT) - rbox(WALL, WALL, FLOOR, IW, ID, IH + 1, R_OUT - WALL)
    adds, cuts = [shell], []
    # ear for the post at the top end of the back plate, two screw holes. v0.3: no bottom ear: the cable glands
    # sit right over it, so its screws couldn't be reached (the two top screws hold the box).
    for ey in (OD,):
        ay = ey if ey < 0 else OD - R_OUT                     # each ear reaches R_OUT into the box's back plate
        adds.append(rbox(6.0, ay, 0, OW - 12.0, EAR_W + R_OUT, EAR_T, 4.0))
        for ex in (OW * 0.28, OW * 0.72):
            cuts.append(cyl(EAR_T + 2, EAR_HOLE_D / 2, ex, ey + EAR_W / 2, -1))
    # lid screw columns
    inner = rrect(IW, ID, R_OUT - WALL).translate([x0, y0])
    cols2d = None
    for cx, cy in COLS:
        q = sq(X(cx), Y(cy), X(cx + COL), Y(cy + COL))
        cols2d = q if cols2d is None else cols2d + q
    cavity = round2d(inner - cols2d)            # rounding the empty space rounds the columns and fillets them in
    adds.append(prism(inner.offset(0.5, mf.JoinType.Round) - cavity, FLOOR - 0.2, H))   # 0.5 mm into the walls so they fuse
    for cx, cy in COLS:
        cuts.append(cyl(INSERT_DEPTH + 0.5, INSERT_D / 2, *col_hole(cx, cy), H - INSERT_DEPTH))
    # bottom columns: cut away everything under a 45 degree slope rising from the side wall (see SHORT_COL_Z)
    reach = COL + FILLET + 1.0
    for left in (True, False):
        wx = X(0) if left else X(IW)                 # the side wall's inside face
        s = 1 if left else -1
        pts = [(wx - s * 1.0, FLOOR - 1.0), (wx + s * reach, FLOOR - 1.0),
               (wx + s * reach, SHORT_COL_Z + reach), (wx - s * 1.0, SHORT_COL_Z - 1.0)]
        under = mf.CrossSection([pts if left else pts[::-1]])          # counter-clockwise either side
        wedge = under.extrude(COL + FILLET + 1.0).rotate([90, 0, 0]).translate([0, Y(COL + FILLET + 1.0), 0])
        cuts.append(wedge ^ cube(min(wx, wx + s * reach), Y(0), FLOOR, max(wx, wx + s * reach), Y(COL + FILLET + 1.0), H))   # stops at the floor
    # battery-holder platform, its insert and the locating rail
    hx, hy, hw, hd, _ = HOLDER
    rx = X(hx + hw + RAIL_CLR)
    # v0.4: the platform runs from the side wall to the rail's outer edge, so there are no thin slots to print
    plat = round2d(sq(X(0) - 0.5, Y(hy + PLAT_INSET), rx + RAIL_W, Y(hy + hd - PLAT_INSET)))
    adds.append(prism(plat, FLOOR - 0.2, FLOOR + PLAT_H))
    adds.append(prism(round2d(sq(rx, Y(hy + 8.0), rx + RAIL_W, Y(hy + hd - 8.0)), 0.8), FLOOR - 0.2, FLOOR + PLAT_H + RAIL_H))
    cuts.append(cyl(HOLDER_INSERT_DEPTH + 0.5, HOLDER_INSERT_D / 2, X(hx + hw / 2), Y(hy + hd / 2), FLOOR + PLAT_H - HOLDER_INSERT_DEPTH))
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
    """NAME_TEXT as a flat outline in rounded block letters, centred on (cx, cy), reading normally
    from the front of the box (X to the right, Y up)."""
    H, sw = NAME_H, NAME_STROKE
    k = H / 12.0                      # the letter shapes were drawn 12 mm tall
    r = 3.0 * k

    def box2(u0, v0, u1, v1):
        return mf.CrossSection.square([u1 - u0, v1 - v0]).translate([u0, v0])

    def ring(u0, v0, u1, v1):
        w, h = u1 - u0, v1 - v0
        return (rrect(w, h, r).translate([u0, v0])
                - rrect(w - 2 * sw, h - 2 * sw, max(r - sw, 0.4)).translate([u0 + sw, v0 + sw]))

    stem = box2(0, 0, sw, H)
    glyphs = {                        # (width, outline) per letter, the same proportions for every letter
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
        rib = rrect(RIB_W, ID - 2 * COL - 8, RIB_W / 2 - 0.01).translate([X(rx) - RIB_W / 2, Y(COL + 4)])
        m = m + prism(rib, H - RIB_H, H + 0.1)
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
    # open the plate either side of the probe band: less to bridge, and the float and temperature cables drop straight through
    for side in (1, -1):
        y0_, y1_ = sorted((side * PLATE_BAND / 2, side * ri))
        m = m - (cyl(PLATE_T + 2, ri - PLATE_LEDGE, 0, 0, SKIRT_H - 1, nseg(ri)) ^ cube(-ri, y0_, SKIRT_H - 1, ri, y1_, SKIRT_H + PLATE_T + 1))
    # 45-degree chamfer under the ledge on the chamber side, so the cap prints upside down (rim on the bed) without supports there
    zc = SKIRT_H + PLATE_T
    m = m + (cyl(PLATE_LEDGE, ri + 0.5, z=zc - 0.01) - mf.Manifold.cylinder(PLATE_LEDGE + 0.02, ri - PLATE_LEDGE, ri + 0.01, nseg(ri)).translate([0, 0, zc - 0.01]))
    # step the probe band's chamber-side face 0.1 mm down from the ledge, so the slicer's fill tool paints supports on the band only
    m = m - (cyl(1.0, ri - PLATE_LEDGE, z=zc - 0.1, seg=nseg(ri)) ^ cube(-ri, -PLATE_BAND / 2 - 0.01, zc - 0.1, ri, PLATE_BAND / 2 + 0.01, zc + 0.9))
    # air vent in the skirt (so the water inside can rise and fall)
    m = m - cyl(10, 1.6, 0, 0, 0).rotate([90, 0, 0]).translate([0, -ri + 1, SKIRT_H - 6])
    # lock screw through the skirt into the pipe, on the side away from the vent
    m = m - cyl(CAP_WALL + 4, LOCK_SCREW_D / 2, 0, 0, 0).rotate([0, 90, 0]).translate([ri - 2, 0, SKIRT_H / 2])
    # three screw posts on the chamber wall for the top (short: they hang from the rim)
    post_h = INSERT_DEPTH + 2.0   # just past the insert hole: printed upside down, the posts grow from the bed and end there
    spots = [(CAP_SCREW_R * np.cos(np.radians(a)), CAP_SCREW_R * np.sin(np.radians(a))) for a in (90, 210, 330)]
    ring = mf.CrossSection.circle(ro - 1.0, nseg(ro)) - mf.CrossSection.circle(ri, nseg(ri))   # outer edge buried in the wall (no coincident faces)
    for bx, by in spots:
        ring = ring + mf.CrossSection.circle(5.0, 48).translate([bx, by])
    j = mf.JoinType.Round
    ring = ring.offset(POST_FILLET, j, 2.0, 96).offset(-POST_FILLET, j, 2.0, 96)   # radius where each post meets the wall
    m = m + prism(ring, total - post_h, total)
    for bx, by in spots:
        m = m - cyl(INSERT_DEPTH + 0.5, INSERT_D / 2, bx, by, total - INSERT_DEPTH)
    # cable exit: a slot down from the rim, between two screw posts; the cables come out sideways under the top
    nw, nh = CABLE_SLOT
    m = m - cube(-nw / 2, -ro - 1, total - nh, nw / 2, -ri + 6, total + 1)   # runs well past the curved inside of the wall
    return m


def pipe_cap_top():
    ri = (PIPE_OD + CAP_CLR) / 2
    ro = ri + CAP_WALL
    t = CAP_TOP_T
    m = cyl(t, ro)                                                     # flat underside: the 3 screws locate it
    for a in (90, 210, 330):
        bx, by = CAP_SCREW_R * np.cos(np.radians(a)), CAP_SCREW_R * np.sin(np.radians(a))
        m = m - cyl(t + 6, SCREW_CLEAR / 2, bx, by, -3)
    return m


def float_bracket():
    """Curved back fits the pipe's inside wall; the float stem goes through the shelf, float hanging below."""
    r = PIPE_ID / 2
    back = (cyl(FB_H, r) - cyl(FB_H + 2, r - FB_T, 0, 0, -1)) ^ cube(-FB_W / 2, -r - 1, 0, FB_W / 2, -r + 10, FB_H)
    shelf = cube(-FB_W / 2, -r + FB_T - 0.5, FB_H - SHELF_T, FB_W / 2, -r + FLOAT_OFFSET + 12, FB_H) ^ cyl(FB_H, r - 0.5)
    m = back + shelf
    m = m - cyl(SHELF_T + 2, FLOAT_STEM_HOLE / 2, 0, -r + FLOAT_OFFSET, FB_H - SHELF_T - 1)
    m = m - cyl(20, M4_CLEAR / 2, 0, 0, 0).rotate([90, 0, 0]).translate([-FB_W / 4, -r + 12, FB_H * 0.3])
    m = m - cyl(20, M4_CLEAR / 2, 0, 0, 0).rotate([90, 0, 0]).translate([FB_W / 4, -r + 12, FB_H * 0.3])
    # print lying on its side: the layers then run along the shelf, so it's strong without a brace
    return m.rotate([0, 90, 0]).translate([0, r, FB_W / 2])


def float_bracket_outside():
    """Curved back fits the pipe's outside wall; the float hangs from the shelf, 19 mm out from the pipe."""
    r = PIPE_OD / 2 + 0.3
    t = FB_T
    back = (cyl(FBO_H, r + t) - cyl(FBO_H + 2, r, 0, 0, -1)) ^ cube(-FBO_W / 2, -r - t - 1, 0, FBO_W / 2, -r + 12, FBO_H)
    shelf = cube(-FB_W / 2, -r - FLOAT_OFFSET - 13, FBO_H - SHELF_T, FB_W / 2, -r - 1, FBO_H) - cyl(FBO_H + 2, r, 0, 0, -1)
    m = back + shelf
    m = m - cyl(SHELF_T + 2, FLOAT_STEM_HOLE / 2, 0, -r - FLOAT_OFFSET, FBO_H - SHELF_T - 1)
    for sx in (-FBO_SLOT_X, FBO_SLOT_X):
        a = cyl(30, M4_CLEAR / 2, 0, 0, 0).rotate([90, 0, 0]).translate([sx, -r + 15, FBO_SLOT_Z0])
        b = cyl(30, M4_CLEAR / 2, 0, 0, 0).rotate([90, 0, 0]).translate([sx, -r + 15, FBO_SLOT_Z0 + FBO_ADJ])
        m = m - mf.Manifold.hull(a + b)
    return m.rotate([0, 90, 0]).translate([0, r + t, FBO_W / 2])


def write_stl(m, path):
    mesh = m.simplify(0.0005).to_mesh()               # merges near-duplicate points (0.0005 mm) so the STL is watertight
    v = np.asarray(mesh.vert_properties)[:, :3].astype(np.float32)
    f = np.asarray(mesh.tri_verts)
    tri = v[f]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    keep = np.linalg.norm(n, axis=1) > 1e-9          # drop zero-area slivers left by the booleans
    tri, n, f = tri[keep], n[keep], f[keep]
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    data = np.zeros(len(f), dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    data["n"], data["v"] = n, tri.reshape(-1, 9)
    with open(path, "wb") as fh:
        fh.write(b"DIP pond sensor".ljust(80, b" "))
        fh.write(np.uint32(len(f)).tobytes())
        fh.write(data.tobytes())
    return len(f)


PARTS = {"box": box, "box_lid": box_lid, "gasket": gasket, "esp_clamp": esp_clamp, "pipe_cap": pipe_cap, "pipe_cap_top": pipe_cap_top, "float_bracket": float_bracket, "float_bracket_outside": float_bracket_outside}

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    for name, fn in PARTS.items():
        m = fn()
        bb = m.bounding_box()
        n = write_stl(m, os.path.join(out, name + ".stl"))
        print("  %-13s %6d triangles, genus %d, size %.1f x %.1f x %.1f mm, status %s" % (
            name, n, m.genus(), bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2], m.status()))
