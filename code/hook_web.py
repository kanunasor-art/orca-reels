"""Reels 15 — web design hook in the dark flat 'farazisenaryo' style.
Cursor glides toward 'SATIN AL', freezes 1 px before the click; word-by-word captions.
Usage: python3 hook_web.py [--stills]"""
import math
import random
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from engine import FPS, H, W, paste, prog, rrect

OSW = "/home/claude/reels/Oswald-Bold.ttf"
INTER = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
RED, BLUE, WHITE = (229, 57, 53), (66, 165, 245), (236, 239, 241)
MUT, BG = (120, 130, 150), (13, 14, 20)
FREEZE = 4.6
VO_START = 5.2
DUR = 18.0


def F(size, f=OSW):
    return ImageFont.truetype(f, size)


# ---------------------------------------------------------------- static night city
def make_city():
    random.seed(3)
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for layer, (shade, top, wmin) in enumerate([((20, 22, 32), 380, 90), ((26, 28, 40), 620, 120)]):
        x = -20
        while x < W:
            w = random.randint(wmin, wmin + 120)
            t = top + random.randint(0, 260)
            d.rectangle([x, t, x + w, H], fill=shade)
            for wy in range(t + 20, H - 200, 34):
                for wx in range(x + 12, x + w - 12, 26):
                    r = random.random()
                    if r < 0.06:
                        d.rectangle([wx, wy, wx + 10, wy + 14], fill=(200, 160, 80))
                    elif r < 0.5:
                        d.rectangle([wx, wy, wx + 10, wy + 14], fill=(34, 37, 52))
            x += w + random.randint(4, 18)
    # row of red aviation lights like the reference
    for k in range(0, W, 46):
        d.ellipse([k + 8, 1092, k + 18, 1102], fill=(150, 40, 36))
    return img


CITY = make_city()


# ---------------------------------------------------------------- the website (a lit window)
SX, SY, SW, SH = 150, 560, 780, 760          # browser window on screen


def make_site(loading_p):
    lay = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([0, 0, SW - 1, SH - 1], radius=26, fill=(232, 234, 238))
    d.rounded_rectangle([0, 0, SW - 1, 70], radius=26, fill=(200, 204, 212))
    d.rectangle([0, 40, SW - 1, 70], fill=(200, 204, 212))
    for i, c in enumerate([(239, 83, 80), (255, 202, 40), (102, 187, 106)]):
        d.ellipse([24 + i * 34, 24, 46 + i * 34, 46], fill=c)
    d.rounded_rectangle([150, 18, SW - 30, 52], radius=17, fill=(240, 242, 245))
    d.text((170, 22), "senin-siten.com", font=F(22, INTER), fill=(110, 115, 125))
    # page skeleton (still loading = grey blocks)
    g = (205, 209, 216)
    d.rounded_rectangle([40, 110, SW - 40, 330], radius=18, fill=g)
    d.rounded_rectangle([40, 360, 380, 400], radius=10, fill=g)
    d.rounded_rectangle([40, 420, SW - 200, 450], radius=10, fill=g)
    d.rounded_rectangle([40, 470, SW - 260, 500], radius=10, fill=g)
    # buy button
    d.rounded_rectangle([40, 560, 400, 660], radius=22, fill=(30, 136, 229))
    d.text((92, 578), "SATIN AL", font=F(54), fill=WHITE)
    # loading bar at the top, stuck near the end
    d.rectangle([0, 70, int(SW * loading_p), 76], fill=(30, 136, 229))
    return lay


BTN = (SX + 40, SY + 560, SX + 400, SY + 660)      # button rect on screen


def cursor_pos(t):
    t = min(t, FREEZE)
    e = 1 - (1 - t / FREEZE) ** 2.6                 # crawls at the end
    x0, y0 = 880, 1500
    x1, y1 = BTN[2] + 1, BTN[1] + 40                 # 1 px right of the button edge
    return x0 + (x1 - x0) * e, y0 + (y1 - y0) * e


def draw_cursor(img, x, y, s=1.7):
    pts = [(0, 0), (0, 34), (9, 26), (15, 40), (21, 37), (15, 24), (27, 24)]
    pts = [(x + px * s, y + py * s) for px, py in pts]
    d = ImageDraw.Draw(img)
    d.polygon([(px + 4, py + 4) for px, py in pts], fill=(0, 0, 0))
    d.polygon(pts, fill=WHITE, outline=(0, 0, 0))


def spinner(img, t, cx, cy):
    d = ImageDraw.Draw(img)
    a = (min(t, FREEZE) * 300) % 360
    d.arc([cx - 40, cy - 40, cx + 40, cy + 40], a, a + 280, fill=(30, 136, 229), width=9)


def callout(img, label, val, x, y, col=RED):
    """Reference-style tag: pill with a thin line pointing down."""
    f = F(30)
    w = int(f.getlength(label + " " + val)) + 40
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x - w / 2, y - 26, x + w / 2, y + 26], radius=26, fill=(18, 18, 24),
                        outline=(230, 230, 230), width=2)
    lw = f.getlength(label + " ")
    d.text((x - w / 2 + 20, y - 21), label, font=f, fill=WHITE)
    d.text((x - w / 2 + 20 + lw, y - 21), val, font=f, fill=col)
    d.line([(x, y + 26), (x, y + 70)], fill=(230, 230, 230), width=2)
    d.ellipse([x - 5, y + 66, x + 5, y + 76], fill=(230, 230, 230))


def hud(img, t):
    d = ImageDraw.Draw(img)
    tt = min(t, FREEZE)
    d.text((44, 120), "ZİYARETÇİ 1 / 1", font=F(28), fill=MUT)
    d.text((44, 152), f"00:0{int(tt)}" if tt < 10 else "00:10", font=F(84), fill=WHITE)
    d.text((44, 252), "SAYFA: SEPET", font=F(28), fill=MUT)
    sab = max(0.0, 3.0 - tt * 0.63)
    d.text((44, 286), "SABIR: ", font=F(28), fill=MUT)
    d.text((44 + F(28).getlength("SABIR: "), 286), f"{sab:.1f} SN", font=F(28),
           fill=RED if sab < 1.2 else (255, 202, 40))


# word-by-word captions; post-freeze groups are timed to real pauses in vo15.mp3
import reels2
reels2.LINES[15] = ["Ama siten üç saniyedir açılmıyor.", "Ziyaretçilerin yarısı tam burada gidiyor.",
                    "Hızlı ve güçlü tasarım satış getirir.", "Siteni ücretsiz inceleyelim. DM'den WEB yaz."]
_c, _d = reels2.cues_for(15)
_c = [VO_START + x for x in _c] + [VO_START + _d]
GROUPS = [[("AMA", []), ("SİTEN", ["SİTEN"]), ("3 SANİYEDİR", ["3"]), ("AÇILMIYOR.", ["AÇILMIYOR."])],
          [("ZİYARETÇİLERİN", []), ("YARISI", ["YARISI"]), ("TAM BURADA GİDİYOR.", ["GİDİYOR."])],
          [("HIZLI VE", ["HIZLI"]), ("GÜÇLÜ TASARIM", ["TASARIM"]), ("SATIŞ GETİRİR.", ["SATIŞ"])]]
CAPS = [(0.0, 1.4, "BİR ZİYARETÇİ", []), (1.4, 2.6, "SATIN ALMAK", ["SATIN"]), (2.6, 4.6, "ÜZERE", [])]
for gi, g in enumerate(GROUPS):
    a0, a1 = _c[gi], _c[gi + 1]
    step = (a1 - a0) / len(g)
    for k, (txt, hi) in enumerate(g):
        CAPS.append((a0 + k * step, a0 + (k + 1) * step, txt, hi))
CTA_AT = _c[3]


def caption(img, t):
    for a, b, s, hi in CAPS:
        if a <= t < b:
            f = F(96)
            words = s.split(" ")
            total = sum(f.getlength(w) for w in words) + f.getlength(" ") * (len(words) - 1)
            x = (W - total) / 2
            p = prog(t, a, 0.12)
            y = 1560 + (1 - p) * 16
            d = ImageDraw.Draw(img)
            for w in words:
                col = (RED if w not in ("SİTEN", "HIZLI", "TASARIM", "SATIŞ") else BLUE) if w in hi else WHITE
                d.text((x + 4, y + 5), w, font=f, fill=(0, 0, 0))
                d.text((x, y), w, font=f, fill=col)
                x += f.getlength(w + " ")


def cta(img, t, s):
    d = ImageDraw.Draw(img)
    img.paste(Image.blend(img, Image.new("RGB", (W, H), BG), 0.8))
    p = prog(t, s, 0.3)
    f = F(110)
    for k, (txt, col) in enumerate([("SİTEN", WHITE), ("SATIŞ GETİRSİN.", BLUE)]):
        w = f.getlength(txt)
        d.text(((W - w) / 2, 560 + k * 130 + (1 - p) * 20), txt, font=f, fill=col)
    p2 = prog(t, s + 0.5, 0.3)
    if p2 > 0:
        lab = "DM'E \"WEB\" YAZ"
        f2 = F(64)
        w = f2.getlength(lab) + 90
        box_ = rrect(int(w), 120, 60, RED)
        paste(img, box_, (W - w) / 2, 900, p2)
        d.text(((W - f2.getlength(lab)) / 2, 918), lab, font=f2, fill=WHITE)
    p3 = prog(t, s + 0.9, 0.3)
    if p3 > 0:
        for k, (txt, ff, col) in enumerate([("ORCA SOFTWARE", F(60), WHITE),
                                             ("orcasoftware.com.tr", F(36, INTER), MUT)]):
            w = ff.getlength(txt)
            d.text(((W - w) / 2, 1120 + k * 80), txt, font=ff, fill=col)


def scene(t):
    img = CITY.copy()
    load = 0.2 + 0.7 * (1 - (1 - min(t, FREEZE) / FREEZE) ** 3)
    site = make_site(min(load, 0.93))
    # site glow
    paste(img, rrect(SW + 60, SH + 60, 50, (60, 120, 220, 40)), SX - 30, SY - 30)
    paste(img, site, SX, SY)
    spinner(img, t, SX + SW / 2, SY + 220)
    cx, cy = cursor_pos(t)
    gap = max(1, int(cx - BTN[2]))
    if t > 1.2:
        callout(img, "MESAFE:", f"{gap} PX", cx + 30, cy - 120)
    draw_cursor(img, cx, cy)
    if t >= FREEZE:
        dt = t - FREEZE
        frozen = img
        if dt < 0.3:
            sx = int(math.sin(dt * 90) * 12 * (1 - dt / 0.3))
            out = Image.new("RGB", (W, H), BG)
            out.paste(frozen, (sx, 0))
            img = Image.blend(out, Image.new("RGB", (W, H), (255, 255, 255)), max(0, 0.55 - dt * 2))
        else:
            g = np.asarray(frozen).astype(float)
            grey = g.mean(axis=2, keepdims=True)
            k = min(0.75, (dt - 0.3) * 1.5)
            img = Image.fromarray((g * (1 - k) + grey * k * 0.6).clip(0, 255).astype("uint8"))
        if _c[1] <= t < _c[2]:      # cursor gives up and leaves
            img2 = img
            lp = prog(t, _c[2] - 1.0, 1.0)
            if lp > 0:
                img2 = Image.blend(img, Image.new("RGB", (W, H), BG), lp * 0.5)
            img = img2
    hud(img, t)
    caption(img, t)
    if t >= CTA_AT:
        cta(img, t, CTA_AT)
    return img


def sfx(path):
    sr = 44100
    n = int(DUR * sr)
    a = np.zeros(n)
    tt = 0.3
    while tt < FREEZE:
        i = int(tt * sr)
        L = int(0.03 * sr)
        a[i:i + L] += 0.3 * np.exp(-np.linspace(0, 8, L)) * np.sin(2 * np.pi * 1800 * np.arange(L) / sr)
        tt += max(0.14, 0.5 - 0.08 * tt)
    i = int(FREEZE * sr)
    L = int(1.0 * sr)
    x = np.arange(L) / sr
    a[i:i + L] += 0.7 * (np.sin(2 * np.pi * 50 * x) + 0.4 * np.random.randn(L) * np.exp(-x * 25)) * np.exp(-x * 3)
    j = int((FREEZE + 0.4) * sr)
    x = np.arange(n - j) / sr
    a[j:] += 0.07 * (np.sin(2 * np.pi * 65 * x) + 0.5 * np.sin(2 * np.pi * 97.5 * x)) * np.minimum(1, x / 2)
    for c in [a for a in [s[0] for s in CAPS] if a > FREEZE]:        # soft hit on each caption
        i = int(c * sr)
        L = int(0.12 * sr)
        a[i:i + L] += 0.18 * np.exp(-np.linspace(0, 10, L)) * np.sin(2 * np.pi * 120 * np.arange(L) / sr)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    if "--stills" in sys.argv:
        for tt in [0.0, 2.5, 4.4, 5.6, 8.8, 11.5, 15.3, 17.6]:
            scene(tt).save(f"stills/w15_{tt:04.1f}.png")
    else:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "out/w15_sfx.wav", "-i", "vo15.mp3",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
               "-filter_complex", f"[2:a]adelay={int(VO_START*1000)}|{int(VO_START*1000)},apad[vo];[1:a][vo]amix=inputs=2:duration=first:normalize=0[a]", "-map", "0:v", "-map", "[a]", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
               "out/orca_reels_15_hook_web.mp4"]
        sfx("out/w15_sfx.wav")
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for k in range(int(DUR * FPS)):
            p.stdin.write(scene(k / FPS).tobytes())
        p.stdin.close()
        p.wait()
        print("done")
