"""Week-2 launch Reels 4-8. Scene cues snap to real pauses in the voiceover.
Usage: python3 reels2.py <4..8|all> [--stills]"""
import re
import subprocess
import sys

from PIL import ImageDraw

from engine import (BLUE, CARD, CARD2, CYAN, DARK, GREEN, MUTED, RED, STROKE, TG, WHITE, YELLOW,
                    box, check_icon, chips_centered, circle_icon, cta_scene, font, headline,
                    lerp, paste, prog, render, rrect, still, text, text_w)
from reels import search_bar

LINES = {
    4: ["Trade botu yaptıracaksan önce şu dört soruyu sor.",
        "Bir: API anahtarım nerede saklanacak? Para çekme izni asla açık olmamalı.",
        "İki: Bot gerçek parayla çalışmadan önce test ediliyor mu?",
        "Üç: Kaynak kod bana teslim ediliyor mu?",
        "Dört: Teslimden sonra sorun çıkarsa kim ilgilenecek?",
        "Bu sorulara net cevap alamıyorsan başka yere bak. Bizim cevaplarımızı merak ediyorsan DM'den BOT yaz."],
    5: ["Siten telefonda üç saniyede açılmıyorsa ziyaretçilerin çoğu beklemeden çıkıyor.",
        "Çoğu esnaf sitesi bilgisayarda güzel görünür ama telefonda ağır açılır.",
        "Kontrol etmesi kolay. Google'da PageSpeed Insights yaz, sitenin adresini gir.",
        "Mobil puanın ellinin altındaysa müşteri kaybediyorsun.",
        "Hızlı ve telefona uygun siteyi sıfırdan kodluyoruz. Siteni ücretsiz inceleyelim, DM'den HARİTA yaz."],
    6: ["Her gün aynı Excel tablosunu elle dolduruyorsan bu video senin için.",
        "Siparişler WhatsApp'tan geliyor, sen tek tek tabloya yazıyorsun, sonra faturaya geçiriyorsun.",
        "Bu işi bir bot yapabilir. Mesajı okur, bilgileri tabloya yazar, faturayı hazırlar.",
        "Her gün o işe harcadığın saat sana kalır, yazım hatası da biter.",
        "Hangi işini otomatiğe bağlayabileceğimizi görmek için DM'den AI yaz."],
    7: ["Başka bir firmanın sekiz ayda bitiremediği projeyi biz üç haftada teslim ettik.",
        "Sır yok. Önce kapsamı netleştiriyoruz, ne yapılacak, ne yapılmayacak.",
        "Sonra stratejiyi kurallara döküp her parçayı tek tek test ediyoruz, sen de düzenli olarak çalışan demoyu görüyorsun.",
        "Binance, Bybit ve OKX'te aynı anda işlem açan çoklu borsa sistemimiz de böyle, üç haftada ve ek masrafsız teslim edildi.",
        "Yarım kalmış bir bot projen varsa DM'den BOT yaz, birlikte bakalım."],
    8: ["Yazılım yaptırmak gözünü korkutuyorsa, süreç aslında dört adım.",
        "Analiz: ne istediğini dinliyor, kapsamı netleştiriyoruz.",
        "Tasarım: sistemin yapısını ve ekranlarını çiziyoruz.",
        "Geliştirme: her aşamanın sonunda çalışan bir demo görüyorsun.",
        "Teslim: test edip yayına alıyoruz, sonrasında da destek veriyoruz.",
        "Aklında bir proje varsa ücretsiz teklif için DM'den TEKLİF yaz."],
}


def audio_info(path):
    dur = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))
    log = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af",
                          "silencedetect=noise=-35dB:d=0.22", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    return dur, ends


def cues_for(n):
    """Line start times: proportional estimate snapped to the nearest real pause."""
    dur, ends = audio_info(f"vo{n}.mp3")
    lines = LINES[n]
    w = [len(s) for s in lines]
    total = sum(w)
    cues, acc = [0.0], 0
    for k in w[:-1]:
        acc += k
        est = acc / total * dur
        near = [e for e in ends if abs(e - est) < 1.6 and e > cues[-1] + 1.0]
        cues.append(min(near, key=lambda e: abs(e - est)) - 0.15 if near else est)
    return cues, dur


def scene_at(t, cues):
    i = 0
    while i + 1 < len(cues) and t >= cues[i + 1]:
        i += 1
    return i, cues[i]


# ============================================================ Reel 4: 4 questions
Q4 = [("API anahtarım nerede saklanacak?", "Para çekme izni asla açık olmamalı", "Güvenlik"),
      ("Bot gerçek parayla çalışmadan önce test ediliyor mu?", "Önce test, sonra canlı", "Test"),
      ("Kaynak kod bana teslim ediliyor mu?", "Kod senin olmalı", "Kaynak kod"),
      ("Teslimden sonra sorun çıkarsa kim ilgilenecek?", "Destek süresi yazılı olsun", "Destek")]


def r4(img, t, cues):
    i, s = scene_at(t, cues)
    if i == 0:
        headline(img, "Bot yaptırmadan önce\n**bu 4 soruyu sor.**", t, 0, first=True)
        for k in range(4):
            p = 1.0
            y = 640 + k * 190
            box(img, 140 + k * 22, y, 800 - k * 44, 160, r=34, fill=CARD, outline=STROKE,
                width=2, alpha=max(p, 1.0 if k == 0 else 0))
            paste(img, circle_icon(96, CARD2, str(k + 1), 44, CYAN), 175 + k * 22, y + 32,
                  max(p, 1.0 if k == 0 else 0))
            text(img, "?", "pb", 80, 300 + k * 22, y + 22, 500, color=MUTED, align="left",
                 alpha=max(p, 1.0 if k == 0 else 0))
    elif i <= 4:
        q, note, tag = Q4[i - 1]
        headline(img, f"**Soru {i}**", t, s, size=72)
        p = prog(t, s, 0.4)
        box(img, 80, 520 + (1 - p) * 40, 920, 560, r=40, fill=CARD, outline=CYAN, width=3,
            alpha=p)
        paste(img, circle_icon(130, CYAN, str(i), 64, DARK), 475, 560 + (1 - p) * 40, p)
        text(img, q, "pb", 58, 130, 730 + (1 - p) * 40, 820, alpha=p, spacing=1.15)
        pn = prog(t, s + 0.8, 0.4)
        box(img, 200, 960, 680, 84, r=42, fill=(20, 60, 48), outline=GREEN, width=2, alpha=pn)
        text(img, note, "isb", 34, 200, 980, 680, alpha=pn)
        done = [Q4[k][2] for k in range(i - 1)]
        if done:
            x = 80
            for lab in done:
                w = text_w(lab, "isb", 30) + 100
                box(img, x, 1180, w, 70, r=35, fill=CARD2, outline=STROKE, width=2)
                paste(img, check_icon(44), x + 14, 1193)
                text(img, lab, "isb", 30, x + 66, 1196, w - 70, align="left")
                x += w + 16
    else:
        cta_scene(img, t, s, "Net cevap yoksa\n**başka yere bak.**", "Bizim cevaplarımız için:",
                  "BOT", "DM'den yaz")


# ============================================================ Reel 5: slow mobile site
def phone(img, x, y, w, h, alpha=1.0):
    box(img, x, y, w, h, r=60, fill=(9, 13, 26), outline=(70, 84, 124), width=6, alpha=alpha)
    box(img, x + w / 2 - 60, y + 22, 120, 30, r=15, fill=(0, 0, 0), outline=None, width=0,
        alpha=alpha)


def r5(img, t, cues):
    i, s = scene_at(t, cues)
    if i == 0:
        headline(img, "Siten **3 saniyede**\naçılıyor mu?", t, 0, first=True)
        phone(img, 290, 600, 500, 820)
        d = ImageDraw.Draw(img)
        a0 = (t * 360) % 360
        d.arc([440, 840, 640, 1040], a0, a0 + 270, fill=CYAN, width=14)
        sec = min(t / 1.2 + 1, 5.9)
        col = RED if sec >= 3 else YELLOW
        text(img, f"{sec:.1f} sn", "pb", 90, 290, 1100, 500, color=col)
        text(img, "Yükleniyor...", "ir", 32, 290, 1220, 500, color=MUTED)
        pb = prog(t, 2.2, 0.4)
        box(img, 300, 1460, 480, 84, r=42, fill=(70, 20, 28), outline=RED, width=3, alpha=pb)
        text(img, "Ziyaretçi çıktı", "isb", 34, 300, 1480, 480, alpha=pb)
    elif i == 1:
        headline(img, "Bilgisayarda güzel,\n**telefonda ağır.**", t, s)
        for k, (lab, sub, ok) in enumerate([("Bilgisayar", "1,2 sn", True),
                                             ("Telefon", "6,8 sn", False)]):
            p = prog(t, s + 0.3 + k * 0.6, 0.4)
            x = 80 + k * 470
            box(img, x, 640 + (1 - p) * 30, 450, 560, r=40, fill=CARD,
                outline=GREEN if ok else RED, width=3, alpha=p)
            text(img, lab, "isb", 44, x, 700 + (1 - p) * 30, 450, alpha=p)
            text(img, sub, "pb", 96, x, 820 + (1 - p) * 30, 450, color=GREEN if ok else RED,
                 alpha=p)
            ic = check_icon(110) if ok else circle_icon(110, RED, "X", 50)
            paste(img, ic, x + 170, 1010 + (1 - p) * 30, p)
        pn = prog(t, s + 1.6, 0.4)
        text(img, "Örnek değerler", "ir", 28, 80, 1240, 920, color=MUTED, alpha=pn)
    elif i == 2:
        headline(img, "Kontrol etmesi\n**30 saniye.**", t, s)
        search_bar(img, 80, 640, 920, "PageSpeed Insights", t, s + 0.2, 1.0)
        p = prog(t, s + 1.6, 0.4)
        box(img, 80, 820 + (1 - p) * 30, 920, 300, r=36, fill=CARD, outline=STROKE, width=2,
            alpha=p)
        text(img, "Web sayfası URL'si girin", "im", 34, 130, 860 + (1 - p) * 30, 820,
             color=MUTED, align="left", alpha=p)
        box(img, 130, 930 + (1 - p) * 30, 820, 90, r=20, fill=(241, 245, 249), outline=None,
            width=0, alpha=p)
        n = int(len("www.senin-siten.com") * prog(t, s + 2.2, 1.0))
        text(img, "www.senin-siten.com"[:n], "im", 36, 160, 952 + (1 - p) * 30, 760,
             color=(15, 23, 42), align="left", alpha=p)
        pa = prog(t, s + 3.4, 0.4)
        box(img, 360, 1170, 360, 90, r=45, fill=BLUE, outline=None, width=0, alpha=pa)
        text(img, "Analiz et", "isb", 38, 360, 1190, 360, alpha=pa)
    elif i == 3:
        headline(img, "Mobil puan\n**50'nin altında mı?**", t, s)
        score = int(lerp(0, 38, prog(t, s + 0.2, 1.4)))
        d = ImageDraw.Draw(img)
        cx, cy, r = 540, 960, 230
        d.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=CARD2, width=34)
        d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * score / 100, fill=RED,
              width=34)
        text(img, str(score), "pb", 170, cx - 250, cy - 120, 500, color=RED)
        text(img, "Mobil puan", "im", 36, cx - 250, cy + 90, 500, color=MUTED)
        pl = prog(t, s + 1.6, 0.4)
        chips_centered(img, ["0-49 Zayıf", "50-89 Orta", "90+ İyi"], 1300, t, s + 1.6,
                       step=0.2, size=32)
        _ = pl
    else:
        cta_scene(img, t, s, "Siteni ücretsiz\n**inceleyelim.**", "DM'den yaz:", "HARİTA",
                  "Hızlı, telefona uygun site")


# ============================================================ Reel 6: Excel automation
def grid(img, x, y, cols, rows, filled, t, cw=220, rh=78, alpha=1.0, fast=False):
    heads = ["Müşteri", "Ürün", "Adet", "Tutar"][:cols]
    data = [("Ayşe K.", "Tişört", "3", "450 TL"), ("Mehmet A.", "Kupa", "5", "375 TL"),
            ("Zeynep T.", "Çanta", "1", "620 TL"), ("Ali V.", "Defter", "10", "300 TL"),
            ("Elif S.", "Kalem", "20", "240 TL")]
    box(img, x, y, cw * cols, rh * (rows + 1), r=14, fill=(250, 250, 250), outline=None,
        width=0, alpha=alpha)
    d = ImageDraw.Draw(img)
    for c in range(cols):
        d.rectangle([x + c * cw, y, x + (c + 1) * cw, y + rh], fill=(22, 101, 52))
        text(img, heads[c], "isb", 30, x + c * cw, y + 20, cw, color=WHITE, alpha=alpha)
    for r_ in range(rows + 1):
        d.line([(x, y + r_ * rh), (x + cw * cols, y + r_ * rh)], fill=(200, 200, 200), width=2)
    for c in range(cols + 1):
        d.line([(x + c * cw, y), (x + c * cw, y + rh * (rows + 1))], fill=(200, 200, 200),
               width=2)
    cells = filled
    k = 0
    for r_ in range(rows):
        for c in range(cols):
            if k >= cells:
                return
            text(img, data[r_][c], "im", 30, x + c * cw, y + (r_ + 1) * rh + 20, cw,
                 color=(15, 23, 42), alpha=alpha)
            k += 1


def flow_row(img, y, labels, mid, t, start, colors, alpha=1.0):
    xs = [80, 400, 720]
    for k, (lab, col) in enumerate(zip(labels, colors)):
        p = prog(t, start + k * 0.35, 0.35) * alpha
        box(img, xs[k], y, 280, 170, r=30, fill=CARD, outline=col, width=3, alpha=p)
        text(img, lab, "isb", 34, xs[k], y + 60, 280, alpha=p)
        if k < 2:
            pa = prog(t, start + k * 0.35 + 0.2, 0.3) * alpha
            text(img, mid, "ib", 40, xs[k] + 270, y + 56, 60, color=MUTED, alpha=pa)


def r6(img, t, cues):
    i, s = scene_at(t, cues)
    if i == 0:
        headline(img, "Her gün aynı Excel'i\n**elle mi dolduruyorsun?**", t, 0, first=True,
                 size=70)
        grid(img, 100, 640, 4, 5, int(1 + t * 1.6), t)
        pc = prog(t, 1.0, 0.4)
        box(img, 300, 1200, 480, 84, r=42, fill=(70, 20, 28), outline=RED, width=3, alpha=pc)
        text(img, "Her gün, tek tek", "isb", 34, 300, 1220, 480, alpha=pc)
    elif i == 1:
        headline(img, "Bugün böyle:\n**hepsi elle.**", t, s)
        flow_row(img, 640, ["WhatsApp", "Excel", "Fatura"], "→", t, s + 0.2, [GREEN, GREEN, BLUE])
        p = prog(t, s + 1.4, 0.4)
        for k in range(3):
            paste(img, circle_icon(80, CARD2, "Sen", 24, WHITE), 180 + k * 320, 850, p)
        pr = prog(t, s + 2.2, 0.4)
        box(img, 240, 1020, 600, 90, r=45, fill=(70, 20, 28), outline=RED, width=3, alpha=pr)
        text(img, "Yavaş + hataya açık", "isb", 36, 240, 1042, 600, alpha=pr)
    elif i == 2:
        headline(img, "**Bot** okur, yazar,\nfaturayı hazırlar.", t, s)
        flow_row(img, 600, ["WhatsApp", "ORCA Bot", "Excel + Fatura"], "→", t, s + 0.2,
                 [GREEN, CYAN, BLUE])
        pg = prog(t, s + 1.2, 0.3)
        grid(img, 100, 840, 4, 5, int(lerp(0, 20, prog(t, s + 1.4, 1.6))), t, alpha=pg)
    elif i == 3:
        headline(img, "Senin kazancın", t, s)
        for k, (a, b) in enumerate([("Zaman", "O saat sana kalır"),
                                    ("Doğruluk", "Yazım hatası biter")]):
            p = prog(t, s + 0.3 + k * 0.8, 0.4)
            y = 620 + k * 300
            box(img, 80, y + (1 - p) * 30, 920, 250, r=40, fill=CARD, outline=GREEN, width=3,
                alpha=p)
            paste(img, check_icon(110), 130, y + 70 + (1 - p) * 30, p)
            text(img, a, "pb", 56, 280, y + 50 + (1 - p) * 30, 680, align="left", alpha=p)
            text(img, b, "im", 38, 280, y + 135 + (1 - p) * 30, 680, color=MUTED, align="left",
                 alpha=p)
    else:
        cta_scene(img, t, s, "Hangi işin\n**otomatiğe bağlanır?**", "DM'den yaz:", "AI",
                  "Birlikte bakalım")


# ============================================================ Reel 7: 8 months vs 3 weeks
def r7(img, t, cues):
    i, s = scene_at(t, cues)
    if i == 0:
        headline(img, "8 ayda bitmeyen proje\n**3 haftada teslim.**", t, 0, first=True)
        rows = [("Başka firma", "8 ay", RED, 0.62, False), ("ORCA", "3 hafta", GREEN, 1.0, True)]
        for k, (lab, d_, col, frac, ok) in enumerate(rows):
            y = 680 + k * 300
            text(img, lab, "isb", 40, 80, y, 600, align="left")
            box(img, 80, y + 70, 920, 80, r=40, fill=CARD2, outline=None, width=0)
            sp = 1.0 if k == 0 else 1.0
            p = frac if t < 0.05 else min(1.0, (t + 0.3) / (2.6 if k == 0 else 0.9)) * frac
            w = max(80, 920 * p)
            box(img, 80, y + 70, w, 80, r=40, fill=col, outline=None, width=0)
            text(img, d_, "pb", 40, 80, y + 170, 920, color=col, align="left")
            if ok and p >= 1.0:
                paste(img, check_icon(70), 930, y + 175)
            if not ok and t > 1.6:
                text(img, "Bitmedi", "isb", 34, 80, y + 175, 920, color=RED, align="right")
            _ = sp
    elif i == 1:
        headline(img, "1. Kapsamı **netleştir**", t, s)
        cols = [("Yapılacak", ["Binance bağlantısı", "Piramit alım", "Telegram bildirimi"],
                 GREEN, True),
                ("Yapılmayacak", ["Belirsiz ekstralar", "Sonsuz revizyon"], RED, False)]
        for k, (h, items, col, ok) in enumerate(cols):
            x = 80 + k * 470
            p = prog(t, s + 0.2 + k * 0.5, 0.4)
            box(img, x, 600, 450, 640, r=36, fill=CARD, outline=col, width=3, alpha=p)
            text(img, h, "pb", 44, x, 640, 450, color=col, alpha=p)
            for j, it in enumerate(items):
                pj = prog(t, s + 0.6 + k * 0.5 + j * 0.3, 0.3)
                ic = check_icon(54) if ok else circle_icon(54, RED, "X", 26)
                paste(img, ic, x + 30, 740 + j * 130, pj)
                text(img, it, "im", 34, x + 100, 744 + j * 130, 330, align="left", alpha=pj)
    elif i == 2:
        headline(img, "2. Kurallar, test,\n**düzenli demo**", t, s)
        steps = [("Strateji → kurallar", CYAN), ("Her parça test edilir", BLUE),
                 ("Çalışan demo sende", GREEN)]
        for k, (lab, col) in enumerate(steps):
            st = s + 0.4 + k * 1.4
            p = prog(t, st, 0.4)
            y = 620 + k * 230
            box(img, 140, y + (1 - p) * 30, 800, 170, r=36, fill=CARD, outline=col, width=3,
                alpha=p)
            paste(img, circle_icon(100, col, str(k + 1), 44, DARK), 175, y + 35 + (1 - p) * 30,
                  p)
            text(img, lab, "isb", 42, 310, y + 58 + (1 - p) * 30, 620, align="left", alpha=p)
    elif i == 3:
        headline(img, "Çoklu borsa sistemi:\n**3 hafta, ek masraf yok**", t, s, size=68)
        chips_centered(img, ["Binance", "Bybit", "OKX"], 640, t, s + 0.3, step=0.3, size=48)
        pb = prog(t, s + 1.4, 0.4)
        for k, (a, b) in enumerate([("3 hafta", "teslim"), ("0 TL", "ek masraf")]):
            x = 80 + k * 470
            box(img, x, 860 + (1 - pb) * 30, 450, 300, r=40, fill=CARD, outline=GREEN, width=3,
                alpha=pb)
            text(img, a, "pb", 84, x, 920 + (1 - pb) * 30, 450, color=GREEN, alpha=pb)
            text(img, b, "im", 38, x, 1050 + (1 - pb) * 30, 450, color=MUTED, alpha=pb)
    else:
        cta_scene(img, t, s, "Yarım kalmış\n**bot projen mi var?**", "DM'den yaz:", "BOT",
                  "Birlikte bakalım")


# ============================================================ Reel 8: 4-step process
STEPS8 = [("Analiz", "Ne istediğini dinler, kapsamı netleştiririz"),
          ("Tasarım", "Sistemin yapısı ve ekranları çizilir"),
          ("Geliştirme", "Her aşamanın sonunda çalışan demo"),
          ("Teslim", "Test, yayına alma ve destek")]


def r8(img, t, cues):
    i, s = scene_at(t, cues)
    if i == 0:
        headline(img, "Yazılım yaptırmak\naslında **4 adım.**", t, 0, first=True)
    elif i <= 4:
        headline(img, f"Adım {i}: **{STEPS8[i - 1][0]}**", t, s, size=70)
    if i <= 4:
        d = ImageDraw.Draw(img)
        x0, y0, gap = 150, 620, 200
        d.line([(x0, y0 + 50), (x0, y0 + 50 + gap * 3)], fill=STROKE, width=8)
        for k, (h, sub) in enumerate(STEPS8):
            y = y0 + k * gap
            appear = 1.0 if i > 0 or t > 0.2 + k * 0.3 else prog(t, 0.2 + k * 0.3, 0.3)
            if i == 0:
                appear = 1.0 if t < 0.05 else prog(t, k * 0.3, 0.3)
            active = i == k + 1
            doneK = i > k + 1
            if doneK:
                paste(img, check_icon(100), x0 - 50, y, appear)
            else:
                col = CYAN if active else CARD2
                paste(img, circle_icon(100, col, str(k + 1), 44, DARK if active else MUTED),
                      x0 - 50, y, appear)
            w_ = 760
            box(img, x0 + 80, y - 5, w_, 115 if not active else 150, r=28,
                fill=CARD if active else (14, 20, 38), outline=CYAN if active else STROKE,
                width=3 if active else 2, alpha=appear)
            text(img, h, "pb" if active else "isb", 40, x0 + 115, y + 12, w_ - 60,
                 color=WHITE if (active or doneK or i == 0) else MUTED, align="left",
                 alpha=appear)
            if active:
                pa = prog(t, s + 0.3, 0.35)
                text(img, sub, "im", 30, x0 + 115, y + 75, w_ - 60, color=MUTED, align="left",
                     alpha=pa)
    else:
        cta_scene(img, t, s, "Aklında bir\n**proje mi var?**", "Ücretsiz teklif için:",
                  "TEKLİF", "DM'den yaz")


REELS = {
    4: (r4, "orca_reels_04_trader_4soru"),
    5: (r5, "orca_reels_05_yerel_site_hizi"),
    6: (r6, "orca_reels_06_ai_excel"),
    7: (r7, "orca_reels_07_trader_3hafta"),
    8: (r8, "orca_reels_08_genel_4adim"),
}

if __name__ == "__main__":
    which = sys.argv[1]
    ids = list(REELS) if which == "all" else [int(which)]
    for n in ids:
        fn, name = REELS[n]
        cues, dur = cues_for(n)
        scene = lambda img, t, fn=fn, cues=cues: fn(img, t, cues)
        if "--stills" in sys.argv:
            ts = [0.0] + [c + 1.6 for c in cues[1:]] + [dur - 0.5]
            for tt in ts:
                still(scene, tt, f"stills/n{n}_{tt:05.1f}.png")
            print(n, [round(c, 2) for c in cues], round(dur, 2))
        else:
            vlen = round(dur + 1.0, 2)
            render(scene, vlen, f"out/{name}.mp4")
            subprocess.check_call(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", f"out/{name}.mp4", "-i",
                 f"vo{n}.mp3", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                 "-b:a", "192k", "-af", "apad", "-t", str(vlen), "-movflags", "+faststart",
                 f"out/{name}_sesli.mp4"])
            print("done", name, vlen)
