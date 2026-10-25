"""Render STL files to PNG previews with a small numpy z-buffer (correct hidden surfaces),
and draw 2D cross-sections. Uses only numpy + matplotlib."""
import struct, sys, os, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def load_stl(path):
    with open(path, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        data = np.frombuffer(f.read(n * 50), dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    return data["v"].reshape(-1, 3, 3).astype(float)


def rot(elev, azim):
    a, e = math.radians(azim), math.radians(elev)
    Rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, math.cos(e), -math.sin(e)], [0, math.sin(e), math.cos(e)]])
    # camera looks along -Z after rotation; first spin about Z, then tilt
    return Rx @ Rz


def zbuffer(tris_list, elev, azim, W=900, H=700, colors=None):
    R = rot(-(90 - elev), azim)
    allp = np.concatenate([t.reshape(-1, 3) for t in tris_list]) @ R.T
    mn, mx = allp.min(0), allp.max(0)
    span = max(mx[0] - mn[0], mx[1] - mn[1]) * 1.08
    sc = min(W, H) / span
    cx, cy = (mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2
    img = np.ones((H, W, 3))
    zb = np.full((H, W), -np.inf)
    light = np.array([0.35, 0.45, 0.82]); light /= np.linalg.norm(light)
    for k, tris in enumerate(tris_list):
        base_col = np.array(colors[k] if colors else (0.62, 0.68, 0.78))
        P = tris @ R.T
        n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
        ln = np.linalg.norm(n, axis=1)
        ok = ln > 1e-9
        P, n = P[ok], n[ok] / ln[ok][:, None]
        shade = 0.30 + 0.70 * np.abs(n @ light)
        sx = (P[:, :, 0] - cx) * sc + W / 2
        sy = H / 2 - (P[:, :, 1] - cy) * sc
        sz = P[:, :, 2]
        for i in range(len(P)):
            x, y, z = sx[i], sy[i], sz[i]
            x0, x1 = int(max(0, math.floor(x.min()))), int(min(W - 1, math.ceil(x.max())))
            y0, y1 = int(max(0, math.floor(y.min()))), int(min(H - 1, math.ceil(y.max())))
            if x1 < x0 or y1 < y0:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            d = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
            if abs(d) < 1e-12:
                continue
            l0 = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / d
            l1 = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / d
            l2 = 1 - l0 - l1
            inside = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
            if not inside.any():
                continue
            zz = l0 * z[0] + l1 * z[1] + l2 * z[2]
            sub = zb[y0:y1 + 1, x0:x1 + 1]
            upd = inside & (zz > sub)
            sub[upd] = zz[upd]
            img[y0:y1 + 1, x0:x1 + 1][upd] = base_col * shade[i]
    return img


def views(paths, out, vlist, colors=None, offsets=None, size=None):
    tris = []
    for i, p in enumerate(paths):
        t = load_stl(p)
        if offsets and offsets[i] is not None:
            t = t + np.array(offsets[i])
        tris.append(t)
    n = len(vlist)
    fig, axs = plt.subplots(1, n, figsize=size or (5.5 * n, 4.6), dpi=110)
    axs = np.atleast_1d(axs)
    for ax, (elev, azim, label) in zip(axs, vlist):
        ax.imshow(zbuffer(tris, elev, azim, colors=colors))
        ax.set_title(label, fontsize=11)
        ax.axis("off")
    plt.tight_layout()
    plt.savefig(out)
    plt.close(fig)


def section(path, axis, value, out, label):
    """Cut the mesh with plane axis=value and draw the outline segments."""
    T = load_stl(path)
    ax_i = "xyz".index(axis)
    other = [i for i in range(3) if i != ax_i]
    d = T[:, :, ax_i] - value
    segs = []
    for tri, dd in zip(T, d):
        pts = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            if (dd[a] > 0) != (dd[b] > 0):
                t = dd[a] / (dd[a] - dd[b])
                p = tri[a] + (tri[b] - tri[a]) * t
                pts.append(p[other])
        if len(pts) == 2:
            segs.append(pts)
    fig, ax = plt.subplots(figsize=(7, 7), dpi=110)
    for s in segs:
        ax.plot([s[0][0], s[1][0]], [s[0][1], s[1][1]], "k-", lw=0.8)
    ax.set_aspect("equal")
    ax.set_title(label)
    ax.set_xlabel("xyz"[other[0]] + " (mm)")
    ax.set_ylabel("xyz"[other[1]] + " (mm)")
    ax.grid(alpha=0.3)
    if axis == "z":
        ax.invert_yaxis()   # front (Y=0) at the top of the picture
    plt.tight_layout()
    plt.savefig(out)
    plt.close(fig)


if __name__ == "__main__":
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    what = sys.argv[1:] or ["previews", "sections"]
    if "previews" in what:
        views([f"{d}/base.stl"], f"{d}/preview_base.png",
              [(30, 30, "Base from the front (radar window at right)"), (30, 210, "Base from the rear (ports)"), (65, 20, "Base from above, front edge nearest")])
        views([f"{d}/base.stl"], f"{d}/preview_base_bottom.png", [(-40, 30, "Base underside (tripod insert hole)")], size=(6, 5))
        views([f"{d}/lid_oled.stl"], f"{d}/preview_lid.png", [(40, 30, "Lid with OLED window"), (-40, 30, "Lid underside (OLED pocket)")], size=(11, 4.6))
        views([f"{d}/front_cover.stl"], f"{d}/preview_cover.png", [(45, 200, "Front cover as printed")], size=(6, 5))
    if "sections" in what:
        section(f"{d}/base.stl", "z", 3.4, f"{d}/sec_z_floor.png", "Base, slice 1 mm above floor (front at top)")
        section(f"{d}/base.stl", "z", 20.0, f"{d}/sec_z_mid.png", "Base, slice at Z = 20 mm (front at top)")
        section(f"{d}/base.stl", "x", 78.4, f"{d}/sec_x_radar.png", "Base, side section through radar centre")
