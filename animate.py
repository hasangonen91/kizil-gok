# -*- coding: utf-8 -*-
"""BULUT-KALKAN animasyon üretici: MP4 video + poster karesi.
Kullanım: python3 animate.py [seed] [cikti.mp4]
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["animation.ffmpeg_path"] = "/opt/homebrew/bin/ffmpeg"
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.patches import Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim import config as C
from sim.engine import run

BG = "#0b1020"

XMIN, XMAX = -3400.0, 900.0
YMIN, YMAX = -180.0, 980.0
GRID_X, GRID_Y = 110, 56


def blur(a, passes=2):
    for _ in range(passes):
        p = np.pad(a, 1, mode="edge")
        a = (p[:-2, :-2] + p[:-2, 1:-1] + p[:-2, 2:] +
             p[1:-1, :-2] + p[1:-1, 1:-1] + p[1:-1, 2:] +
             p[2:, :-2] + p[2:, 1:-1] + p[2:, 2:]) / 9.0
    return a


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else C.SEED
    out = sys.argv[2] if len(sys.argv) > 2 else "media/demo.mp4"
    C.SEED = seed
    res = run(C)

    n_frames = len(res.t)
    print(f"Kare sayısı: {n_frames}, süre {res.t[-1]:.1f}s")

    fig, ax = plt.subplots(figsize=(16, 9), dpi=110)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(XMIN, XMAX)
    ax.set_ylim(YMIN, YMAX)
    ax.set_aspect("equal")
    ax.tick_params(colors="#5a6a8a", labelsize=8)
    for s in ax.spines.values():
        s.set_color("#2a3550")

    # yoğunluk ısı haritası
    dens_img = ax.imshow(np.zeros((GRID_Y, GRID_X)), origin="lower",
                         extent=(XMIN, XMAX, YMIN, YMAX), cmap="inferno",
                         alpha=0.55, vmin=0, vmax=6.0, interpolation="bilinear",
                         zorder=1)

    # zemin
    ax.axhline(0, color="#3d4d70", lw=1.5, zorder=2)
    ax.fill_between([XMIN, XMAX], YMIN, 0, color="#141b30", zorder=2)

    # korunanan varlık
    ax.plot(0, 0, marker="s", ms=13, mfc="#ffd166", mec="#ffffff", mew=1.2, zorder=6)
    ax.text(40, 45, "KORUNAN VARLIK", color="#ffd166", fontsize=9,
            fontweight="bold", zorder=6)

    # serpiciler
    for i, d in enumerate(C.DISPENSERS):
        ax.plot(*d["pos"], marker="^", ms=11, mfc="#7ae582", mec="#ffffff",
                mew=1.0, zorder=6)
        ax.text(d["pos"][0] - 60, d["pos"][1] + 40, f"SERPİCİ-{i + 1}",
                color="#7ae582", fontsize=8, fontweight="bold", zorder=6)

    # parçacıklar
    scat = ax.scatter([], [], s=[], c=[], alpha=0.85, zorder=4)

    # füze izi + gövde
    trail, = ax.plot([], [], color="#ff5964", lw=1.2, alpha=0.65, zorder=3)
    tri = Polygon([[0, 0], [0, 0], [0, 0]], closed=True, fc="#ff5964",
                  ec="#ffffff", lw=0.7, zorder=5)
    ax.add_patch(tri)

    hud_t = ax.text(0.02, 0.97, "", transform=ax.transAxes, color="#cfe3ff",
                    fontsize=10, family="monospace", va="top", zorder=7)
    title = ax.text(0.5, 1.03, "BULUT-KALKAN v0.1 — Elektron Bulut Aktif Koruma Simülatörü",
                    transform=ax.transAxes, ha="center", color="#e8f0ff",
                    fontsize=13, fontweight="bold", zorder=7)
    banner = ax.text(0.5, 0.12, "", transform=ax.transAxes, ha="center",
                     color="#ffffff", fontsize=17, fontweight="bold", zorder=8,
                     bbox=dict(boxstyle="round,pad=0.5", fc="#b02a37", ec="#ffffff"))

    def triangle_pts(x, y, h):
        L, W = 95.0, 38.0
        fwd = np.array([np.cos(h), np.sin(h)])
        side = np.array([-fwd[1], fwd[0]])
        return np.array([np.array([x, y]) + fwd * L,
                         np.array([x, y]) - fwd * L * 0.6 + side * W,
                         np.array([x, y]) - fwd * L * 0.6 - side * W])

    def density_field(pos, q):
        alive = np.abs(q) > 0.05
        if not alive.any():
            return np.zeros((GRID_Y, GRID_X))
        H, _, _ = np.histogram2d(pos[alive, 0], pos[alive, 1],
                                 bins=(GRID_X, GRID_Y),
                                 range=((XMIN, XMAX), (YMIN, YMAX)),
                                 weights=np.abs(q)[alive])
        return blur(H.T, passes=2)

    def update(fi):
        pos = res.cloud_pos[fi]
        q = res.cloud_q[fi]
        dens_img.set_data(density_field(pos, q))

        alive = np.abs(q) > 0.05
        n_alive = int(alive.sum())
        if n_alive:
            colors = np.where(q[alive] > 0, "#ff9f43", "#54a0ff")
            sizes = 6.0 + 26.0 * np.abs(q[alive])
            offs = pos[alive]
            scat.set_offsets(offs)
            scat.set_color(list(colors))
            scat.set_sizes(sizes)
        else:
            empty = np.empty((0, 2))
            scat.set_offsets(empty)

        mp = res.missile_pos[: fi + 1]
        trail.set_data([p[0] for p in mp], [p[1] for p in mp])
        mx, my = mp[-1]
        tri.set_xy(triangle_pts(mx, my, res.missile_heading[fi]))
        if res.lock[fi] <= 0.01:
            tri.set_fc("#8d99ae")

        burn_txt = ""
        if res.missile_burnout and res.t[fi] >= res.burn_time:
            burn_txt = "\n!! SEEKER YANDI !!"
        hud_t.set_text(
            f"t = {res.t[fi]:6.2f} s\n"
            f"füze hızı  : {C.MISSILE_SPEED:.0f} m/s\n"
            f"kilit      : %{res.lock[fi] * 100:5.1f}\n"
            f"sinyal kayb: %{res.att[fi] * 100:5.1f}\n"
            f"bulut bütünlüğü: %{res.integrity[fi] * 100:5.1f}{burn_txt}")

        if fi >= n_frames - 1:
            banner.set_text(res.outcome)
        return dens_img, scat, trail, tri, hud_t, banner

    anim = FuncAnimation(fig, update, frames=n_frames, interval=40, blit=False)

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    writer = FFMpegWriter(fps=25, bitrate=4200)
    print("Video render ediliyor...")
    anim.save(out, writer=writer)
    print(f"Video hazır: {out}")

    poster_path = os.path.join(os.path.dirname(out) or ".", "poster.png")
    update(n_frames - 1)
    fig.savefig(poster_path, facecolor=BG, bbox_inches="tight")
    print(f"Poster: {poster_path}")


if __name__ == "__main__":
    main()
