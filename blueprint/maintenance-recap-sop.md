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

## Cara cek log dengan metadata pengirim

Untuk cek cepat pesan maintenance dari log gateway:

```bash
openclaw logs --limit 20000 --max-bytes 10000000 --plain --no-color \
  | python3 tools/extract-maintenance-log.py --group 6285259199495-1496927635@g.us
```

Aturan validasi pengirim:
- Jika output `sender` berisi nomor/participant/senderId, gunakan itu sebagai bukti pengirim.
- Jika output `sender` adalah `UNKNOWN_PARTICIPANT_NOT_IN_LOG`, jangan menebak pengirim dari log.
- Bila Tuan Besar menyebut pengirim secara eksplisit, boleh tulis `berdasarkan instruksi Tuan Besar`, dan tetap catat bahwa participant tidak tersedia di log.
- Jangan ubah config/restart gateway hanya untuk rekap kecuali Tuan Besar meminta eksplisit.
