"""Composite Reels 16 (balloon hook): Blender frames + camera HUD + countdown + captions + VO.
Needs /home/claude/b3d/frames/b0001..b0180.png, wire.png, vo16.mp3"""
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import reels2

W, H, FPS = 1080, 1920, 24
B3 = "/home/claude/b3d"
OSW = "/home/claude/reels/Oswald-Bold.ttf"
INT = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
ORANGE, WHITE, MUT = (255, 106, 28), (240, 240, 240), (150, 150, 150)
NF = 180                      # rendered frames; frame 180 = freeze
T_FREEZE = NF / FPS           # 7.5 s
VO_START = T_FREEZE + 0.4
CUT = 54


def F(size, path=OSW):
    return ImageFont.truetype(path, size)


def load(i):
    return Image.open(f"{B3}/frames/b{i:04d}.png").convert("RGB").resize((W, H), Image.LANCZOS)


FROZEN = None
WIRE = None


def wire_img():
    g = np.asarray(Image.open(f"{B3}/wire.png").convert("L").resize((W, H), Image.LANCZOS)).astype(float) / 255
    g = np.clip((g - 0.35) * 1.8, 0, 1) ** 1.4          # keep lines, kill the washed fill
    col = np.array(ORANGE, float)
    return Image.fromarray((g[..., None] * col).clip(0, 255).astype("uint8"))


def rec_hud(img, t, frame):
    d = ImageDraw.Draw(img)
    a = 230
    for (x, y, dx, dy) in [(40, 120, 1, 1), (W - 40, 120, -1, 1), (40, H - 260, 1, -1), (W - 40, H - 260, -1, -1)]:
        d.line([(x, y), (x + 60 * dx, y)], fill=(a, a, a), width=3)
        d.line([(x, y), (x, y + 60 * dy)], fill=(a, a, a), width=3)
    secs = frame / FPS
    tc = f"REC 00:00:{int(secs):02d}:{int(frame % FPS):02d}"
    if int(t * 2) % 2 == 0:
        d.ellipse([70, 146, 88, 164], fill=(230, 40, 40))
    d.text((98, 140), tc, font=F(28, MONO), fill=WHITE)
    lens = "100MM MACRO" if frame >= CUT else "85MM"
    d.text((W - 70 - F(28, MONO).getlength(lens), 140), lens, font=F(28, MONO), fill=WHITE)


def countdown(img, frame, alpha=1.0):
    left = max(2, NF + 2 - frame)
    d = ImageDraw.Draw(img, "RGBA")
    lab = "KALAN KARE"
    f1, f2 = F(26, INT), F(110, OSW)
    d.text(((W - f1.getlength(lab)) / 2, 1300), lab, font=f1, fill=(240, 240, 240, int(220 * alpha)))
    num = f"{left:03d}"
    col = (*ORANGE, int(255 * alpha)) if left < 50 else (255, 255, 255, int(255 * alpha))
    d.text(((W - f2.getlength(num)) / 2, 1335), num, font=f2, fill=col)


def watch_pill(img, t):
    d = ImageDraw.Draw(img, "RGBA")
    lab = f"izliyorsun  {t:4.1f} sn"
    f = F(28, INT)
    w = f.getlength(lab) + 70
    d.rounded_rectangle([(W - w) / 2, 128, (W + w) / 2, 180], radius=26, fill=(20, 20, 20, 200))
    d.ellipse([(W - w) / 2 + 22, 146, (W - w) / 2 + 38, 162], fill=(230, 40, 40))
    d.text(((W - w) / 2 + 48, 136), lab, font=f, fill=WHITE)


reels2.LINES[16] = ["Bir balonu tam yedi saniyedir izliyorsun.", "Gerçekte var olmayan bir balonu.",
                    "Ve hâlâ buradasın, patlamasını bekliyorsun.", "Bunu biz kodla yaptık.",
                    "Şimdi senin markan için neler yapabileceğimizi düşün. DM'den TEKLİF yaz."]
CUES, VOD = reels2.cues_for(16)
CUES = [VO_START + c for c in CUES] + [VO_START + VOD]
DUR = round(VO_START + VOD + 1.4, 2)
# caption lines (small white + big highlighted line), revealed word by word across each cue
LINES = [("Bir balonu", "7 saniyedir", "izliyorsun."), ("Gerçekte", "var olmayan", "bir balonu."),
         ("Ve hâlâ buradasın,", "patlamasını", "bekliyorsun."), ("Bunu biz", "kodla", "yaptık."),
         ("Senin markan için", "neler yapabiliriz?", "")]


def caption(img, t):
    for i, (small, big, tail) in enumerate(LINES):
        a, b = CUES[i], CUES[i + 1]
        if not (a <= t < b):
            continue
        p = (t - a) / max(0.01, b - a)
        band = np.zeros((H, W), np.uint8)
        yy = np.arange(H)[:, None]
        band[:] = (np.clip((yy - 900) / 450.0, 0, 1) ** 1.5).repeat(W, 1) * 200
        dark = Image.new("RGB", (W, H), (0, 0, 0))
        img.paste(dark, (0, 0), Image.fromarray(band))
        d = ImageDraw.Draw(img)
        fs, fb = F(40, INT), F(96, OSW)
        if p > 0.0:
            d.text(((W - fs.getlength(small)) / 2, 1250), small, font=fs, fill=WHITE)
        words = [(big, (255, 140, 70))] + ([(tail, WHITE)] if tail else [])
        shown = [wd for k, wd in enumerate(words) if p > 0.25 + k * 0.3]
        if shown:
            total = sum(fb.getlength(w) for w, _ in shown) + fb.getlength(" ") * (len(shown) - 1)
            x = (W - total) / 2
            for w, c in shown:
                d.text((x + 3, 1314), w, font=fb, fill=(0, 0, 0))
                d.text((x, 1310), w, font=fb, fill=c)
                x += fb.getlength(w + " ")


def cta(img, t, s):
    p = min(1, (t - s) / 0.4)
    img.paste(Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), 0.7 * p))
    d = ImageDraw.Draw(img)
    for k, (txt, f, col, y) in enumerate([("DM'E", F(80), WHITE, 1080), ("\"TEKLİF\"", F(150), ORANGE, 1170),
                                          ("YAZ", F(80), WHITE, 1350)]):
        if p > k * 0.25:
            d.text(((W - f.getlength(txt)) / 2, y), txt, font=f, fill=col)
    if p >= 1:
        for txt, f, col, y in [("ORCA SOFTWARE", F(54), WHITE, 1520), ("orcasoftware.com.tr", F(32, INT), MUT, 1592)]:
            d.text(((W - f.getlength(txt)) / 2, y), txt, font=f, fill=col)


def frame_at(t):
    global FROZEN, WIRE
    if t < T_FREEZE:
        fr = min(NF, int(t * FPS) + 1)
        img = load(fr)
        rec_hud(img, t, fr)
        countdown(img, fr)
        return img
    if FROZEN is None:
        FROZEN = load(NF)
        WIRE = wire_img()
    dt = t - T_FREEZE
    img = FROZEN.copy()
    if dt < 0.25:                       # freeze punch
        img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), 0.5 * (1 - dt / 0.25))
    if CUES[1] <= t < CUES[2] + 0.3:    # "doesn't exist" -> wireframe reveal (scan line)
        k = min(1.0, (t - CUES[1]) / 0.6)
        yline = int(H * k)
        top = WIRE.crop((0, 0, W, yline))
        img.paste(top, (0, 0))
        if k < 1:
            ImageDraw.Draw(img).line([(0, yline), (W, yline)], fill=ORANGE, width=4)
    elif CUES[2] + 0.3 <= t < CUES[2] + 0.9:   # wire fades back to the real balloon
        k = (t - CUES[2] - 0.3) / 0.6
        img = Image.blend(WIRE, FROZEN, k)
    watch_pill(img, min(t, CUES[1]) if t < CUES[2] else min(t, CUES[1]) + (t - CUES[2]))
    if t < CUES[4] + 0.6:
        caption(img, t)
    if t >= CUES[4] + 0.6:
        cta(img, t, CUES[4] + 0.6)
    return img


def sfx(path):
    sr = 44100
    n = int(DUR * sr)
    a = np.zeros(n)
    x = np.arange(n) / sr
    # low tension drone rising until the freeze
    rise = np.clip(x / T_FREEZE, 0, 1)
    a += 0.06 * np.sin(2 * np.pi * (48 + 30 * rise) * x) * (x < T_FREEZE)
    a += 0.025 * np.random.randn(n) * rise ** 3 * (x < T_FREEZE)
    i = int(T_FREEZE * sr)
    L = int(1.2 * sr)
    y = np.arange(L) / sr
    a[i:i + L] += 0.6 * (np.sin(2 * np.pi * 42 * y) + 0.3 * np.random.randn(L) * np.exp(-y * 30)) * np.exp(-y * 2.5)
    j = int((T_FREEZE + 0.5) * sr)
    a[j:] += 0.04 * np.sin(2 * np.pi * 55 * x[j:]) * np.minimum(1, (x[j:] - x[j]) / 2)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    import sys
    if "--stills" in sys.argv:
        for tt in [0.5, 3.0, 7.0, CUES[0] + 1.2, CUES[1] + 1.0, CUES[2] + 1.2, CUES[4] + 1.5]:
            frame_at(tt).save(f"stills/b16_{tt:05.2f}.png")
        print(CUES, DUR)
        raise SystemExit
    sfx("out/b16_sfx.wav")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", "out/b16_sfx.wav", "-i", "vo16.mp3", "-filter_complex",
           f"[2:a]adelay={int(VO_START*1000)}|{int(VO_START*1000)},apad[vo];[1:a][vo]amix=inputs=2:duration=first:normalize=0[a]",
           "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
           "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "160k", "-shortest",
           "-movflags", "+faststart", "out/orca_reels_16_hook_balon_sesli.mp4"]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(int(DUR * FPS)):
        p.stdin.write(frame_at(k / FPS).tobytes())
    p.stdin.close()
    p.wait()
    print("done", DUR)
