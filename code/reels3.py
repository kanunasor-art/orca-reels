"""Gap-filler Reels 9-11 (30 Oct - 1 Nov). Usage: python3 reels3.py <9..11|all> [--stills]"""
import subprocess
import sys

from PIL import ImageDraw

from engine import (BLUE, CARD, CARD2, CYAN, DARK, GREEN, MUTED, RED, STROKE, TG, W, WHITE,
                    YELLOW, box, check_icon, chips_centered, circle_icon, cta_scene, headline,
                    paste, prog, render, still, text, text_w)
from reels import chat
import reels2
from reels2 import scene_at

reels2.LINES.update({
    9: ["Müşterilerin her gün aynı soruları mı soruyor?",
        "Fiyat ne, kargo kaç günde gelir, hangi saatlerde açıksınız.",
        "Bir Telegram botu bu soruları senin yerine saniyeler içinde cevaplar, siparişi alır ve sana haber verir.",
        "Basit bir bot genelde bir iki haftada hazır olur.",
        "İşine uygun botu konuşmak için DM'den AI yaz."],
    10: ["Bir uygulama fikrin var ama nereden başlayacağını bilmiyor musun?",
         "Önce şu üç soruyu cevapla.",
         "Bir: Bu uygulamayı kim kullanacak?",
         "İki: Olmazsa olmaz tek özellik ne?",
         "Üç: Uygulama nasıl para kazanacak?",
         "Bu üç cevap hazırsa gerisini birlikte planlayalım. Ücretsiz teklif için DM'den TEKLİF yaz."],
    11: ["Kim aradı, kime teklif gitti, kim dönüş bekliyor, hepsi aklında mı?",
         "Not defterinde ve WhatsApp'ta dağılan müşteriler bir yerde unutuluyor.",
         "Basit bir müşteri takip sistemi her müşteriyi tek ekranda toplar ve takip zamanı gelince sana hatırlatır.",
         "Hazır programlar işine tam uymuyorsa, sana özel yazıyoruz.",
         "Müşteri takibini toparlamak için DM'den TEKLİF yaz."],
})


# ============================================================ Reel 9: Telegram bot
def r9(img, t, cues):
    i, s = scene_at(t, cues)
    if i == 0:
        headline(img, "Hep **aynı sorular** mı?", t, 0, first=True)
        qs = ["Fiyat ne?", "Fiyat ne?", "Kargo kaç gün?", "Fiyat ne?", "Açık mısınız?"]
        for k, q in enumerate(qs):
            p = 1.0 if k < 2 else prog(t, 0.3 + k * 0.4, 0.3)
            x = 100 + (k % 2) * 260
            y = 560 + k * 165
            w = text_w(q, "im", 40) + 70
            box(img, x, y, w, 120, r=32, fill=(36, 48, 82), outline=None, width=0, alpha=p)
            text(img, q, "im", 40, x, y + 34, w, alpha=p)
        pc = prog(t, 2.2, 0.4)
        box(img, 620, 1420, 380, 84, r=42, fill=(70, 20, 28), outline=RED, width=3, alpha=pc)
        text(img, "Günde 50 kez", "isb", 34, 620, 1440, 380, alpha=pc)
    elif i == 1:
        headline(img, "En sık 3 soru", t, s)
        for k, (em, q) in enumerate([("₺", "Fiyat ne?"), ("📦", "Kargo kaç günde?"),
                                     ("🕘", "Saat kaçta açıksınız?")]):
            p = prog(t, s + 0.2 + k * 0.6, 0.4)
            y = 620 + k * 220
            box(img, 80, y + (1 - p) * 30, 920, 180, r=40, fill=CARD, outline=STROKE, width=2,
                alpha=p)
            paste(img, circle_icon(110, CARD2, str(k + 1), 48, CYAN), 120, y + 35 + (1 - p) * 30,
                  p)
            text(img, q, "isb", 48, 270, y + 56 + (1 - p) * 30, 700, align="left", alpha=p)
    elif i == 2:
        headline(img, "Telegram botu\n**saniyede** cevaplar", t, s)
        msgs = [
            {"t": s + 0.3, "side": "l", "text": "Merhaba, fiyat ne?", "time": "22:14"},
            {"t": s + 0.8, "side": "r", "kind": "typing"},
            {"t": s + 1.3, "side": "r", "text": "Merhaba! Güncel fiyat listemiz\nekte.",
             "time": "22:14", "kind": "file"},
            {"t": s + 2.8, "side": "l", "text": "2 adet sipariş vermek istiyorum", "time": "22:15"},
            {"t": s + 3.3, "side": "r", "kind": "typing"},
            {"t": s + 3.8, "side": "r", "text": "Siparişiniz alındı.\nKargo 2 iş gününde.",
             "time": "22:15", "kind": "ok"},
        ]
        chat(img, t, 80, 600, 920, 860, "ORCA Bot", "bot · 7/24", TG, msgs, alpha=prog(t, s, 0.3))
    elif i == 3:
        headline(img, "Basit bir bot\n**1-2 haftada** hazır", t, s)
        p = prog(t, s + 0.2, 0.5)
        text(img, "1-2", "pb", 230, 80, 640 + (1 - p) * 30, 920, color=CYAN, alpha=p)
        text(img, "hafta", "pb", 80, 80, 920 + (1 - p) * 30, 920, alpha=p)
        chips_centered(img, ["Soru-cevap", "Sipariş alma", "Sana bildirim"], 1120, t, s + 0.8,
                       step=0.3, size=36)
    else:
        cta_scene(img, t, s, "İşine uygun\n**botu konuşalım**", "DM'den yaz:", "AI",
                  "Ücretsiz analiz")


# ============================================================ Reel 10: app idea
Q10 = [("Kim kullanacak?", "Hedef kullanıcıyı tek cümleyle yaz"),
       ("Olmazsa olmaz tek özellik ne?", "İlk sürüm sadece onu yapsın"),
       ("Nasıl para kazanacak?", "Abonelik, satış, reklam...")]


def r10(img, t, cues):
    i, s = scene_at(t, cues)
    if i == 0:
        headline(img, "Uygulama fikrin var,\n**nereden başlamalı?**", t, 0, first=True)
        box(img, 330, 620, 420, 760, r=60, fill=(9, 13, 26), outline=(70, 84, 124), width=6)
        box(img, 480, 642, 120, 30, r=15, fill=(0, 0, 0), outline=None, width=0)
        for k in range(6):
            x = 385 + (k % 3) * 110
            y = 760 + (k // 3) * 130
            box(img, x, y, 90, 90, r=22, fill=CARD2, outline=None, width=0)
        p = prog(t, 0.6, 0.4)
        text(img, "?", "pb", 200, 330, 1040 + (1 - p) * 20, 420, color=CYAN, alpha=max(p, 0.0))
    elif i == 1:
        headline(img, "Önce **3 soru**", t, s)
        p = prog(t, s + 0.1, 0.4)
        text(img, "3", "pb", 420, 80, 560 + (1 - p) * 40, 920, color=CYAN, alpha=p)
    elif i <= 4:
        q, note = Q10[i - 2]
        headline(img, f"**Soru {i - 1}**", t, s)
        p = prog(t, s, 0.4)
        box(img, 80, 560 + (1 - p) * 40, 920, 480, r=40, fill=CARD, outline=CYAN, width=3,
            alpha=p)
        paste(img, circle_icon(130, CYAN, str(i - 1), 64, DARK), 475, 600 + (1 - p) * 40, p)
        qh = text(img, q, "pb", 62, 130, 760 + (1 - p) * 40, 820, alpha=p)
        pn = prog(t, s + 0.6, 0.4)
        text(img, note, "im", 38, 130, 775 + qh + (1 - p) * 40, 820, color=MUTED, alpha=pn)
        x = 80
        for k in range(i - 2):
            lab = ["Kullanıcı", "Tek özellik"][k]
            w = text_w(lab, "isb", 30) + 100
            box(img, x, 1100, w, 70, r=35, fill=CARD2, outline=STROKE, width=2)
            paste(img, check_icon(44), x + 14, 1113)
            text(img, lab, "isb", 30, x + 66, 1116, w - 70, align="left")
            x += w + 16
    else:
        cta_scene(img, t, s, "Cevaplar hazırsa\n**birlikte planlayalım**", "Ücretsiz teklif:",
                  "TEKLİF", "DM'den yaz")


# ============================================================ Reel 11: CRM
NOTES = [("Ahmet Bey'i ara", -4, 120, 600, YELLOW), ("Teklif gönder?", 5, 560, 640, (250, 160, 90)),
         ("Ayşe H. dönüş bekliyor", 3, 140, 960, (134, 239, 172)),
         ("Fiyat sordu, kimdi?", -6, 560, 1020, YELLOW)]


def r11(img, t, cues):
    i, s = scene_at(t, cues)
    if i == 0:
        headline(img, "Kim aradı, kime teklif gitti,\n**hepsi aklında mı?**", t, 0, first=True,
                 size=66)
        from PIL import Image
        for k, (lab, rot, x, y, col) in enumerate(NOTES):
            p = 1.0 if k < 2 else prog(t, 0.4 + k * 0.4, 0.3)
            if p <= 0:
                continue
            lay = Image.new("RGBA", (400, 300), (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            d.rectangle([10, 10, 390, 290], fill=col)
            from engine import text_layer
            tl = text_layer(lab, "isb", 40, 340, DARK, DARK, "left", 1.2)
            lay.paste(tl, (30, 40), tl)
            lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
            paste(img, lay, x, y, p)
    elif i == 1:
        headline(img, "Dağınık müşteri =\n**unutulan müşteri**", t, s)
        srcs = [("Not defteri", YELLOW), ("WhatsApp", GREEN), ("Excel", BLUE), ("Hafıza", MUTED)]
        for k, (lab, col) in enumerate(srcs):
            p = prog(t, s + 0.2 + k * 0.4, 0.35)
            x = 80 + (k % 2) * 470
            y = 620 + (k // 2) * 260
            box(img, x, y + (1 - p) * 30, 450, 220, r=36, fill=CARD, outline=col, width=3,
                alpha=p)
            text(img, lab, "isb", 44, x, y + 82 + (1 - p) * 30, 450, alpha=p)
        pr = prog(t, s + 2.2, 0.4)
        box(img, 300, 1200, 480, 90, r=45, fill=(70, 20, 28), outline=RED, width=3, alpha=pr)
        text(img, "Müşteri unutuldu", "isb", 36, 300, 1222, 480, alpha=pr)
    elif i == 2:
        headline(img, "Tek ekran,\n**zamanında hatırlatma**", t, s)
        p = prog(t, s + 0.1, 0.4)
        box(img, 80, 580, 920, 700, r=40, fill=CARD, outline=STROKE, width=2, alpha=p)
        text(img, "Müşteriler", "pb", 44, 130, 615, 500, align="left", alpha=p)
        rows = [("Ahmet Yılmaz", "Teklif gönderildi", BLUE), ("Ayşe Han", "Dönüş bekliyor", YELLOW),
                ("Mert Kaya", "Satış tamam", GREEN), ("Selin Ak", "İlk görüşme", CYAN)]
        for k, (n, st, col) in enumerate(rows):
            pk = prog(t, s + 0.5 + k * 0.3, 0.3)
            y = 710 + k * 130
            box(img, 120, y, 840, 110, r=24, fill=CARD2, outline=None, width=0, alpha=pk)
            text(img, n, "isb", 36, 160, y + 33, 400, align="left", alpha=pk)
            w = text_w(st, "isb", 28) + 40
            box(img, 940 - w, y + 28, w, 54, r=27, fill=col, outline=None, width=0, alpha=pk)
            text(img, st, "isb", 28, 940 - w, y + 38, w, color=DARK, alpha=pk)
        pb = prog(t, s + 2.4, 0.4)
        box(img, 140, 1320 - (1 - pb) * 40, 800, 120, r=30, fill=(32, 44, 76), outline=CYAN,
            width=3, alpha=pb)
        text(img, "🔔 Hatırlatma: Ayşe Han'ı ara, 14:00", "isb", 34, 140, 1360 - (1 - pb) * 40,
             800, alpha=pb)
    elif i == 3:
        headline(img, "Hazır olan uymazsa\n**sana özel yazılım**", t, s)
        for k, lab in enumerate(["Senin iş akışına göre", "Gereksiz menü yok",
                                 "Ekibin kolay kullanır"]):
            p = prog(t, s + 0.3 + k * 0.5, 0.35)
            y = 640 + k * 190
            box(img, 80, y + (1 - p) * 30, 920, 160, r=36, fill=CARD, outline=GREEN, width=3,
                alpha=p)
            paste(img, check_icon(90), 120, y + 35 + (1 - p) * 30, p)
            text(img, lab, "isb", 44, 250, y + 52 + (1 - p) * 30, 720, align="left", alpha=p)
    else:
        cta_scene(img, t, s, "Müşteri takibini\n**toparlayalım**", "DM'den yaz:", "TEKLİF",
                  "Ücretsiz analiz")


REELS = {9: (r9, "orca_reels_09_ai_telegram_bot"), 10: (r10, "orca_reels_10_genel_uygulama"),
         11: (r11, "orca_reels_11_genel_crm")}

if __name__ == "__main__":
    which = sys.argv[1]
    ids = list(REELS) if which == "all" else [int(which)]
    for n in ids:
        fn, name = REELS[n]
        cues, dur = reels2.cues_for(n)
        scene = lambda img, t, fn=fn, cues=cues: fn(img, t, cues)
        if "--stills" in sys.argv:
            for tt in [0.0] + [c + 1.8 for c in cues[1:]]:
                still(scene, tt, f"stills/m{n}_{tt:05.1f}.png")
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
