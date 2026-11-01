"""Wiring diagrams for the DIP assembly guide (docs/DIP-assembly-guide.docx). Run: python make_diagrams.py"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

D = os.path.dirname(os.path.abspath(__file__))
RED, BLK, YEL, ORG, BLU, GRN, PUR, GRY = "#d62728", "#222222", "#c9a400", "#e07b00", "#1f6fd1", "#1f9e4a", "#7b3fb5", "#888888"
FS = 11


def fig(w, h):
    f, ax = plt.subplots(figsize=(w, h), dpi=200)
    ax.set_xlim(0, w * 10); ax.set_ylim(0, h * 10); ax.axis("off"); ax.set_aspect("equal")
    return f, ax


def box(ax, x, y, w, h, title, sub=None, fc="#eef3fb", ec=BLU):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.5", fc=fc, ec=ec, lw=1.8))
    ax.text(x + w / 2, y + h - 2.2, title, ha="center", va="top", fontsize=FS + 1, weight="bold")
    if sub:
        ax.text(x + w / 2, y + h - 5.6, sub, ha="center", va="top", fontsize=FS - 2, color="#555")


def wire(ax, pts, c, lw=2.6):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=c, lw=lw, solid_capstyle="round", solid_joinstyle="round", zorder=3)


def dot(ax, x, y, c):
    ax.add_patch(Circle((x, y), 0.7, color=c, zorder=4))


def resistor(ax, x, y, horiz=True, label="", c=PUR):
    w, h = (6, 2.2) if horiz else (2.2, 6)
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fc="white", ec=c, lw=2, zorder=5))
    if horiz:
        ax.text(x, y + 2.2, label, ha="center", va="bottom", fontsize=FS - 1)
    else:
        ax.text(x + 2.2, y, label, ha="left", va="center", fontsize=FS - 1)


def save(f, name):
    f.savefig(os.path.join(D, name), bbox_inches="tight", facecolor="white")
    plt.close(f)


# ---------------------------------------------------------------- 1. the whole thing
def overview():
    f, ax = fig(13, 9.6)
    # battery holder: a plain cradle, two wires to the XIAO's BAT pads
    box(ax, 2, 50, 24, 22, "18650 holder", "plain, red and black wires", fc="#f7efe2", ec="#9a6b2f")
    # XIAO (front view, USB-C at the top)
    box(ax, 44, 36, 26, 42, "XIAO ESP32-C6", "the brain, charges the cell")
    for lab, y in [("D0", 68), ("D1", 64), ("D3", 56), ("D4", 52), ("D5", 48)]:
        ax.text(45.5, y, lab, ha="left", va="center", fontsize=FS, weight="bold")
    for lab, y in [("GND", 64), ("3V3", 60)]:
        ax.text(68.5, y, lab, ha="right", va="center", fontsize=FS, weight="bold")
    ax.text(57, 39.5, "BAT -   BAT +\n(pads underneath)", ha="center", va="bottom", fontsize=FS - 2, color="#555")
    # battery wires to the BAT pads
    wire(ax, [(26, 62), (34, 62), (34, 30), (60, 30), (60, 38)], RED); ax.text(27, 63.2, "red", fontsize=FS - 2, color=RED)
    wire(ax, [(26, 58), (31, 58), (31, 27), (54, 27), (54, 38)], BLK); ax.text(27, 55, "black", fontsize=FS - 2)
    # battery divider: drawn on its own picture
    ax.text(14, 44, "D0: battery reading,\n2 x 100k to BAT + and BAT -\n(see its own picture)", ha="center", va="top", fontsize=FS - 2, color=PUR)
    # sensor board
    box(ax, 92, 56, 34, 22, "Ultrasonic sensor board", "JSN-SR20, MODE pad left empty")
    for lab, y in [("5V", 68), ("Trig", 64.5), ("Echo", 61), ("GND", 57.5)]:
        ax.text(93.5, y, lab, ha="left", va="center", fontsize=FS - 1)
    ax.text(124, 62, "2 probes plug\ninto the white\nsockets", ha="right", va="center", fontsize=FS - 2, color="#555")
    # sensor power from 3V3 / GND
    wire(ax, [(69, 60), (84, 60), (84, 84), (88, 84), (88, 68), (93, 68)], RED)
    wire(ax, [(69, 64), (82, 64), (82, 82), (86, 82), (86, 57.5), (93, 57.5)], BLK)
    # trig / echo
    wire(ax, [(45, 52), (38, 52)], BLU); wire(ax, [(38, 52), (38, 88), (90, 88), (90, 64.5), (93, 64.5)], BLU); ax.text(60, 85.5, "Trig (D4)", fontsize=FS - 2, color=BLU)
    wire(ax, [(45, 48), (36, 48), (36, 90), (91.5, 90), (91.5, 61), (93, 61)], GRN); ax.text(75, 91, "Echo (D5)", fontsize=FS - 2, color=GRN)
    # 4-core cable
    ax.add_patch(FancyBboxPatch((76, 6), 50, 40, boxstyle="round,pad=0.6,rounding_size=1.5", fc="#fafafa", ec=GRY, lw=1.2, ls="--"))
    ax.text(101, 44.5, "4-core cable to the pipe cap", ha="center", va="top", fontsize=FS, weight="bold")
    wire(ax, [(69, 60), (74, 60), (74, 38), (118, 38)], RED); ax.text(119, 38, "1: 3.3V", va="center", fontsize=FS - 1)
    wire(ax, [(69, 64), (72, 64), (72, 31), (118, 31)], BLK); ax.text(119, 31, "2: GND", va="center", fontsize=FS - 1)
    wire(ax, [(45, 56), (43, 56), (43, 24), (118, 24)], YEL); ax.text(119, 24, "3: Temp (D3)", va="center", fontsize=FS - 1)
    wire(ax, [(45, 64), (44, 64), (44, 17), (118, 17)], ORG); ax.text(119, 17, "4: Float (D1)", va="center", fontsize=FS - 1)
    # pull-ups at the cable end
    dot(ax, 86, 38, RED); wire(ax, [(86, 38), (86, 34)], RED); resistor(ax, 86, 31, False, ""); ax.text(84, 34.5, "4.7k", ha="right", va="center", fontsize=FS - 1); wire(ax, [(86, 28), (86, 24)], YEL); dot(ax, 86, 24, YEL)
    dot(ax, 100, 38, RED); wire(ax, [(100, 38), (100, 27.5)], RED); resistor(ax, 100, 24.5, False, "100k (C)"); wire(ax, [(100, 21.5), (100, 17)], ORG); dot(ax, 100, 17, ORG)
    ax.text(101, 9.5, "The 4.7k and 100k (C) sit right where the cable enters the box", ha="center", fontsize=FS - 2, color="#555")
    save(f, "d_overview.png")


# ---------------------------------------------------------------- 2. XIAO pins (front view, USB-C at the top)
def pins():
    f, ax = fig(10, 7)
    ax.add_patch(FancyBboxPatch((34, 10), 32, 46, boxstyle="round,pad=0.4,rounding_size=1.5", fc="#1d1d1d", ec="#000"))
    ax.add_patch(Rectangle((44, 52), 12, 7, fc="#c0c0c0", ec="#777")); ax.text(50, 55.5, "USB-C", ha="center", va="center", fontsize=FS - 2)
    ax.text(50, 33, "XIAO\nESP32-C6\nFRONT\n(metal can side)", ha="center", va="center", color="white", fontsize=FS - 1)
    left = ["D0", "D1", "D2", "D3", "D4", "D5", "D6"]
    right = ["5V", "GND", "3V3", "D10", "D9", "D8", "D7"]
    use = {"D0": ("Batt", PUR), "D1": ("Float", ORG), "D3": ("Temp", YEL), "D4": ("Trig", BLU), "D5": ("Echo", GRN),
           "GND": ("GND", "#9a9a9a"), "3V3": ("3.3V", RED)}
    for i in range(7):
        y = 49 - i * 6
        for lab, x, tx, ha in [(left[i], 36, 28, "right"), (right[i], 64, 72, "left")]:
            u = use.get(lab)
            ax.add_patch(Circle((x, y), 1.5, fc="#d4a017" if u else "#7a6a3a", ec=u[1] if u else "none", lw=3 if u else 0, zorder=4))
            ax.text(x + (4.5 if x < 50 else -4.5), y, lab, ha="center", va="center", color="white", fontsize=FS - 2, weight="bold")
            if u:
                ax.text(tx, y, u[0], ha=ha, va="center", fontsize=FS - 1, color=u[1], weight="bold")
    ax.text(50, 2, "Pins you use are ringed in color. Leave the grey ones empty. The battery goes to the BAT pads underneath.", ha="center", fontsize=FS - 2, color="#555")
    save(f, "d_pins.png")


# ---------------------------------------------------------------- 3. reading resistors
def resistors():
    f, ax = fig(10, 5.2)
    rows = [("100k (4 bands)", ["#8b4513", "#000000", "#e8c800", "#d4af37"], "brown, black, yellow, gold", 40),
            ("100k (5 bands)", ["#8b4513", "#000000", "#000000", "#ff7f00", "#8b4513"], "brown, black, black, orange, brown", 25),
            ("4.7k (5 bands)", ["#e8c800", "#7b3fb5", "#000000", "#8b4513", "#8b4513"], "yellow, violet, black, brown, brown", 10)]
    for name, cols, words, y in rows:
        ax.text(2, y, name, va="center", fontsize=FS, weight="bold")
        ax.plot([24, 64], [y, y], color="#999", lw=2, zorder=1)
        ax.add_patch(FancyBboxPatch((32, y - 3.4), 24, 6.8, boxstyle="round,pad=0.2,rounding_size=2.5", fc="#e9d8b4", ec="#b59a6a", zorder=2))
        for k, c in enumerate(cols):
            x = 35 + k * 4.2 + (2.5 if k == len(cols) - 1 else 0)
            ax.add_patch(Rectangle((x, y - 3.3), 1.8, 6.6, fc=c, ec="none", zorder=3))
        ax.text(66, y, words, va="center", fontsize=FS - 1)
    ax.text(50, 1, "Resistors work either way round. The odd band (gold or the last brown) goes on the right when you read them.", ha="center", fontsize=FS - 2, color="#555")
    save(f, "d_resistors.png")


# ---------------------------------------------------------------- 4. how to splice two wires
def splice():
    f, ax = fig(12, 6.5)
    steps = [("1. Slide heat shrink on first", 52), ("2. Strip 8 mm, twist or hook together", 36), ("3. Solder, let cool, slide shrink over, heat", 20)]
    for t, y in steps:
        ax.text(2, y + 7, t, fontsize=FS, weight="bold")
    # step 1
    wire(ax, [(10, 52), (55, 52)], RED, 6); wire(ax, [(65, 52), (110, 52)], RED, 6)
    ax.add_patch(Rectangle((22, 50), 16, 4, fc="#333", ec="none", alpha=0.6, zorder=5)); ax.text(30, 46.5, "heat shrink, pushed well back", ha="center", fontsize=FS - 2)
    # step 2
    wire(ax, [(10, 36), (52, 36)], RED, 6); wire(ax, [(68, 36), (110, 36)], RED, 6)
    wire(ax, [(52, 36), (62, 36.6)], "#b87333", 2); wire(ax, [(68, 36), (58, 35.4)], "#b87333", 2)
    ax.text(60, 31, "bare copper overlaps", ha="center", fontsize=FS - 2)
    # step 3
    wire(ax, [(10, 20), (110, 20)], RED, 6)
    ax.add_patch(Rectangle((50, 17.5), 20, 5, fc="#333", ec="none", zorder=5)); ax.text(60, 14, "shrink covers all the bare metal", ha="center", fontsize=FS - 2)
    ax.text(60, 3, "Outdoors (the pipe cap): use adhesive-lined heat shrink, it seals with glue as it shrinks.", ha="center", fontsize=FS - 1, color="#555")
    save(f, "d_splice.png")


# ---------------------------------------------------------------- 5. probe cable: cut and re-solder (coax)
def coax():
    f, ax = fig(12, 6.2)
    ax.text(2, 56, "Each probe cable is a thin coax: a centre wire inside a braided shield.", fontsize=FS)
    # plug side
    ax.add_patch(Rectangle((4, 30), 12, 10, fc="#111", ec="none")); ax.add_patch(Rectangle((0, 32), 4, 6, fc="white", ec="#999")); ax.text(9, 26, "plug", ha="center", fontsize=FS - 2)
    wire(ax, [(16, 35), (40, 35)], BLK, 7)
    wire(ax, [(40, 35), (47, 35)], "#9a9a9a", 5); ax.text(43, 40, "shield", ha="center", fontsize=FS - 2)
    wire(ax, [(47, 35), (53, 35)], "#ddd", 3); wire(ax, [(53, 35), (56, 35)], "#b87333", 2); ax.text(52, 29, "centre", ha="center", fontsize=FS - 2)
    # probe side
    wire(ax, [(64, 35), (67, 35)], "#b87333", 2); wire(ax, [(67, 35), (73, 35)], "#ddd", 3); wire(ax, [(73, 35), (80, 35)], "#9a9a9a", 5); wire(ax, [(80, 35), (112, 35)], BLK, 7)
    ax.text(100, 40, "to the probe (through the gland)", ha="center", fontsize=FS - 2)
    ax.annotate("", xy=(54.5, 35), xytext=(65.5, 35), arrowprops=dict(arrowstyle="<->", color=RED, lw=1.5))
    ax.text(60, 46, "centre to centre", ha="center", color=RED, fontsize=FS - 1, weight="bold")
    ax.text(60, 22, "shield to shield (twist the braid into a tail, bring it\nalongside on top of the first piece of heat shrink)", ha="center", fontsize=FS - 1, color="#333")
    ax.text(60, 6, "Small shrink over the centre joint first, then one bigger piece over the whole splice.", ha="center", fontsize=FS - 1, color="#555")
    save(f, "d_coax.png")


# ---------------------------------------------------------------- 6. pipe cap end of the cable
def capend():
    f, ax = fig(12, 6.5)
    ax.text(2, 61, "Inside the pipe cap: the 4-core cable meets the temperature probe and the float", fontsize=FS, weight="bold")
    for y, c, lab in [(48, RED, "1: 3.3V"), (40, BLK, "2: GND"), (32, YEL, "3: Temp"), (24, ORG, "4: Float")]:
        wire(ax, [(4, y), (50, y)], c); ax.text(4, y + 1.5, lab, fontsize=FS - 1)
    box(ax, 82, 34, 32, 18, "Temperature probe", fc="#eaf6ee", ec=GRN)
    wire(ax, [(50, 48), (82, 48)], RED); ax.text(80, 49.3, "red", ha="right", fontsize=FS - 2)
    wire(ax, [(50, 40), (82, 40)], BLK); ax.text(80, 41.3, "black", ha="right", fontsize=FS - 2)
    wire(ax, [(50, 32), (66, 32), (66, 44), (82, 44)], YEL); ax.text(80, 45.3, "yellow", ha="right", fontsize=FS - 2)
    box(ax, 82, 6, 32, 18, "Float switch", fc="#fff3e2", ec=ORG)
    wire(ax, [(50, 24), (60, 24), (60, 18), (82, 18)], ORG); ax.text(80, 19.3, "float wire", ha="right", fontsize=FS - 2)
    wire(ax, [(56, 40), (56, 12), (82, 12)], BLK); dot(ax, 56, 40, BLK); ax.text(80, 13.3, "other float wire", ha="right", fontsize=FS - 2)
    ax.text(30, 10, "The GND joint has three wires:\ncable 2, probe black, one float wire.\nThe float's two wires are the same,\nuse either.", ha="center", fontsize=FS - 1, color="#555")
    save(f, "d_capend.png")


# ---------------------------------------------------------------- 7. box end of the cable (pull-up resistors)
def boxend():
    f, ax = fig(12, 6)
    ax.text(2, 56, "Inside the box: two resistors where the 4-core cable comes in", fontsize=FS, weight="bold")
    ys = {"r": 44, "k": 36, "y": 28, "o": 20}
    for k, c, lab in [("r", RED, "1: 3.3V  ->  XIAO 3V3"), ("k", BLK, "2: GND  ->  XIAO GND"), ("y", YEL, "3: Temp  ->  XIAO D3"), ("o", ORG, "4: Float  ->  XIAO D1")]:
        wire(ax, [(4, ys[k]), (112, ys[k])], c); ax.text(112, ys[k] + 1.5, lab, ha="right", fontsize=FS - 1)
    ax.text(4, 48, "from the gland", fontsize=FS - 2, color="#555")
    dot(ax, 40, 44, RED); wire(ax, [(40, 44), (40, 40)], RED); resistor(ax, 40, 34, False, ""); ax.text(37, 34, "4.7k", ha="right", va="center", fontsize=FS - 1); wire(ax, [(40, 31), (40, 28)], YEL); dot(ax, 40, 28, YEL)
    dot(ax, 60, 44, RED); wire(ax, [(60, 44), (60, 35)], RED); resistor(ax, 60, 30, False, ""); ax.text(63, 30, "100k (C)", va="center", fontsize=FS - 1); wire(ax, [(60, 27), (60, 20)], ORG); dot(ax, 60, 20, ORG)
    ax.text(58, 6, "Solder each resistor leg onto the wire with a small piece of heat shrink over each joint.\nThe 4.7k leg crosses the GND wire: put a sleeve of heat shrink on that leg first.", ha="center", fontsize=FS - 1, color="#555")
    save(f, "d_boxend.png")


# ---------------------------------------------------------------- 8. battery divider on the XIAO's underside
def divider():
    f, ax = fig(11, 7)
    ax.text(2, 66, "Battery reading: two 100k resistors on the XIAO's underside", fontsize=FS, weight="bold")
    ax.add_patch(FancyBboxPatch((30, 8), 32, 46, boxstyle="round,pad=0.4,rounding_size=1.5", fc="#1d1d1d", ec="#000"))
    ax.add_patch(Rectangle((40, 50), 12, 7, fc="#c0c0c0", ec="#777"))
    ax.text(46, 30, "XIAO\nBACK", ha="center", va="center", color="white", fontsize=FS)
    ax.add_patch(Circle((60, 47), 1.6, fc="#d4a017", ec=PUR, lw=3, zorder=4)); ax.text(56, 47, "D0", ha="center", va="center", color="white", fontsize=FS - 1, weight="bold")
    for x, lab in [(42, "BAT -"), (50, "BAT +")]:
        ax.add_patch(Rectangle((x - 1.6, 13), 3.2, 6, fc="#d4a017", ec="#7a5a00", zorder=4)); ax.text(x, 22, lab, ha="center", color="white", fontsize=FS - 2, weight="bold")
    wire(ax, [(50, 13), (50, 4), (16, 4)], RED); ax.text(15, 4, "holder red", ha="right", va="center", fontsize=FS - 1, color=RED)
    wire(ax, [(42, 13), (42, 7), (16, 7)], BLK); ax.text(15, 7.6, "holder black", ha="right", va="center", fontsize=FS - 1)
    # A: BAT+ to D0 (outside the board edge), B: D0 to BAT-
    wire(ax, [(51.6, 16), (68, 16), (68, 28)], PUR); resistor(ax, 68, 31, False, "100k (A)"); wire(ax, [(68, 34), (68, 47), (61.6, 47)], PUR)
    wire(ax, [(60, 45.4), (60, 40), (24, 40), (24, 28)], PUR); resistor(ax, 24, 24, False, ""); ax.text(21, 24, "100k (B)", ha="right", va="center", fontsize=FS - 1)
    wire(ax, [(24, 21), (24, 16), (40.4, 16)], PUR)
    ax.text(46, 61, "(A) from BAT + to D0, (B) from D0 to BAT -. Sleeve the legs with heat shrink.", ha="center", fontsize=FS - 2, color="#555")
    save(f, "d_divider.png")


if __name__ == "__main__":
    overview(); pins(); resistors(); splice(); coax(); capend(); boxend(); divider()
    print("ok")
