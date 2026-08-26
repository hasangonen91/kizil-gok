# -*- coding: utf-8 -*-
"""BULUT-KALKAN sinematik render: PIL kare kare compositing + ffmpeg pipe.
Kullanim: python3 render_cinematic.py [seed] [cikti.mp4]
"""
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim import config as C
from sim.engine import run

W, H = 1600, 900
FPS = 30
SCALE = 0.36
CX, CY = -1250.0, 380.0
LETTERBOX = 58

FONT_PATH = "/System/Library/Fonts/Menlo.ttc"
FONT_PATH2 = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(sz):
    try:
        return ImageFont.truetype(FONT_PATH, sz)
    except OSError:
        try:
            return ImageFont.truetype(FONT_PATH2, sz)
        except OSError:
            return ImageFont.load_default()


F_SMALL = font(17)
F_MED = font(21)
F_BIG = font(30)
F_HUGE = font(64)


def w2s(x, y):
    sx = W / 2 + (x - CX) * SCALE
    sy = H * 0.55 - (y - CY) * SCALE
    return sx, sy


def make_background(rng):
    yy = np.linspace(0.0, 1.0, H)[:, None]
    stops_y = np.array([0.0, 0.55, 0.80, 1.0])
    stops_c = np.array([[4, 6, 14], [10, 16, 34], [26, 34, 58], [52, 44, 52]],
                       dtype=np.float32)
    rows = np.stack([np.interp(yy[:, 0], stops_y, stops_c[:, k]) for k in range(3)],
                    axis=1)
    grad = np.repeat(rows[:, None, :], W, axis=1)
    img = Image.fromarray(grad.astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img)
    for _ in range(240):
        x = rng.integers(0, W)
        y = rng.integers(0, int(H * 0.62))
        b = int(rng.integers(40, 220))
        r = 1 if rng.random() < 0.85 else 2
        d.ellipse([x - r, y - r, x + r, y + r], fill=(b, b, min(255, b + 20)))
    mgx, mgy, mgr = int(W * 0.82), int(H * 0.16), 34
    for rr, cc in ((mgr * 3, (38, 44, 66)), (mgr * 2, (58, 64, 88)), (mgr, (188, 196, 214))):
        d.ellipse([mgx - rr, mgy - rr, mgx + rr, mgy + rr], fill=cc)
    d.ellipse([mgx - mgr + 9, mgy - mgr + 6, mgx + mgr - 2, mgy + mgr - 9], fill=(16, 20, 38))
    return img


def make_hills():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(7)
    for layer, col, base in ((0, (10, 14, 28, 255), 0.70), (1, (6, 9, 20, 255), 0.78)):
        pts = [(0, H)]
        yy = H * base
        xx = 0
        while xx <= W:
            yy += rng.normal(0, 14)
            yy = min(H * 0.92, max(H * 0.60, yy))
            pts.append((xx, yy))
            xx += 55
        pts.append((W, H))
        d.polygon(pts, fill=col)
    return img


def blob(radius, color, soft=2.4):
    sz = int(radius * 2)
    arr = np.zeros((sz, sz), dtype=np.float32)
    yy, xx = np.mgrid[0:sz, 0:sz]
    d2 = (xx - radius) ** 2 + (yy - radius) ** 2
    arr = np.exp(-d2 / (2 * (radius / soft) ** 2))
    a = (arr * 255).astype(np.uint8)
    rgba = np.zeros((sz, sz, 4), dtype=np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = color
    rgba[..., 3] = a
    return Image.fromarray(rgba, "RGBA")


SPRITES = {}
GLOWS = {}


def init_sprites():
    for q, col in ((1, (255, 178, 92)), (-1, (110, 185, 255))):
        for r in (5, 7, 9, 12):
            SPRITES[(q, r)] = blob(r, col, soft=2.0)
            GLOWS[(q, r)] = blob(r * 3, col, soft=3.2)


def draw_cloud(frame, pos, q, alpha_scale=1.0):
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(0, len(q), 2):
        qi = q[i]
        a = abs(qi)
        if a < 0.05:
            continue
        sx, sy = w2s(pos[i, 0], pos[i, 1])
        if -80 < sx < W + 80 and -80 < sy < H + 80:
            r = 5 if a < 0.5 else (9 if a < 1.2 else 12)
            gr = GLOWS[(1 if qi > 0 else -1, r)]
            ga = int(26 * a * alpha_scale)
            if ga > 0:
                tmp = gr.copy()
                tmp.putalpha(tmp.split()[3].point(lambda v: min(255, v * ga // 255)))
                glow.alpha_composite(tmp, (int(sx - tmp.width / 2), int(sy - tmp.height / 2)))
    frame.alpha_composite(glow)
    core = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for i in range(len(q)):
        qi = q[i]
        a = abs(qi)
        if a < 0.05:
            continue
        sx, sy = w2s(pos[i, 0], pos[i, 1])
        if -40 < sx < W + 40 and -40 < sy < H + 40:
            r = 5 if a < 0.5 else (7 if a < 1.0 else (9 if a < 1.6 else 12))
            sp = SPRITES[(1 if qi > 0 else -1, r)]
            ca = int(150 * min(1.4, a) * alpha_scale)
            tmp = sp.copy()
            tmp.putalpha(tmp.split()[3].point(lambda v: min(255, v * ca // 255)))
            core.alpha_composite(tmp, (int(sx - tmp.width / 2), int(sy - tmp.height / 2)))
    frame.alpha_composite(core)


def rot(pts, ang, ox, oy):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(ox + x * ca - y * sa, oy + x * sa + y * ca) for x, y in pts]


def draw_missile(frame, x, y, heading, lock, blinded, flame_on, tumble_ang=None):
    d = ImageDraw.Draw(frame, "RGBA")
    sx, sy = w2s(x, y)
    if blinded:
        sx += np.random.normal(0, 2.2)
        sy += np.random.normal(0, 2.2)
    ang = -heading if tumble_ang is None else -tumble_ang
    L, Wd = 21, 6
    body = rot([(-L, -Wd), (L * 0.4, -Wd), (L, 0), (L * 0.4, Wd), (-L, Wd), (-L * 0.7, 0)], ang, sx, sy)
    if flame_on:
        fl = (24 + np.random.uniform(0, 18)) * (1.0 if lock > 0.3 else 0.55)
        flame = rot([(-L, -5), (-L - fl, 0), (-L, 5)], ang, sx, sy)
        d.polygon(flame, fill=(255, 170, 60, 235))
        flame2 = rot([(-L, -2.5), (-L - fl * 0.6, 0), (-L, 2.5)], ang, sx, sy)
        d.polygon(flame2, fill=(255, 248, 220, 250))
        gx, gy = sx - math.cos(ang) * (L + 14), sy - math.sin(ang) * (L + 14)
        d.ellipse([gx - 13, gy - 13, gx + 13, gy + 13], fill=(255, 150, 50, 70))
    d.polygon(body, fill=(198, 205, 220, 255))
    d.line(body + [body[0]], fill=(240, 244, 252, 255), width=1)
    nose = rot([(L, 0), (L * 0.4, -Wd), (L * 0.4, Wd)], ang, sx, sy)
    d.polygon(nose, fill=(70, 76, 92, 255))
    return sx, sy


class Smoke:
    def __init__(self):
        self.items = []
        self.tick = 0

    def emit(self, x, y):
        self.tick += 1
        if self.tick % 3:
            return
        self.items.append([x + np.random.normal(0, 1.5), y + np.random.normal(0, 1.5), 0])

    def draw(self, frame, dt):
        dd = ImageDraw.Draw(frame, "RGBA")
        alive = []
        for it in self.items:
            it[0] += np.random.normal(0, 2.5) * dt * 6
            it[1] += (np.random.normal(0, 2.5) - 3 * dt) * 6 * dt
            it[2] += 1
            age = it[2]
            if age > 95:
                continue
            alive.append(it)
            sx, sy = w2s(it[0], it[1])
            r = 2.0 + age * 0.30
            a = max(0, int(58 - age * 0.62))
            if a > 0:
                dd.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(122, 127, 143, a))
        self.items = alive


def draw_asset(frame, fi, sweep_ang):
    d = ImageDraw.Draw(frame, "RGBA")
    bx, by = w2s(0, 0)
    sweep = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sweep)
    for k in range(10):
        a0 = sweep_ang - k * 3.2
        alpha = max(0, 26 - k * 2.4)
        sd.pieslice([bx - 110, by - 110, bx + 110, by + 110], a0, a0 + 3.4,
                    fill=(110, 235, 170, int(alpha)))
    frame.alpha_composite(sweep)
    d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(255, 209, 102, 255))
    d.rectangle([bx - 16, by - 3, bx + 16, by + 3], fill=(40, 48, 66, 255))
    d.polygon([(bx - 20, by), (bx + 20, by), (bx + 12, by + 16), (bx - 12, by + 16)],
              fill=(30, 36, 52, 255))
    blink = 255 if (fi // 15) % 2 == 0 else 60
    d.ellipse([bx - 2, by - 22, bx + 2, by - 18], fill=(255, 70, 70, blink))
    d.line([(bx, by - 4), (bx, by - 20)], fill=(90, 100, 120, 255), width=2)
    for dpos, name in ((C.DISPENSERS[0]["pos"], "S-1"), (C.DISPENSERS[1]["pos"], "S-2")):
        dx, dy = w2s(*dpos)
        d.polygon([(dx - 10, dy + 6), (dx, dy - 8), (dx + 10, dy + 6)], fill=(122, 229, 130, 255))
        d.rectangle([dx - 6, dy + 6, dx + 6, dy + 12], fill=(34, 42, 58, 255))


def hud(frame, fi, t, lock, att, integ, events, blinded, outcome_shown):
    d = ImageDraw.Draw(frame, "RGBA")
    d.rectangle([0, 0, W, LETTERBOX], fill=(0, 0, 0, 255))
    d.rectangle([0, H - LETTERBOX, W, H], fill=(0, 0, 0, 255))
    panel = (8, 12, 22, 170)
    d.rounded_rectangle([18, LETTERBOX + 12, 400, LETTERBOX + 128], 10, fill=panel, outline=(70, 90, 130, 160))
    d.text((34, LETTERBOX + 22), "BULUT-KALKAN C2", font=F_MED, fill=(140, 220, 255, 255))
    d.text((34, LETTERBOX + 52), f"T+{t:06.2f} SN", font=F_BIG, fill=(230, 240, 255, 255))
    d.text((34, LETTERBOX + 92), f"HUD: {HUD_STATE['mode']}", font=F_SMALL, fill=(150, 165, 195, 255))

    d.rounded_rectangle([W - 420, LETTERBOX + 12, W - 18, LETTERBOX + 128], 10, fill=panel, outline=(70, 90, 130, 160))
    bars = [("SEEKER KILIT", lock, (90, 220, 120), (220, 70, 70)),
            ("SINYAL GUCU", 1.0 - att, (90, 160, 240), (240, 150, 60)),
            ("BULUT BUTUNLUK", integ, (200, 170, 90), (200, 170, 90))]
    for i, (name, val, cg, cb) in enumerate(bars):
        yy = LETTERBOX + 30 + i * 32
        d.text((W - 404, yy), name, font=F_SMALL, fill=(170, 185, 210, 255))
        bx0, bx1, bw = W - 250, W - 34, 216
        d.rectangle([bx0, yy + 2, bx1, yy + 14], fill=(28, 34, 50, 220))
        col = cg if val > 0.5 else cb
        d.rectangle([bx0, yy + 2, bx0 + max(2, int(bw * max(0, val))), yy + 14], fill=col + (230,))
    d.text((34, H - LETTERBOX - 150), "OLAY KAYDI", font=F_SMALL, fill=(120, 200, 255, 230))
    for i, (tt, msg, hot) in enumerate(events[-6:]):
        col = (255, 120, 110, 255) if hot else (185, 200, 225, 235)
        d.text((34, H - LETTERBOX - 122 + i * 21), f"[{tt:06.2f}] {msg}", font=F_SMALL, fill=col)
    if blinded and (fi // 8) % 2 == 0:
        d.text((W / 2 - 130, LETTERBOX + 16), "! KILIT YOK !", font=F_BIG, fill=(255, 80, 70, 255))
    d.ellipse([W / 2 - 5, LETTERBOX + 8, W / 2 + 5, LETTERBOX + 18], fill=(255, 60, 60, 200))


HUD_STATE = {"mode": "TARAMA"}


def vignette_grain():
    yy, xx = np.mgrid[0:H, 0:W]
    cx, cy = W / 2, H / 2
    dist = np.sqrt(((xx - cx) / (W * 0.62)) ** 2 + ((yy - cy) / (H * 0.62)) ** 2)
    v = np.clip(1.0 - np.clip(dist - 0.55, 0, 1) * 0.85, 0, 1) ** 1.4
    grains = []
    g_rng = np.random.default_rng(3)
    for _ in range(4):
        g = g_rng.normal(0, 5.5, (H, W, 1))
        grains.append(g)
    return v[..., None].astype(np.float32), grains


def finish(frame_rgb, vig, grain, shake=(0, 0)):
    arr = np.asarray(frame_rgb, dtype=np.float32)
    arr = arr * vig + grain
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    out = Image.fromarray(arr, "RGB")
    if shake != (0, 0):
        base = Image.new("RGB", (W, H), (0, 0, 0))
        base.paste(out, shake)
        out = base
    d = ImageDraw.Draw(out)
    d.rectangle([0, 0, W, LETTERBOX], fill=(0, 0, 0))
    d.rectangle([0, H - LETTERBOX, W, H], fill=(0, 0, 0))
    return out


def title_card(sec, sub, alpha):
    img = Image.new("RGB", (W, H), (2, 3, 8))
    d = ImageDraw.Draw(img)
    a = int(255 * alpha)
    tw = d.textlength(sec, font=F_HUGE)
    d.text(((W - tw) / 2, H / 2 - 70), sec, font=F_HUGE, fill=(235, 242, 255) + ())
    d.text(((W - tw) / 2, H / 2 - 70), sec, font=F_HUGE, fill=(a, a, a))
    tw2 = d.textlength(sub, font=F_MED)
    d.text(((W - tw2) / 2, H / 2 + 20), sub, font=F_MED, fill=(int(a * 0.75), int(a * 0.8), int(a * 0.9)))
    return img


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 99
    out = sys.argv[2] if len(sys.argv) > 2 else "media/demo_sinematik.mp4"
    C.SEED = seed
    res = run(C)
    n = len(res.t)
    print(f"sim: {n} kare, {res.t[-1]:.1f}s, sonuc: {res.outcome}")

    rng = np.random.default_rng(seed)
    init_sprites()
    bg = make_background(rng)
    hills = make_hills()
    vig, grains = vignette_grain()

    events = [(res.t[0], "HV-HEDEF ALGILANDI — SERPICILER HAZIR", False)]
    entry_fi = next((i for i, a in enumerate(res.att) if a > 0.15), None)
    blind_fi = next((i for i, l in enumerate(res.lock) if l < 0.35), None)
    impact = res.missile_pos[-1][1] <= 1.0
    deploy_fi = next((i for i, t in enumerate(res.t) if t >= C.BULUT_DEPLOY_T), 0)
    end_fi = n - 1
    fired = set()

    smoke = Smoke()
    INTRO, OUTRO = 66, 100
    seq = []
    for i in range(INTRO):
        seq.append(("title", i))
    for i in range(n):
        seq.append(("sim", i))
        if entry_fi is not None and abs(i - entry_fi) < 55 and i % 2 == 0:
            seq.append(("sim", i))
    for i in range(OUTRO):
        seq.append(("outro", i))

    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = len(seq)
    shake = (0, 0)

    for idx, (kind, i) in enumerate(seq):
        if kind == "title":
            a = min(1.0, i / 18, (INTRO - i) / 18)
            img = title_card("BULUT-KALKAN", "ELEKTRON BULUT AKTIF KORUMA — KONSEPT DEMONSTRASYONU", max(0.0, a))
            proc.stdin.write(np.asarray(img).tobytes())
            continue
        if kind == "outro":
            j = i
            img = Image.new("RGB", (W, H), (2, 3, 8))
            d = ImageDraw.Draw(img)
            a = min(1.0, j / 20)
            col = (int(235 * a), int(240 * a), int(255 * a))
            msg = res.outcome
            tw = d.textlength(msg, font=F_HUGE)
            d.text(((W - tw) / 2, H / 2 - 90), msg, font=F_HUGE, fill=col)
            stats = [
                f"HEDEFE MIN MESAFE   : {res.min_dist:7.0f} m",
                f"BULUTTA KALMA       : {res.in_cloud_time:7.2f} sn",
                f"MAKS RF ZAYIFLAMA   : %{res.max_att * 100:5.1f}",
                f"BULUT BUTUNLUGU     : %{res.integrity[-1] * 100:5.1f}",
                f"TOHUM               : {seed}",
            ]
            for k, sline in enumerate(stats):
                d.text((W / 2 - 260, H / 2 + 6 + k * 30), sline, font=F_MED,
                       fill=(int(165 * a), int(180 * a), int(205 * a)))
            proc.stdin.write(np.asarray(img).tobytes())
            continue

        fi = i
        t = res.t[fi]
        frame = bg.copy().convert("RGBA")
        sweep = (fi * 4.1) % 360
        draw_asset(frame, fi, sweep)
        frame.alpha_composite(hills)

        pos = res.cloud_pos[fi]
        q = res.cloud_q[fi]
        alive = np.abs(q) > 0.05
        if alive.any() and fi >= deploy_fi:
            draw_cloud(frame, pos, q)

        mp = res.missile_pos[fi]
        if fi > deploy_fi:
            smoke.emit(mp[0], mp[1])
        smoke.draw(frame, C.DT * 2)

        blinded = res.lock[fi] < 0.45
        flame_on = not res.missile_burnout and mp[1] > 0.5
        tumble = res.missile_heading[fi] + (fi - res.burnout_frame) * 0.35 \
            if res.missile_burnout and res.burnout_frame else None
        draw_missile(frame, mp[0], mp[1], res.missile_heading[fi],
                     res.lock[fi], blinded, flame_on, tumble)

        if entry_fi is not None and entry_fi not in fired and fi >= entry_fi:
            events.append((t, "FUZE BULUTA GIRDİ — RF ZAYIFLAMA", False))
            fired.add(entry_fi)
        if blind_fi is not None and blind_fi not in fired and fi >= blind_fi:
            events.append((t, "SEEKER KILIT KAYBI — YANILSAMA BASLADI", True))
            fired.add(blind_fi)
        if res.missile_burnout and res.burn_time and res.burn_time not in [e[0] for e in events]:
            events.append((res.burn_time, "SEEKER YANDI — INDUKSIYON AKIMI", True))
        if fi == end_fi:
            tag = "YER TEMASI — FUZE ETKISIZ" if impact else "HEDEF KAÇIRDI"
            events.append((t, tag + " | " + res.outcome, True))

        HUD_STATE["mode"] = "ANGAJMAN" if (entry_fi and fi >= entry_fi) else "TARAMA"
        frame = frame.convert("RGB")

        if entry_fi is not None and entry_fi - 10 <= fi <= min(n - 1, entry_fi + 120):
            zt = min(1.0, max(0.0, 1 - abs(fi - (entry_fi + 55)) / 65.0))
            z = 1.0 + 0.30 * zt
            cw, ch = int(W / z), int(H / z)
            mx, my = w2s(mp[0], mp[1])
            cx = int(min(max(mx, cw / 2), W - cw / 2))
            cy = int(min(max(my, ch / 2), H - ch / 2))
            frame = frame.crop((cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2)) \
                .resize((W, H), Image.Resampling.LANCZOS)

        hud(frame, fi, t, res.lock[fi], res.att[fi], res.integrity[fi], events, blinded, False)

        if fi == end_fi and impact:
            shake = (int(np.random.uniform(-7, 7)), int(np.random.uniform(-5, 5)))
        elif shake != (0, 0):
            shake = (int(shake[0] * 0.75), int(shake[0] * 0.75))

        g = grains[fi % len(grains)]
        out_img = finish(frame, vig, g, shake)
        proc.stdin.write(np.asarray(out_img).tobytes())
        if idx % 100 == 0:
            print(f"render %{100 * idx // total}", flush=True)

    proc.stdin.close()
    proc.wait()
    print(f"video hazir: {out} ({total} kare, {total / FPS:.1f}s)")


if __name__ == "__main__":
    main()
