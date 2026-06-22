# SOP Rekap Maintenance Crew Dentanet

## Sumber
WhatsApp group: `6285259199495-1496927635@g.us`

## Jadwal
Rekap harian: 15:00 WITA (`Asia/Makassar`).

## Format item
- Teknisi/pengirim
- Tanggal maintenance
- Nomor list
- Lokasi/customer/area
- Kendala/pekerjaan
- Status/marker bila terlihat

## Aturan respons
Alvii tidak membalas pesan apapun di group sumber. Jika group memicu agent, gunakan `NO_REPLY` kecuali Tuan Besar secara privat meminta laporan.

## Catatan teknis OpenClaw
Jika `sessions_list`/`sessions_history` belum menampilkan session group, cek log inbound OpenClaw dengan `openclaw logs --limit ... --plain --no-color` dan filter group id `6285259199495-1496927635@g.us`. Pesan group bisa tetap masuk di log walau session API belum visible.
