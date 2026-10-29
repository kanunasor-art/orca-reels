"""Week-1 ORCA Reels. Usage: python3 reels.py <1|2|3|all> [--stills]"""
import sys

from PIL import Image, ImageDraw

from engine import (BLUE, CARD, CARD2, CYAN, DARK, GREEN, MUTED, RED, STROKE, TG, W, WHITE,
                    YELLOW, arrow_down, box, check_icon, chips_centered, circle_icon, cta_scene,
                    font, headline, lerp, paste, pin_layer, prog, render, rrect, star, still,
                    text, text_layer, text_w)


# ============================================================ Reel 1: trader
def r1(img, t):
    if t < 3:
        headline(img, "Sinyal 03:12'de geldi.\n**Sen uyuyordun.**", t, 0, first=True)
        # phone
        box(img, 230, 640, 620, 860, r=70, fill=(9, 13, 26), outline=(70, 84, 124), width=6)
        box(img, 470, 665, 140, 34, r=17, fill=(0, 0, 0), outline=None, width=0)
        text(img, "03:12", "pb", 150, 230, 735, 620)
        text(img, "Herkes uyuyor, piyasa açık", "ir", 30, 230, 920, 620, color=MUTED)
        # notification
        p = prog(t, 0.25, 0.4)
        ny = 1010 + (1 - p) * -50
        box(img, 262, ny, 556, 190, r=34, fill=(32, 44, 76), outline=(60, 78, 120), width=2,
            alpha=p)
        paste(img, circle_icon(84, BLUE, "TV", 30), 290, ny + 26, p)
        text(img, "TradingView", "isb", 32, 394, ny + 26, 300, align="left", alpha=p)
        text(img, "şimdi", "ir", 28, 600, ny + 28, 190, color=MUTED, align="right", alpha=p)
        text(img, "BTCUSDT Long sinyali", "ir", 30, 394, ny + 76, 410, align="left",
             alpha=p)
        text(img, "Okunmadı", "isb", 26, 394, ny + 126, 300, color=RED, align="left", alpha=p)
        # zzz
        for i, z in enumerate(["z", "z", "z"]):
            pz = prog(t, 0.6 + i * 0.35, 0.5)
            text(img, z, "pb", 44 + i * 14, 700 + i * 40, 1320 - i * 50 - pz * 20, 100,
                 color=MUTED, alpha=pz * 0.8)
    elif t < 8:
        s = 3
        headline(img, "Sabah baktığında fiyat\n**çoktan gitmişti.**", t, s)
        box(img, 80, 620, 920, 720, r=40)
        text(img, "BTCUSDT", "isb", 36, 130, 660, 400, align="left")
        text(img, "1 saat", "ir", 30, 600, 664, 350, color=MUTED, align="right")
        ys = [0.18, 0.16, 0.21, 0.19, 0.24, 0.33, 0.30, 0.40, 0.49, 0.46, 0.57, 0.66, 0.63,
              0.75, 0.84, 0.81, 0.92]
        x0, x1, ytop, ybot = 140, 930, 760, 1270
        pts = [(lerp(x0, x1, i / (len(ys) - 1)), lerp(ybot, ytop, v)) for i, v in enumerate(ys)]
        p = prog(t, s + 0.3, 2.4)
        d = ImageDraw.Draw(img)
        for gy in range(4):
            yy = ytop + gy * (ybot - ytop) / 3
            d.line([(x0, yy), (x1, yy)], fill=(40, 55, 92), width=2)
        upto = p * (len(pts) - 1)
        k = int(upto)
        seg = pts[:k + 1]
        if k < len(pts) - 1:
            fr = upto - k
            seg = seg + [(lerp(pts[k][0], pts[k + 1][0], fr), lerp(pts[k][1], pts[k + 1][1], fr))]
        if len(seg) > 1:
            d.line(seg, fill=GREEN, width=8, joint="curve")
        sx, sy = pts[0]
        d.ellipse([sx - 16, sy - 16, sx + 16, sy + 16], fill=CYAN)
        text(img, "03:12 sinyal", "isb", 30, sx - 30, sy - 70, 260, color=CYAN, align="left")
        if p >= 1:
            ex, ey = pts[-1]
            pe = prog(t, s + 2.75, 0.3)
            d.ellipse([ex - 16, ey - 16, ex + 16, ey + 16], fill=RED)
            text(img, "08:30 sen", "isb", 30, ex - 260, ey - 72, 250, color=RED, align="right",
                 alpha=pe)
        pf = prog(t, s + 3.0, 0.35)
        box(img, 380, 1150, 320, 80, r=40, fill=(70, 20, 28), outline=RED, width=3, alpha=pf)
        text(img, "Fırsat kaçtı", "isb", 34, 380, 1166, 320, color=WHITE, alpha=pf)
        pq = prog(t, s + 3.3, 0.4)
        text(img, "Tanıdık geldi mi?", "pb", 60, 80, 1390 + (1 - pq) * 20, 920, alpha=pq)
    elif t < 16:
        s = 8
        headline(img, "Çözüm: sinyali\n**otomatiğe bağla.**", t, s)
        nodes = [
            ("TradingView", "Alarm tetiklenir", BLUE, "TV", WHITE),
            ("ORCA Bot", "Sinyali webhook ile alır", CYAN, "ORCA", DARK),
            ("Binance", "Emri otomatik açar", YELLOW, "B", DARK),
            ("Telegram", "Sana anında haber verir", TG, "TG", WHITE),
        ]
        y0, nh, gap = 600, 150, 72
        for i, (title, sub, col, lab, lc) in enumerate(nodes):
            st = s + 0.4 + i * 1.7
            p = prog(t, st, 0.45)
            y = y0 + i * (nh + gap)
            if i > 0:
                arrow_down(img, 540, y - gap + 6, y - 6, prog(t, st - 0.45, 0.4))
                pa = (t - st) % 1.0
                if p >= 1:
                    d = ImageDraw.Draw(img)
                    yy = lerp(y - gap + 6, y - 14, pa)
                    d.ellipse([532, yy - 8, 548, yy + 8], fill=WHITE)
            box(img, 140 + (1 - p) * 40, y, 800, nh, r=36, fill=CARD, outline=col, width=3,
                alpha=p)
            paste(img, circle_icon(100, col, lab, 26 if len(lab) > 2 else 34, lc),
                  168 + (1 - p) * 40, y + 25, p)
            text(img, title, "isb", 42, 300 + (1 - p) * 40, y + 28, 600, align="left", alpha=p)
            text(img, sub, "ir", 32, 300 + (1 - p) * 40, y + 84, 620, color=MUTED,
                 align="left", alpha=p)
    elif t < 22:
        s = 16
        headline(img, "**Saniyeden kısa** sürede.\n7/24, sen uyurken bile.", t, s)
        p = prog(t, s + 0.3, 0.5)
        text(img, "< 1 sn", "pb", 210, 80, 640 + (1 - p) * 30, 920, color=CYAN, alpha=p)
        text(img, "sinyalden emre", "im", 40, 80, 890, 920, color=MUTED, alpha=p)
        pl = prog(t, s + 1.0, 0.4)
        text(img, "Desteklenen platformlar", "isb", 32, 80, 1020, 920, color=MUTED, alpha=pl)
        chips_centered(img, ["Binance", "Bybit", "OKX", "MetaTrader 5", "Borsa İstanbul"], 1090,
                       t, s + 1.3, step=0.35, size=38)
    else:
        cta_scene(img, t, 22, "Kendi stratejini\n**otomatiğe bağla.**", "DM'den yaz:", "BOT",
                  "Ücretsiz analiz yapalım")


# ============================================================ Reel 2: local business
def search_bar(img, x, y, w, query, t, start, type_dur=0.8):
    box(img, x, y, w, 110, r=55, fill=(241, 245, 249), outline=None, width=0)
    d = ImageDraw.Draw(img)
    d.ellipse([x + 40, y + 34, x + 76, y + 70], outline=(100, 116, 139), width=5)
    d.line([(x + 72, y + 66), (x + 88, y + 82)], fill=(100, 116, 139), width=6)
    n = int(len(query) * prog(t, start, type_dur)) if type_dur else len(query)
    shown = query[:n]
    text(img, shown, "im", 40, x + 112, y + 30, w - 150, color=(15, 23, 42), align="left")
    if int(t * 2.5) % 2 == 0 and n < len(query) + 1:
        cx = x + 112 + text_w(shown, "im", 40) + 4
        d.line([(cx, y + 30), (cx, y + 80)], fill=(15, 23, 42), width=3)


def result_row(img, x, y, w, name, rating, reviews, alpha=1.0, highlight=None, badge=None):
    outline = highlight or STROKE
    box(img, x, y, w, 150, r=30, fill=CARD, outline=outline, width=3 if highlight else 2,
        alpha=alpha)
    text(img, name, "isb", 38, x + 36, y + 26, w - 300, align="left", alpha=alpha)
    if alpha > 0.05:
        lay = Image.new("RGBA", (w, 50), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.text((0, 4), rating, font=font("isb", 30), fill=YELLOW)
        sx = font("isb", 30).getlength(rating) + 26
        for i in range(5):
            star(d, sx + i * 34, 24, 13, YELLOW)
        d.text((sx + 5 * 34 + 6, 4), f"({reviews} yorum)", font=font("ir", 28), fill=MUTED)
        paste(img, lay, x + 36, y + 84, alpha)
    if badge:
        bw = text_w(badge, "isb", 28) + 44
        box(img, x + w - bw - 30, y + 45, bw, 60, r=30, fill=highlight, outline=None, width=0,
            alpha=alpha)
        text(img, badge, "isb", 28, x + w - bw - 30, y + 58, bw, color=DARK, alpha=alpha)


def r2(img, t):
    if t < 3.5:
        headline(img, "Müşterin seni arıyor.\n**Rakibini buluyor.**", t, 0, first=True)
        search_bar(img, 80, 640, 920, "yakınımdaki nakliyeci", t, 0.0, 0)
        rows = [("Rakip Nakliyat", "4,8", 212), ("Hızlı Taşıma", "4,6", 98)]
        for i, (n, r, c) in enumerate(rows):
            p = prog(t, 0.9 + i * 0.35, 0.4)
            result_row(img, 80, 800 + i * 175 + (1 - p) * 30, 920, n, r, c, alpha=p)
        p = prog(t, 1.75, 0.4)
        y = 1150 + (1 - p) * 30
        box(img, 80, y, 920, 150, r=30, fill=(14, 20, 38), outline=(80, 40, 50), width=3,
            alpha=p)
        text(img, "Senin işletmen?", "isb", 38, 116, y + 30, 600, color=MUTED, align="left",
             alpha=p)
        text(img, "Listede yok", "isb", 32, 116, y + 84, 600, color=RED, align="left", alpha=p)
    elif t < 8:
        s = 3.5
        headline(img, "Siteye girmeden\n**haritadan arıyorlar.**", t, s)
        mx, my, mw, mh = 80, 620, 920, 700
        mp = prog(t, s + 0.2, 0.4)
        lay = Image.new("RGBA", (mw, mh), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rounded_rectangle([0, 0, mw - 1, mh - 1], radius=40, fill=(16, 28, 52),
                            outline=STROKE, width=3)
        d.rectangle([90, 80, 300, 260], fill=(20, 60, 48))
        d.rectangle([600, 430, 830, 640], fill=(20, 60, 48))
        d.polygon([(mw - 3, 0), (mw - 3, 220), (700, 0)], fill=(18, 44, 82))
        for yy in (330, 560):
            d.line([(0, yy), (mw, yy)], fill=(44, 60, 98), width=26)
        for xx in (180, 480, 760):
            d.line([(xx, 0), (xx, mh)], fill=(44, 60, 98), width=22)
        d.line([(0, 680), (mw, 120)], fill=(52, 70, 112), width=30)
        paste(img, lay, mx, my, mp)
        pins = [(260, 300, RED), (640, 240, RED), (420, 520, RED), (800, 400, RED)]
        for i, (px, py, c) in enumerate(pins):
            pp = prog(t, s + 0.7 + i * 0.3, 0.35)
            pl = pin_layer(56, c)
            paste(img, pl, mx + px - 28, my + py - 76 - (1 - pp) * 80, pp)
        pb = prog(t, s + 2.1, 0.45)
        pl = pin_layer(110, CYAN)
        paste(img, pl, mx + 520 - 55, my + 330 - 150 - (1 - pb) * 120, pb)
        pt = prog(t, s + 2.6, 0.4)
        text(img, "Harita = **vitrinin**", "pb", 70, 80, 1390 + (1 - pt) * 20, 920, alpha=pt)
    elif t < 19:
        s = 8
        headline(img, "**3 adımda** üst sıraya çık", t, s)
        steps = [
            ("Profilini eksiksiz doldur", "Çalışma saati, telefon, fotoğraf"),
            ("Doğru kategori ve hizmetler", "Müşterinin aradığı kelimelerle"),
            ("Yorum iste, hepsine cevap ver", "Her müşteriden, her seferinde"),
        ]
        for i, (a, b) in enumerate(steps):
            st = s + 0.5 + i * 3.4
            p = prog(t, st, 0.45)
            y = 560 + i * 260
            box(img, 80, y + (1 - p) * 30, 920, 220, r=36, fill=CARD, outline=STROKE, width=2,
                alpha=p)
            paste(img, circle_icon(96, CARD2, str(i + 1), 44, CYAN), 116, y + 62 + (1 - p) * 30, p)
            text(img, a, "isb", 42, 240, y + 52 + (1 - p) * 30, 720, align="left", alpha=p)
            text(img, b, "ir", 32, 240, y + 120 + (1 - p) * 30, 720, color=MUTED, align="left",
                 alpha=p)
            pc = prog(t, st + 2.2, 0.3)
            if pc > 0:
                ck = check_icon(80).resize((int(80 * (0.6 + 0.4 * pc)),) * 2, Image.LANCZOS)
                paste(img, ck, 890 - ck.size[0] / 2, y + 110 - ck.size[1] / 2, pc)
    elif t < 24:
        s = 19
        headline(img, "Gemlik'te bir firmayı\n**1. sıraya taşıdık.**", t, s)
        search_bar(img, 80, 640, 920, "gemlik nakliyeci", t, s, 0)
        p = prog(t, s + 0.3, 0.45)
        result_row(img, 80, 800 + (1 - p) * 30, 920, "Gemlik Taşımacı", "5,0", 64, alpha=p,
                   highlight=GREEN, badge="1. sıra")
        for i, n in enumerate(["Diğer firma", "Diğer firma"]):
            pi = prog(t, s + 0.7 + i * 0.25, 0.4)
            box(img, 80, 975 + i * 130, 920, 110, r=28, fill=(14, 20, 38), outline=STROKE,
                width=2, alpha=pi * 0.7)
            text(img, n, "im", 34, 116, 1007 + i * 130, 600, color=MUTED, align="left",
                 alpha=pi * 0.7)
        pt = prog(t, s + 1.4, 0.4)
        chips_centered(img, ["Google Maps profili", "Yerel SEO", "Hızlı web sitesi"], 1290, t,
                       s + 1.4, step=0.3, size=32)
        _ = pt
    else:
        cta_scene(img, t, 24, "Senin işletmen\n**nerede çıkıyor?**", "DM'den yaz:", "HARİTA",
                  "Ücretsiz bakalım")


# ============================================================ Reel 3: AI assistant
def bubble_layer(msg, maxw):
    side, body, tm = msg["side"], msg.get("text", ""), msg.get("time", "")
    kind = msg.get("kind", "text")
    if kind == "typing":
        lay = rrect(150, 84, 42, (36, 48, 82))
        return lay.copy(), "typing"
    f = font("ir", 34)
    tl = text_layer(body, "ir", 34, maxw - 56, WHITE, CYAN, "left", 1.25)
    tw = 0
    for line in body.split("\n"):
        tw = max(tw, f.getlength(line))
    bw = int(min(maxw, max(tw + 56, 200)))
    if kind == "file":
        bw = max(bw, 420)
    bh = tl.size[1] + 70 + (70 if kind == "file" else 0)
    fill = (14, 116, 144) if side == "r" else (36, 48, 82)
    if kind == "ok":
        fill = (20, 83, 45)
    lay = rrect(bw, bh, 30, fill).copy()
    d = ImageDraw.Draw(lay)
    lay.paste(tl, (28, 18), tl)
    if kind == "file":
        y = 18 + tl.size[1] - 4
        d.rounded_rectangle([24, y, bw - 24, y + 62], radius=14, fill=(255, 255, 255, 30))
        d.text((44, y + 13), "Fiyat listesi.pdf", font=font("isb", 30), fill=WHITE)
    if tm:
        fs = font("ir", 24)
        d.text((bw - 24 - fs.getlength(tm), bh - 40), tm, font=fs, fill=(203, 213, 225))
    return lay, kind


def chat(img, t, x, y, w, h, title, sub, sub_color, msgs, alpha=1.0):
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=40, fill=(12, 19, 38), outline=STROKE,
                        width=3)
    d.rounded_rectangle([0, 0, w - 1, 120], radius=40, fill=CARD2)
    d.rectangle([0, 80, w - 1, 120], fill=CARD2)
    d.line([(0, 120), (w, 120)], fill=STROKE, width=2)
    av = circle_icon(76, sub_color if sub_color != MUTED else (71, 85, 105),
                     title[0], 34, WHITE)
    lay.paste(av, (30, 22), av)
    d.text((126, 22), title, font=font("isb", 36), fill=WHITE)
    d.text((126, 68), sub, font=font("ir", 28), fill=sub_color)
    visible = []
    for i, m in enumerate(msgs):
        if t < m["t"]:
            continue
        if m.get("kind") == "typing":
            nxt = msgs[i + 1]["t"] if i + 1 < len(msgs) else 1e9
            if t >= nxt:
                continue
        visible.append(m)
    maxw = int(w * 0.74)
    items, total = [], 0
    for m in visible:
        bl, kind = bubble_layer(m, maxw)
        items.append((m, bl, kind))
        total += bl.size[1] + 22
    area_top, area_h = 150, h - 170
    offset = max(0, total - area_h)
    cy = area_top - offset
    for m, bl, kind in items:
        p = prog(t, m["t"], 0.3)
        bx = 28 if m["side"] == "l" else w - 28 - bl.size[0]
        by = cy + (1 - p) * 30
        if by + bl.size[1] > area_top - 10:
            b = bl
            if p < 0.99:
                b = bl.copy()
                b.putalpha(b.getchannel("A").point(lambda v, p=p: int(v * p)))
            if by < area_top:
                cut = int(area_top - by)
                if cut < b.size[1]:
                    b = b.crop((0, cut, b.size[0], b.size[1]))
                    by = area_top
                else:
                    cy += bl.size[1] + 22
                    continue
            lay.paste(b, (int(bx), int(by)), b)
            if kind == "typing":
                for k in range(3):
                    ph = ((t * 3 - k * 0.3) % 1.0)
                    a = int(120 + 135 * (1 - abs(ph - 0.5) * 2))
                    d.ellipse([bx + 32 + k * 34, by + 32, bx + 52 + k * 34, by + 52],
                              fill=(203, 213, 225, a))
        cy += bl.size[1] + 22
    paste(img, lay, x, y, alpha)


def r3(img, t):
    if t < 7:
        if t < 3:
            headline(img, "Gece 3'te gelen mesaja\n**kim cevap veriyor?**", t, 0, first=True)
        else:
            headline(img, "Sabah döndüğünde\n**müşteri gitmişti.**", t, 3)
        msgs = [
            {"t": 0.0, "side": "l", "text": "Merhaba, fiyat alabilir miyim?", "time": "03:07"},
            {"t": 3.3, "side": "r", "text": "Günaydın, yeni gördüm!", "time": "09:42"},
            {"t": 4.6, "side": "l", "text": "Başka yerden aldım, teşekkürler.", "time": "09:44"},
        ]
        chat(img, t, 80, 610, 920, 820, "Müşteri", "son görülme 03:07", MUTED, msgs)
        if t < 3:
            p = prog(t, 0.6, 0.4)
            box(img, 300, 1300, 480, 80, r=40, fill=(70, 20, 28), outline=RED, width=3, alpha=p)
            text(img, "6 saattir cevap yok", "isb", 32, 300, 1318, 480, alpha=p)
        else:
            p = prog(t, 5.2, 0.35)
            box(img, 330, 1300, 420, 80, r=40, fill=(70, 20, 28), outline=RED, width=3, alpha=p)
            text(img, "Müşteri kaybedildi", "isb", 32, 330, 1318, 420, alpha=p)
    elif t < 17:
        s = 7
        headline(img, "AI asistan\n**saniyeler içinde** yazar.", t, s)
        msgs = [
            {"t": s + 0.3, "side": "l", "text": "Merhaba, fiyat alabilir miyim?", "time": "03:07"},
            {"t": s + 1.0, "side": "r", "kind": "typing"},
            {"t": s + 1.7, "side": "r", "text": "Merhaba! Fiyat listemizi hemen\npaylaşıyorum.",
             "time": "03:07", "kind": "file"},
            {"t": s + 3.6, "side": "l", "text": "Yarın için randevu var mı?", "time": "03:08"},
            {"t": s + 4.2, "side": "r", "kind": "typing"},
            {"t": s + 4.8, "side": "r", "text": "Yarın 14:00 ve 16:30 boş.\nHangisini ayırayım?",
             "time": "03:08"},
            {"t": s + 6.6, "side": "l", "text": "14:00 olsun", "time": "03:09"},
            {"t": s + 7.2, "side": "r", "kind": "typing"},
            {"t": s + 7.8, "side": "r", "text": "Randevunuz oluşturuldu.\nYarın 14:00, görüşmek üzere!",
             "time": "03:09", "kind": "ok"},
        ]
        p = prog(t, s, 0.35)
        chat(img, t, 80, 590, 920, 900, "ORCA AI Asistan", "çevrimiçi · 7/24", GREEN, msgs,
             alpha=p)
    elif t < 22:
        s = 17
        headline(img, "Gerçek proje:\n**eğitim kurumu botu**", t, s)
        p = prog(t, s + 0.3, 0.45)
        box(img, 80, 620 + (1 - p) * 30, 920, 760, r=40, alpha=p)
        paste(img, circle_icon(110, TG, "TG", 38), 130, 670 + (1 - p) * 30, p)
        text(img, "Tusmer Eğitim Botu", "isb", 44, 270, 680 + (1 - p) * 30, 700, align="left",
             alpha=p)
        text(img, "Telegram · Öğrenci paneli", "ir", 32, 270, 740 + (1 - p) * 30, 700,
             color=MUTED, align="left", alpha=p)
        feats = ["7/24 öğrenci desteği", "Doküman indirme", "Deneme sınavları",
                 "Tamamen dijital süreç"]
        for i, f in enumerate(feats):
            pf = prog(t, s + 0.9 + i * 0.6, 0.35)
            y = 880 + i * 120
            paste(img, check_icon(70), 140, y + (1 - pf) * 20, pf)
            text(img, f, "im", 40, 240, y + 10 + (1 - pf) * 20, 700, align="left", alpha=pf)
    else:
        cta_scene(img, t, 22, "İşletmen için\n**neler yapabilir?**", "DM'den yaz:", "AI",
                  "Senaryonu birlikte çıkaralım")


REELS = {
    "1": (r1, 28.0, "orca_reels_01_trader_sinyal.mp4"),
    "2": (r2, 29.0, "orca_reels_02_yerel_harita.mp4"),
    "3": (r3, 27.0, "orca_reels_03_ai_asistan.mp4"),
}

STILL_TIMES = {
    "1": [0.0, 2.5, 6.8, 15.5, 20.5, 25.5],
    "2": [0.0, 3.0, 7.5, 18.5, 23.0, 27.0],
    "3": [0.0, 6.5, 12.0, 16.5, 21.5, 25.5],
}

if __name__ == "__main__":
    which = sys.argv[1]
    ids = list(REELS) if which == "all" else [which]
    for rid in ids:
        fn, dur, name = REELS[rid]
        if "--stills" in sys.argv:
            for tt in STILL_TIMES[rid]:
                still(fn, tt, f"stills/r{rid}_{tt:05.1f}.png")
        else:
            render(fn, dur, f"out/{name}")
            print("done", name)
