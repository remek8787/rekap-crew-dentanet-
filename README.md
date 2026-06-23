# Rekap Crew Dentanet

Repo ini dipakai Alvii untuk menyimpan arsip dan rekap jadwal maintenance/perbaikan crew Dentanet dari WhatsApp group yang diizinkan oleh Tuan Besar.

## Sumber
- WhatsApp group: `6285259199495-1496927635@g.us`
- Mode kerja: pasif — Alvii tidak membalas group.

## Konsep kerja
1. Pesan group masuk dan diarsipkan dulu sebagai bahan mentah.
2. Arsip mentah disimpan oleh collector non-AI ke `raw/whatsapp/YYYY-MM-DD.jsonl`.
3. Saat Tuan Besar memberi perintah, Alvii memfilter sesuai kebutuhan:
   - pengirim/partisipan tertentu,
   - tanggal maintenance,
   - jam upload,
   - nomor list,
   - item tambahan,
   - list final.
4. Hasil rekap final disimpan ke `rekap/YYYY-MM-DD.md`.

## Hemat token
Collector berjalan sebagai systemd user timer non-AI:
- service: `rekap-crew-collector.service`
- timer: `rekap-crew-collector.timer`
- interval: setiap 10 menit

Collector hanya membaca log OpenClaw dan menulis JSONL. Tidak memanggil model AI, jadi tidak memakai token. Token baru dipakai saat Tuan Besar meminta Alvii menganalisis/filter rekap.

## Struktur
- `blueprint/` — SOP dan aturan kerja.
- `tools/` — alat bantu non-AI untuk ekstraksi/collector.
- `raw/whatsapp/YYYY-MM-DD.jsonl` — arsip pesan mentah group.
- `rekap/YYYY-MM-DD.md` — hasil rekap harian.
- `raw/screenshots/` — referensi screenshot bila diperlukan.

## Aturan utama
- Jangan membalas pesan di group sumber.
- Jangan menggandakan item yang hanya diulang oleh pengirim lain.
- Jika ditanya “upload atas nama siapa saja”, tampilkan item dari pesan pengirim tersebut.
- Jika ditanya “tambahan siapa saja”, bandingkan dengan update sebelumnya dan tampilkan item baru saja.
- Jika ditanya “list final”, ambil versi paling baru pada tanggal itu.
- Jika ditanya “riwayat update”, tampilkan urutan waktu + pengirim + perubahan list.
