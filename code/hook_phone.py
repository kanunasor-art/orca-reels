"""Hook Reels 14: phone falls in slow motion, freezes 1 cm above the floor.
Usage: python3 hook_phone.py [--stills]"""
import math
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from engine import (CYAN, DARK, FPS, GREEN, H, MUTED, RED, W, WHITE, box, brand_chip,
                    cta_scene, font, headline, paste, prog, rrect, text, text_w)
import reels2

FREEZE = 4.9          # moment of the freeze (seconds)
VO_START = 5.4        # voiceover starts after the freeze
FLOOR_Y = 1480        # floor line
LINES = ["Bu telefonun düşmesini beş saniyedir izliyorsun.",
         "Müşterin de mesajına cevap beklerken tam olarak bunu yapıyor.",
         "Cevap gecikirse, müşteri düşer gider.",
         "Yapay zeka asistanı saniyesinde cevap verir.",
         "Telefonun yere düşmesin. DM'den AI yaz."]


# ---------------------------------------------------------------- static layers
def make_room():
    y = np.linspace(0, 1, H)[:, None]
    top = np.array([4, 6, 12], float)
    mid = np.array([14, 18, 30], float)
    grad = np.where(y[..., None] < FLOOR_Y / H,
                    top + (mid - top) * (y[..., None] / (FLOOR_Y / H)),
                    mid * 0.55)
    grad = np.repeat(grad, W, axis=1)
    yy, xx = np.mgrid[0:H, 0:W]
    # spotlight cone from top
    d = np.sqrt(((xx - 560) / 420.0) ** 2 + ((yy - 900) / 900.0) ** 2)
    g = np.clip(1 - d, 0, 1) ** 2 * 0.22
    grad = grad + g[..., None] * np.array([90, 120, 160])
    img = Image.fromarray(grad.clip(0, 255).astype("uint8"), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    # floor sheen
    for k in range(60):
        a = int(40 * (1 - k / 60))
        d.line([(0, FLOOR_Y + k * 7), (W, FLOOR_Y + k * 7)], fill=(120, 150, 200, a // 6))
    d.line([(0, FLOOR_Y), (W, FLOOR_Y)], fill=(70, 90, 130, 160), width=3)
    return img


ROOM = make_room()


def make_phone():
    pw, ph = 300, 610
    lay = Image.new("RGBA", (pw + 40, ph + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([20, 20, 20 + pw, 20 + ph], radius=52, fill=(18, 18, 22),
                        outline=(90, 95, 110), width=5)
    d.rounded_rectangle([34, 34, 6 + pw, 6 + ph], radius=42, fill=(10, 14, 24))
    d.rounded_rectangle([20 + pw / 2 - 45, 48, 20 + pw / 2 + 45, 72], radius=12,
                        fill=(0, 0, 0))
    d.text((20 + pw / 2 - 52, 120), "03:07", font=font("pb", 64), fill=WHITE)
    # notification card
    d.rounded_rectangle([46, 250, pw - 6, 380], radius=24, fill=(32, 44, 70))
    d.ellipse([62, 272, 112, 322], fill=GREEN)
    d.text((126, 268), "Yeni müşteri", font=font("isb", 26), fill=WHITE)
    d.text((126, 304), "Fiyat alabilir miyim?", font=font("ir", 22), fill=(203, 213, 225))
    d.text((126, 340), "şimdi", font=font("ir", 20), fill=MUTED)
    # screen glow
    glow = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([34, 34, 6 + pw, 6 + ph], radius=42,
                                           fill=(60, 130, 255, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    out = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(lay)
    return out


PHONE = make_phone()
PHONE = PHONE.resize((int(PHONE.size[0] * 1.25), int(PHONE.size[1] * 1.25)), Image.LANCZOS)
random.seed(7)
DUST = [(random.uniform(150, 950), random.uniform(500, 1450), random.uniform(1.5, 4),
         random.uniform(-6, 6), random.uniform(-12, -3)) for _ in range(70)]


# ---------------------------------------------------------------- phone motion
def phone_state(t):
    """Returns (cx, cy, angle). Slides on desk, then falls with slow-motion easing."""
    t = min(t, FREEZE)
    f = t / FREEZE                            # 0..1 fall progress
    e = 1 - (1 - f) ** 2.2                    # fast start, crawling end = slow-mo
    cx = 470 + 90 * e
    top_y = 470
    bottom_cy = FLOOR_Y - 431 - 12            # ~1 cm gap at freeze
    cy = top_y + (bottom_cy - top_y) * e
    ang = -4 - 26 * e
    return cx, cy, ang


def draw_phone(img, t, alpha=1.0, blur=True):
    cx, cy, ang = phone_state(t)
    ph = PHONE.rotate(ang, resample=Image.BICUBIC, expand=True)
    # reflection on the floor
    refl = ph.transpose(Image.FLIP_TOP_BOTTOM)
    ra = refl.getchannel("A").point(lambda v: int(v * 0.22))
    refl.putalpha(ra)
    ry = 2 * FLOOR_Y - (cy + ph.size[1] / 2)
    if ry < FLOOR_Y + 600:
        paste(img, refl, cx - refl.size[0] / 2, ry, alpha)
    # motion trail while falling fast
    if blur and t < FREEZE - 0.8:
        for k, a in ((3, 0.12), (2, 0.2), (1, 0.32)):
            tx, ty, tang = phone_state(t - k / FPS * 1.5)
            trail = PHONE.rotate(tang, resample=Image.BICUBIC, expand=True)
            paste(img, trail, tx - trail.size[0] / 2, ty - trail.size[1] / 2, a * alpha)
    paste(img, ph, cx - ph.size[0] / 2, cy - ph.size[1] / 2, alpha)
    # contact shadow grows as it gets closer
    gap = FLOOR_Y - (cy + 431)
    k = max(0.0, 1 - gap / 900)
    sh = Image.new("RGBA", (500, 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([0, 0, 499, 79], fill=(0, 0, 0, int(170 * k)))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    paste(img, sh, cx - 250, FLOOR_Y - 30)


def draw_dust(img, t):
    d = ImageDraw.Draw(img, "RGBA")
    tt = min(t, FREEZE)
    for x, y, r, vx, vy in DUST:
        yy = (y + vy * tt) % 1000 + 450
        xx = x + vx * tt
        d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(200, 220, 255, 70))


def gap_label(img, t):
    """Tiny measurement marker between phone and floor — feeds the tension."""
    cx, cy, _ = phone_state(t)
    gap = FLOOR_Y - (cy + 431)
    if gap > 260:
        return
    a = min(1.0, (260 - gap) / 120)
    d = ImageDraw.Draw(img, "RGBA")
    x = cx + 290
    d.line([(x, cy + 416), (x, FLOOR_Y)], fill=(239, 68, 68, int(255 * a)), width=4)
    d.line([(x - 18, FLOOR_Y), (x + 18, FLOOR_Y)], fill=(239, 68, 68, int(255 * a)), width=4)
    cm = max(1, round(gap / 12))
    text(img, f"{cm} cm", "pb", 46, x + 24, (cy + 416 + FLOOR_Y) / 2 - 30, 220, color=RED,
         align="left", alpha=a)


def watch_counter(img, t):
    """'izliyorsun 4.9 sn' pill, like the reference's live watch-time counter."""
    secs = t
    lab = f"izliyorsun  {secs:4.1f} sn"
    w = int(text_w(lab, "isb", 30)) + 70
    box(img, (W - w) / 2, 236, w, 60, r=30, fill=(255, 255, 255, 18),
        outline=(255, 255, 255, 50), width=2)
    d = ImageDraw.Draw(img)
    d.ellipse([(W - w) / 2 + 24, 258, (W - w) / 2 + 40, 274], fill=RED)
    text(img, lab, "isb", 30, (W - w) / 2 + 30, 247, w - 30, color=WHITE)


def frozen_frame(t):
    img = ROOM.copy()
    draw_dust(img, FREEZE)
    draw_phone(img, FREEZE, blur=False)
    gap_label(img, FREEZE)
    return img


FROZEN = None


def scene(img, t, cues):
    global FROZEN
    if t < FREEZE:
        img.paste(ROOM)
        draw_dust(img, t)
        draw_phone(img, t)
        gap_label(img, t)
        return
    # ---- frozen world
    if FROZEN is None:
        FROZEN = frozen_frame(FREEZE)
    dt = t - FREEZE
    base = FROZEN
    if dt < 0.35:                               # freeze punch: flash + shake
        sx = int(math.sin(dt * 90) * 14 * (1 - dt / 0.35))
        img.paste(base, (sx, 0))
        fl = Image.new("RGB", (W, H), (255, 255, 255))
        img.paste(Image.blend(img, fl, max(0, 0.6 - dt * 2)))
    else:
        dim = min(0.35, (dt - 0.35) * 0.9)
        img.paste(Image.blend(base, Image.new("RGB", (W, H), (2, 4, 10)), dim))
    watch_counter(img, min(t, FREEZE + 0.0) if dt > 0 else t)
    if t < VO_START:
        return
    i, s = reels2.scene_at(t - VO_START, cues)
    s += VO_START
    if i == 0:
        headline(img, "Bu telefonu\n**5 saniyedir** izliyorsun.", t, s, y=330)
    elif i == 1:
        headline(img, "Müşterin de cevap beklerken\n**tam olarak bunu** yapıyor.", t, s,
                 y=330, size=64)
    elif i == 2:
        headline(img, "Cevap gecikirse\n**müşteri düşer gider.**", t, s, y=330)
    elif i == 3:
        headline(img, "AI asistan\n**saniyesinde** cevap verir.", t, s, y=330)
        p = prog(t, s + 0.2, 0.4)
        box(img, 140, 760, 800, 150, r=36, fill=(20, 83, 45), outline=GREEN, width=3,
            alpha=p)
        text(img, "03:07  ·  Cevap gönderildi ✓", "isb", 40, 140, 812, 800, alpha=p)
    else:
        img.paste(Image.blend(img, Image.new("RGB", (W, H), (4, 8, 18)), 0.75))
        cta_scene(img, t, s, "Telefonun\n**yere düşmesin.**", "DM'den yaz:", "AI",
                  "Ücretsiz analiz")


def render_all(cues, vlen, out):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset",
           "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(int(round(vlen * FPS))):
        t = k / FPS
        img = Image.new("RGB", (W, H))
        scene(img, t, cues)
        brand_chip(img)
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()


def sfx(path, vlen):
    """Ticking clock during the fall (speeding up), a hard 'freeze' hit, low drone after."""
    sr = 44100
    n = int(vlen * sr)
    a = np.zeros(n)
    t = 0.3
    while t < FREEZE:
        i = int(t * sr)
        L = int(0.025 * sr)
        env = np.exp(-np.linspace(0, 9, L))
        a[i:i + L] += 0.35 * env * np.sin(2 * np.pi * 2200 * np.arange(L) / sr)
        t += max(0.16, 0.55 - 0.08 * t)
    i = int(FREEZE * sr)
    L = int(0.9 * sr)
    tt = np.arange(L) / sr
    hit = (np.sin(2 * np.pi * 55 * tt) + 0.5 * np.random.randn(L) * np.exp(-tt * 30))
    a[i:i + L] += 0.7 * hit * np.exp(-tt * 3.5)
    j = int((FREEZE + 0.3) * sr)
    tt = np.arange(n - j) / sr
    a[j:] += 0.06 * np.sin(2 * np.pi * 73 * tt) * np.minimum(1, tt / 1.5)
    a = np.clip(a, -1, 1)
    import wave
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((a * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    reels2.LINES[14] = LINES
    cues, vodur = reels2.cues_for(14)
    vlen = round(VO_START + vodur + 1.0, 2)
    if "--stills" in sys.argv:
        for tt in [0.0, 2.0, 3.8, 4.6, 5.0, 5.3] + [VO_START + c + 1.5 for c in cues]:
            img = Image.new("RGB", (W, H))
            scene(img, tt, cues)
            brand_chip(img)
            img.save(f"stills/h14_{tt:05.1f}.png")
        print(cues, vodur, vlen)
    else:
        render_all(cues, vlen, "out/hook_phone_raw.mp4")
        sfx("out/hook_phone_sfx.wav", vlen)
        subprocess.check_call([
            "ffmpeg", "-y", "-loglevel", "error", "-i", "out/hook_phone_raw.mp4",
            "-i", "out/hook_phone_sfx.wav", "-i", "vo14.mp3", "-filter_complex",
            f"[2:a]adelay={int(VO_START * 1000)}|{int(VO_START * 1000)},apad[vo];"
            "[1:a][vo]amix=inputs=2:duration=first:normalize=0[a]",
            "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", "out/orca_reels_14_hook_telefon_sesli.mp4"])
        print("done", vlen)
