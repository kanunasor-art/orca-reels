# ORCA Reels üretim kodu

- `engine.py` — 1080x1920 kare çizimi ve ffmpeg render altyapısı
- `reels.py` — Reels 1-3 sahneleri (yardımcı `search_bar` buradan)
- `reels2.py` — Reels 4-8; sahne geçişleri seslendirmedeki duraklamalara oturtulur (`vo<N>.mp3` gerekir)
- `stories.py` — günlük 2 hikâye görseli (13:00 soru, 18:00 günün videosu)

Akış: senaryo → ElevenLabs (ses: Fatih, RDNgFQdRVzvDdSV3I6nb, eleven_v4) → render + sesi birleştir →
`videos/` ve `stories/` klasörlerine push → raw.githubusercontent linkiyle Metricool'a zamanla
(blogId 7707044, Reels 10:00, hikâye 13:00 ve 18:00, 3 hashtag, isAiGenerated=false).
