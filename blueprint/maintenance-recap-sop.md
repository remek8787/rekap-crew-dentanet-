# SOP Rekap Maintenance Crew Dentanet

## Sumber
WhatsApp group: `6285259199495-1496927635@g.us`

## Tujuan
Menyimpan semua pesan jadwal maintenance/perbaikan dari group secara pasif, lalu memfilter dan merekap sesuai perintah Tuan Besar.

## Prinsip utama
- Alvii tidak membalas pesan apapun di group sumber.
- Semua pesan group yang relevan dibiarkan masuk dulu ke sisi Alvii/collector.
- Collector otomatis hanya mengarsipkan raw message; tidak menganalisis dengan AI dan tidak memakai token.
- Analisis/filter baru dilakukan saat Tuan Besar meminta.
- Jangan membuat cron/OpenClaw agent otomatis untuk menganalisis, merekap, atau mengirim laporan sebelum Tuan Besar meminta. Hemat token: tidak ada laporan proaktif.

## Jadwal rekap
- Rekap harian default: sekitar 15:00 WITA (`Asia/Makassar`) bila diminta/diaktifkan.
- Collector raw berjalan lebih sering untuk menghindari kehilangan konteks.

## Collector non-AI
Systemd user timer aktif:

```bash
systemctl --user status rekap-crew-collector.timer
systemctl --user status rekap-crew-collector.service
```

Detail:
- Service: `~/.config/systemd/user/rekap-crew-collector.service`
- Timer: `~/.config/systemd/user/rekap-crew-collector.timer`
- Interval: setiap 10 menit
- Script: `tools/collect-group-messages.py`
- Output: `raw/whatsapp/YYYY-MM-DD.jsonl`
- State dedupe: `state/collector-state.json`

Manual run:

```bash
python3 tools/collect-group-messages.py
```

Dry run:

```bash
python3 tools/collect-group-messages.py --dry-run
```

## Aturan filter sesuai perintah Tuan Besar

### 1. “Upload atas nama siapa saja”
Makna: ambil item/nama/lokasi/customer dari pesan yang dikirim oleh pengirim/partisipan tertentu pada tanggal tertentu.

Contoh:
- “Call Center hari Selasa 23-06-2026 upload perbaikan atas nama siapa saja?”
- Jawab dengan semua item yang ada pada pesan Call Center di tanggal itu.

### 2. “Tambahan siapa saja”
Makna: bandingkan pesan update pengirim tersebut dengan update sebelumnya, lalu tampilkan item baru saja.

Contoh kasus 23/06/2026:
- Pakwin upload awal no. 1–7 jam 03.18.
- Call Center upload update no. 1–8 jam 08.25/08.26.
- Tambahan Call Center = no. 8, Sugeng Adi Taufik DC.
- Mas Bagong upload update no. 1–9 jam 10.52.
- Tambahan Mas Bagong = no. 9, Area Pos Kina Salon DC.

### 3. “List final”
Makna: ambil update paling baru pada tanggal maintenance tersebut, lalu tampilkan daftar final tanpa duplikasi.

### 4. “Riwayat update”
Makna: tampilkan urutan waktu, pengirim/partisipan, rentang nomor list, dan item yang bertambah.

Format contoh:
- 03.18 — Pakwin/Pak Win Dentanet: upload awal no. 1–7.
- 08.25/08.26 — Call Center PT Denta Sejahtera Group: update sampai no. 8; tambahan no. 8.
- 10.52 — Mas Bagong Dentanet: update sampai no. 9; tambahan no. 9.

## Format item rekap
Untuk setiap item valid, catat:
- Teknisi/pengirim/partisipan
- Waktu upload jika tersedia
- Tanggal maintenance
- Nomor list
- Lokasi/customer/area/nama
- Kendala/pekerjaan
- Status/marker bila terlihat, termasuk centang hijau

## Aturan deduplikasi
- Jika pesan berikutnya mengulang no. 1–7 dan menambah no. 8, no. 1–7 jangan dihitung item baru lagi.
- Simpan tetap riwayat pengirimnya, tetapi rekap tambahan hanya mencatat nomor baru.
- Bila ada revisi teks pada nomor lama, catat sebagai revisi/update, bukan duplikasi.

## Metadata pengirim
Sumber prioritas:
1. Screenshot WhatsApp dari Tuan Besar yang memperlihatkan nama bubble/pengirim.
2. Metadata raw jika collector/log menyediakan `sender`, `participant`, atau `senderId`.
3. Instruksi eksplisit Tuan Besar, dengan catatan “berdasarkan instruksi Tuan Besar”.

Jika raw log tidak menyediakan participant, jangan menebak. Tulis `UNKNOWN_PARTICIPANT_NOT_IN_LOG` atau jelaskan bahwa participant tidak tersedia di log.

## Cara cek log dengan metadata pengirim

```bash
openclaw logs --limit 5000 --max-bytes 1000000 --plain --no-color \
  | python3 tools/extract-maintenance-log.py --group 6285259199495-1496927635@g.us
```

Aturan validasi pengirim:
- Jika output `sender` berisi nomor/participant/senderId, gunakan itu sebagai bukti pengirim.
- Jika output `sender` adalah `UNKNOWN_PARTICIPANT_NOT_IN_LOG`, jangan menebak pengirim dari log.
- Bila Tuan Besar menyebut pengirim secara eksplisit, boleh tulis `berdasarkan instruksi Tuan Besar`, dan tetap catat bahwa participant tidak tersedia di log.

## Aturan respons
- Jika group memicu agent dan tidak ada permintaan laporan privat, jawab `NO_REPLY`.
- Laporan hasil hanya dikirim ke Tuan Besar/private chat kecuali Tuan Besar minta lain.
- Jangan ubah config/restart gateway hanya untuk rekap kecuali Tuan Besar meminta eksplisit.
