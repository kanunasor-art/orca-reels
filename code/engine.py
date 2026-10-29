"""ORCA Reels video engine: PIL frame rendering piped to ffmpeg (1080x1920, 30fps)."""
import math
import subprocess
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30

GF = "/usr/share/fonts/truetype/google-fonts/"
IF = "/usr/share/fonts/opentype/inter/"
FONTS = {
    "pb": GF + "Poppins-Bold.ttf",
    "pm": GF + "Poppins-Medium.ttf",
    "ir": IF + "Inter-Regular.otf",
    "im": IF + "Inter-Medium.otf",
    "isb": IF + "Inter-SemiBold.otf",
    "ib": IF + "Inter-Bold.otf",
}

# Palette
BG1 = (6, 10, 22)
BG2 = (12, 22, 48)
CARD = (17, 27, 53)
CARD2 = (25, 38, 72)
STROKE = (48, 66, 110)
CYAN = (34, 211, 238)
BLUE = (59, 130, 246)
GREEN = (34, 197, 94)
RED = (239, 68, 68)
YELLOW = (250, 204, 21)
TG = (41, 170, 225)
WHITE = (241, 245, 249)
MUTED = (148, 163, 184)
DARK = (8, 13, 28)


@lru_cache(maxsize=None)
def font(name, size):
    return ImageFont.truetype(FONTS[name], size)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, start, dur=0.45):
    """Ease-out cubic progress of an animation starting at `start`."""
    x = clamp((t - start) / dur)
    return 1 - (1 - x) ** 3


def lerp(a, b, p):
    return a + (b - a) * p


# ---------------------------------------------------------------- compositing
@lru_cache(maxsize=256)
def _lut(alpha_q):
    a = alpha_q / 100.0
    return [int(v * a) for v in range(256)]


def paste(base, layer, x, y, alpha=1.0):
    if alpha <= 0.01:
        return
    if alpha < 0.99:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(_lut(int(alpha * 100))))
    base.paste(layer, (int(round(x)), int(round(y))), layer)


# ---------------------------------------------------------------- background
@lru_cache(maxsize=1)
def background():
    y = __import__("numpy").linspace(0, 1, H)[:, None]
    np = __import__("numpy")
    top = np.array(BG1, float)
    bot = np.array(BG2, float)
    grad = (top[None, None, :] * (1 - y[..., None]) + bot[None, None, :] * y[..., None])
    grad = np.repeat(grad, W, axis=1)
    # soft cyan glow top-right and blue glow bottom-left
    yy, xx = np.mgrid[0:H, 0:W]
    for cx, cy, r, col, k in ((900, 300, 650, CYAN, 0.10), (150, 1650, 750, BLUE, 0.12)):
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
        g = np.clip(1 - d, 0, 1) ** 2 * k
        grad = grad * (1 - g[..., None]) + np.array(col, float)[None, None, :] * g[..., None]
    img = Image.fromarray(grad.clip(0, 255).astype("uint8"), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    for gx in range(0, W, 90):
        d.line([(gx, 0), (gx, H)], fill=(255, 255, 255, 7), width=1)
    for gy in range(0, H, 90):
        d.line([(0, gy), (W, gy)], fill=(255, 255, 255, 7), width=1)
    return img


# ---------------------------------------------------------------- text
def _parse(text, color, accent):
    """'**' toggles accent colour. Returns list of lines, each a list of (word, colour)."""
    lines = []
    acc = False
    for raw_line in text.split("\n"):
        words = []
        parts = raw_line.split("**")
        for i, part in enumerate(parts):
            if i > 0:
                acc = not acc
            for w in part.split(" "):
                if w:
                    words.append((w, accent if acc else color))
        lines.append(words)
    return lines


@lru_cache(maxsize=512)
def text_layer(text, fname, size, max_w, color=WHITE, accent=CYAN, align="center", spacing=1.18):
    f = font(fname, size)
    space = f.getlength(" ")
    lh = int(size * spacing)
    out_lines = []
    for words in _parse(text, color, accent):
        cur, cur_w = [], 0
        for w, c in words:
            wl = f.getlength(w)
            add = wl if not cur else space + wl
            if cur and cur_w + add > max_w:
                out_lines.append((cur, cur_w))
                cur, cur_w = [(w, c)], wl
            else:
                cur.append((w, c))
                cur_w += add
        out_lines.append((cur, cur_w))
    h = lh * len(out_lines) + int(size * 0.35)
    layer = Image.new("RGBA", (max_w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i, (words, lw) in enumerate(out_lines):
        if align == "center":
            x = (max_w - lw) / 2
        elif align == "right":
            x = max_w - lw
        else:
            x = 0
        for w, c in words:
            d.text((x, i * lh), w, font=f, fill=c)
            x += f.getlength(w) + space
    return layer


def text(base, s, fname, size, x, y, max_w, color=WHITE, accent=CYAN, align="center",
         alpha=1.0, spacing=1.18):
    """x is the left edge of the text box (width max_w). Returns rendered height."""
    lay = text_layer(s, fname, size, int(max_w), color, accent, align, spacing)
    paste(base, lay, x, y, alpha)
    return lay.size[1]


def text_w(s, fname, size):
    return font(fname, size).getlength(s)


def headline(base, s, t, start, first=False, y=330, size=76):
    """Scene headline in the top safe zone. `first` = fully visible at frame 0 (cover)."""
    p = 1.0 if first else prog(t, start, 0.35)
    return text(base, s, "pb", size, 80, y + (1 - p) * 30, 920, alpha=p, spacing=1.16)


def brand_chip(base):
    lay = _brand_chip()
    paste(base, lay, 80, 236, 0.9)


@lru_cache(maxsize=1)
def _brand_chip():
    f = font("isb", 28)
    label = "ORCA Software"
    w = int(f.getlength(label)) + 64
    lay = Image.new("RGBA", (w, 50), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([0, 0, w - 1, 49], radius=25, fill=(255, 255, 255, 14),
                        outline=(255, 255, 255, 40), width=2)
    d.ellipse([18, 18, 32, 32], fill=CYAN)
    d.text((42, 9), label, font=f, fill=MUTED)
    return lay


# ---------------------------------------------------------------- shapes
@lru_cache(maxsize=256)
def rrect(w, h, r, fill, outline=None, width=0):
    lay = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle([0, 0, int(w) - 1, int(h) - 1], radius=r, fill=fill,
                                          outline=outline, width=width)
    return lay


def box(base, x, y, w, h, r=36, fill=CARD, outline=STROKE, width=3, alpha=1.0):
    paste(base, rrect(int(w), int(h), r, fill, outline, width), x, y, alpha)


@lru_cache(maxsize=128)
def circle_icon(d, fill, label="", fsize=34, fcolor=WHITE):
    lay = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay)
    dr.ellipse([0, 0, d - 1, d - 1], fill=fill)
    if label:
        f = font("ib", fsize)
        tw = f.getlength(label)
        bb = f.getbbox(label)
        dr.text(((d - tw) / 2, (d - (bb[3] + bb[1])) / 2), label, font=f, fill=fcolor)
    return lay


@lru_cache(maxsize=32)
def check_icon(d, fill=GREEN):
    lay = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay)
    dr.ellipse([0, 0, d - 1, d - 1], fill=fill)
    s = d / 100
    dr.line([(28 * s, 52 * s), (44 * s, 68 * s), (73 * s, 35 * s)], fill=WHITE,
            width=max(3, int(9 * s)), joint="curve")
    return lay


def star(draw, cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    draw.polygon(pts, fill=fill)


def pin_layer(size, color):
    lay = Image.new("RGBA", (size, int(size * 1.35)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.ellipse([0, 0, size - 1, size - 1], fill=color)
    d.polygon([(size * 0.18, size * 0.72), (size * 0.82, size * 0.72), (size / 2, size * 1.33)],
              fill=color)
    d.ellipse([size * 0.32, size * 0.32, size * 0.68, size * 0.68], fill=WHITE)
    return lay


def arrow_down(base, x, y1, y2, p, color=CYAN, width=6):
    if p <= 0:
        return
    d = ImageDraw.Draw(base)
    ye = y1 + (y2 - y1) * p
    d.line([(x, y1), (x, ye - 10)], fill=color, width=width)
    if p > 0.6:
        d.polygon([(x - 14, ye - 18), (x + 14, ye - 18), (x, ye)], fill=color)


def chip(base, label, x, y, alpha=1.0, fill=CARD2, outline=STROKE, color=WHITE, size=34):
    w = int(text_w(label, "isb", size)) + 56
    h = int(size * 2.0)
    box(base, x, y, w, h, r=h // 2, fill=fill, outline=outline, width=2, alpha=alpha)
    text(base, label, "isb", size, x, y + (h - size * 1.2) / 2 - 2, w, color=color, alpha=alpha)
    return w, h


def chip_size(label, size=34):
    return int(text_w(label, "isb", size)) + 56, int(size * 2.0)


def chips_centered(base, labels, y, t, start, step=0.3, size=34, gap=20, max_w=920,
                   fill=CARD2, outline=STROKE, color=WHITE):
    rows, cur, cur_w = [], [], 0
    for lab in labels:
        w, _ = chip_size(lab, size)
        if cur and cur_w + gap + w > max_w:
            rows.append((cur, cur_w))
            cur, cur_w = [], 0
        cur_w = cur_w + (gap if cur else 0) + w
        cur.append(lab)
    rows.append((cur, cur_w))
    i = 0
    h = int(size * 2.0)
    for r, (labs, rw) in enumerate(rows):
        x = (W - rw) / 2
        for lab in labs:
            p = prog(t, start + i * step, 0.35)
            chip(base, lab, x, y + r * (h + gap) + (1 - p) * 24, alpha=p, fill=fill,
                 outline=outline, color=color, size=size)
            x += chip_size(lab, size)[0] + gap
            i += 1
    return len(rows) * (h + gap)


def cta_scene(base, t, start, head, pre, keyword, sub):
    """Shared closing scene: headline, DM keyword pill, brand + site."""
    headline(base, head, t, start)
    p1 = prog(t, start + 0.25)
    text(base, pre, "im", 46, 80, 700 + (1 - p1) * 20, 920, color=MUTED, alpha=p1)
    p2 = prog(t, start + 0.5, 0.5)
    pulse = 1 + 0.035 * math.sin((t - start) * 2 * math.pi * 1.2)
    f = font("pb", 150)
    pw = int(f.getlength(keyword)) + 140
    ph = 230
    pill = rrect(pw, ph, ph // 2, CYAN)
    pill = pill.copy()
    d = ImageDraw.Draw(pill)
    bb = f.getbbox(keyword)
    d.text(((pw - f.getlength(keyword)) / 2, (ph - (bb[3] + bb[1])) / 2), keyword, font=f,
           fill=DARK)
    sc = pulse * (0.7 + 0.3 * p2)
    sw, sh = int(pw * sc), int(ph * sc)
    pill = pill.resize((sw, sh), Image.LANCZOS)
    # glow
    glow = rrect(sw + 60, sh + 60, (sh + 60) // 2, CYAN + (40,))
    paste(base, glow, (W - sw - 60) / 2, 900 - (sh + 60) / 2, p2 * 0.6)
    paste(base, pill, (W - sw) / 2, 900 - sh / 2, p2)
    p3 = prog(t, start + 0.9)
    text(base, sub, "im", 40, 80, 1060 + (1 - p3) * 20, 920, color=WHITE, alpha=p3)
    p4 = prog(t, start + 1.3)
    text(base, "ORCA Software", "pb", 58, 80, 1250 + (1 - p4) * 20, 920, alpha=p4)
    text(base, "orcasoftware.com.tr", "isb", 40, 80, 1332 + (1 - p4) * 20, 920, color=CYAN,
         alpha=p4)


# ---------------------------------------------------------------- render
def render(scene_fn, duration, out_path):
    n = int(round(duration * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    bg = background()
    for i in range(n):
        t = i / FPS
        frame = bg.copy()
        scene_fn(frame, t)
        brand_chip(frame)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError("ffmpeg failed")


def still(scene_fn, t, out_path):
    frame = background().copy()
    scene_fn(frame, t)
    brand_chip(frame)
    frame.save(out_path)
