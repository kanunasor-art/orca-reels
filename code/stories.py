"""Launch-week Instagram Stories (2 per day). Usage: python3 stories.py"""
import subprocess
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

from engine import (CARD, CARD2, CYAN, DARK, GREEN, MUTED, STROKE, W, WHITE, background,
                    brand_chip, box, font, paste, rrect, text, text_w)

EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"


@lru_cache(maxsize=64)
def emoji(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((size, int(size * im.size[1] / im.size[0])), Image.LANCZOS)


def tag(img, label, y=330, color=CYAN):
    w = int(text_w(label, "ib", 30)) + 70
    box(img, (W - w) / 2, y, w, 64, r=32, fill=color, outline=None, width=0)
    text(img, label, "ib", 30, (W - w) / 2, y + 14, w, color=DARK)


def pill(img, label, y, fill=CARD2, color=WHITE, outline=STROKE, size=36):
    w = int(text_w(label, "isb", size)) + 90
    box(img, (W - w) / 2, y, w, 96, r=48, fill=fill, outline=outline, width=2)
    text(img, label, "isb", size, (W - w) / 2, y + 26, w, color=color)


def reply_hint(img, label):
    """Arrow pointing down to Instagram's reply bar."""
    text(img, label, "isb", 34, 80, 1540, 920, color=MUTED)
    d = ImageDraw.Draw(img)
    d.line([(540, 1600), (540, 1650)], fill=MUTED, width=5)
    d.polygon([(524, 1645), (556, 1645), (540, 1668)], fill=MUTED)


def reaction_story(day, question, options, hint="Hikâyeye tepki at"):
    img = background().copy()
    brand_chip(img)
    tag(img, "GÜNÜN SORUSU")
    h = text(img, question, "pb", 80, 80, 450, 920, spacing=1.14)
    y = max(450 + h + 70, 820)
    for em, lab in options:
        box(img, 110, y, 860, 150, r=40, fill=CARD, outline=STROKE, width=2)
        paste(img, emoji(em, 86), 160, y + 32)
        text(img, lab, "isb", 44, 290, y + 46, 640, align="left")
        y += 180
    reply_hint(img, hint)
    img.save(f"stories/story_{day}_a.png")


def dm_story(day, question, sub, hint="Cevabını mesaj olarak yaz"):
    img = background().copy()
    brand_chip(img)
    tag(img, "GÜNÜN SORUSU")
    h = text(img, question, "pb", 84, 80, 470, 920, spacing=1.14)
    y = 470 + h + 60
    box(img, 110, y, 860, 6, r=3, fill=CYAN, outline=None, width=0)
    sh = text(img, sub, "im", 44, 110, y + 60, 860, color=MUTED, spacing=1.3)
    paste(img, emoji("💬", 130), 475, max(1200, y + 60 + sh + 40))
    reply_hint(img, hint)
    img.save(f"stories/story_{day}_a.png")


def cover_frame(video):
    out = f"stories/_cover_{video}.png"
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.05", "-i",
                           f"out/{video}_sesli.mp4", "-frames:v", "1", out])
    return Image.open(out).convert("RGBA")


def reminder_story(day, video, title, keyword, extra=None):
    img = background().copy()
    brand_chip(img)
    tag(img, "BUGÜNÜN VİDEOSU", color=GREEN)
    text(img, title, "pb", 64, 80, 420, 920, spacing=1.14)
    cov = cover_frame(video).resize((420, 747), Image.LANCZOS)
    mask = Image.new("L", cov.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, 419, 746], radius=36, fill=255)
    cov.putalpha(mask)
    cx, cy = (W - 420) // 2, 600
    paste(img, rrect(436, 763, 44, CYAN), cx - 8, cy - 8)
    paste(img, cov, cx, cy)
    d = ImageDraw.Draw(img)
    d.ellipse([W / 2 - 60, cy + 313, W / 2 + 60, cy + 433], fill=(255, 255, 255, 230))
    d.polygon([(W / 2 - 18, cy + 343), (W / 2 - 18, cy + 403), (W / 2 + 34, cy + 373)],
              fill=DARK)
    pill(img, "Profilde izle", 1385, size=34)
    msg = f"DM'e {keyword} yaz" if not extra else extra
    w = int(text_w(msg, "pb", 48)) + 100
    box(img, (W - w) / 2, 1505, w, 110, r=55, fill=CYAN, outline=None, width=0)
    text(img, msg, "pb", 48, (W - w) / 2, 1528, w, color=DARK)
    img.save(f"stories/story_{day}_b.png")


DAYS = [
    ("02", lambda: reaction_story(
        "02", "Müşterin seni Google Maps'te **bulabiliyor mu?**",
        [("😍", "Evet, ilk sıralardayım"), ("🔥", "Çıkıyorum ama aşağıda"),
         ("😮", "Hiç bakmadım")]),
     lambda: reminder_story("02", "orca_reels_02_yerel_harita",
                            "Google Maps'te\n**üst sıraya çık**", "HARİTA")),
    ("03", lambda: reaction_story(
        "03", "Gece gelen mesaja **kaç saatte** dönüyorsun?",
        [("💯", "Hemen dönerim"), ("😢", "Sabah görürüm"), ("😮", "Çoğu cevapsız kalıyor")]),
     lambda: reminder_story("03", "orca_reels_03_ai_asistan",
                            "Müşteriye gece 3'te\n**AI asistan** cevap versin", "AI")),
    ("04", lambda: dm_story(
        "04", "API anahtarında hangi izin **asla açık olmamalı?**",
        "A) İşlem izni\nB) Para çekme izni\nCevabını yaz, doğruysa söyleyelim."),
     lambda: reminder_story("04", "orca_reels_04_trader_4soru",
                            "Trade botu yaptırmadan\nönce **bu 4 soruyu sor**", "BOT",
                            extra="Bot yaptıracak birine gönder")),
    ("05", lambda: dm_story(
        "05", "Siten telefonda **kaç puan** alıyor?",
        "PageSpeed Insights'ta test et,\nmobil puanını bize yaz.\nNe anlama geldiğini söyleyelim."),
     lambda: reminder_story("05", "orca_reels_05_yerel_site_hizi",
                            "Siten telefonda\n**yavaş mı açılıyor?**", "HARİTA")),
    ("06", lambda: dm_story(
        "06", "Her gün elle yaptığın **en sıkıcı iş** ne?",
        "Yaz, otomatiğe bağlanıp\nbağlanamayacağını söyleyelim."),
     lambda: reminder_story("06", "orca_reels_06_ai_excel",
                            "Excel'i elle\n**doldurmayı bırak**", "AI")),
    ("07", lambda: reaction_story(
        "07", "Hiç yarım kalan bir **yazılım projen** oldu mu?",
        [("😢", "Evet, hâlâ bitmedi"), ("👏", "Oldu ama kurtardık"), ("😍", "Hiç olmadı")]),
     lambda: reminder_story("07", "orca_reels_07_trader_3hafta",
                            "8 ayda bitmeyen proje\n**3 haftada teslim**", "BOT")),
    ("08", lambda: reaction_story(
        "08", "Bu hafta en çok **hangi konu** işine yaradı?",
        [("😍", "Google Maps ve site"), ("🔥", "Trade botları"), ("💯", "AI ve otomasyon")]),
     lambda: reminder_story("08", "orca_reels_08_genel_4adim",
                            "Yazılım yaptırmak\n**aslında 4 adım**", "TEKLİF")),
]

if __name__ == "__main__":
    import os
    os.makedirs("stories", exist_ok=True)
    for day, a, b in DAYS:
        a()
        b()
        print("done", day)


def info_story(name, tag_label, title, lines, cta, tag_color=CYAN, quote=False):
    img = background().copy()
    brand_chip(img)
    tag(img, tag_label, color=tag_color)
    h = text(img, title, "pb", 80, 80, 450, 920, spacing=1.14)
    y = 450 + h + 70
    if quote:
        box(img, 100, y, 880, 560, r=40, fill=CARD, outline=STROKE, width=2)
        text(img, "“", "pb", 160, 140, y - 10, 200, color=CYAN, align="left")
        qh = text(img, lines[0], "im", 42, 150, y + 130, 780, align="left", spacing=1.3)
        text(img, lines[1], "isb", 36, 150, y + 150 + qh, 780, color=CYAN, align="left")
    else:
        for ln in lines:
            box(img, 110, y, 860, 130, r=36, fill=CARD, outline=STROKE, width=2)
            paste(img, emoji("✅", 64), 150, y + 33)
            text(img, ln, "isb", 42, 250, y + 40, 690, align="left")
            y += 158
    w = int(text_w(cta, "pb", 46)) + 100
    box(img, (W - w) / 2, 1460, w, 110, r=55, fill=CYAN, outline=None, width=0)
    text(img, cta, "pb", 46, (W - w) / 2, 1484, w, color=DARK)
    img.save(f"stories/{name}.png")


def extra_days():
    reminder_story("29", "orca_reels_01_trader_sinyal",
                   "Sinyal gece geldi,\n**bot işlemi açtı**", "BOT")
    import os
    os.replace("stories/story_29_b.png", "stories/story_1029_b.png")
    reaction_story("1030", "Hangi iş için **yazılım** lazım?",
                   [("😍", "Trade botu"), ("🔥", "Web sitesi ve Google"),
                    ("💯", "AI asistan")])
    info_story("story_1030_b", "BİZ KİMİZ", "**ORCA Software**",
               ["2020'den beri", "20+ tamamlanan proje", "Türkiye geneli, uzaktan"],
               "DM'e TEKLİF yaz")
    dm_story("1031", "Sinyalini hâlâ **elle mi** açıyorsun?",
             "Evet ya da hayır yaz.\nEvet ise otomatiğe nasıl\nbağlanır anlatalım.")
    info_story("story_1031_b", "MÜŞTERİMİZ NE DİYOR", "Gerçek proje:\n**RobotX**",
               ["TradingView indikatör sinyallerimi Telegram kanalıma ve üyelerimin "
                "Binance hesaplarına otomatik ileten üyelik panelini tam istediğim gibi "
                "kurdular.", "Aydın Hoca"], "DM'e BOT yaz", tag_color=GREEN, quote=True)
    reaction_story("1101", "Yazılım yaptırırken en çok **neden çekinirsin?**",
                   [("😢", "Fiyat"), ("😮", "Ne kadar süreceği"), ("🔥", "Güvenilir firma")])
    info_story("story_1101_b", "PAZARTESİ BAŞLIYORUZ", "**7 gün, 7 video**",
               ["Google Maps ve web sitesi", "Trade botları", "AI asistan ve otomasyon"],
               "Takip et, kaçırma")
