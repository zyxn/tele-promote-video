# Anime API Integration

Bot sekarang menggunakan **anime-api** library untuk mendapatkan gambar NSFW clickbait secara otomatis dari Nekos API, menggantikan sistem upload manual ke folder lokal.

## Instalasi

```bash
pip install anime-api
```

Atau install semua dependencies:

```bash
pip install -r requirements.txt
```

## Perubahan

### 1. **services/media.py**
- `get_random_clickbait_image()` sekarang mengembalikan URL gambar NSFW dari API
- Menggunakan `NsfwLevel.NSFW` untuk mendapatkan gambar NSFW only
- Fetch 1 gambar per request (sesuai kebutuhan)
- Menggunakan NekosAPI untuk fetch gambar random

### 2. **services/scheduler.py**
- Variable `image_path` diganti menjadi `image_url`
- Telethon bisa langsung mengirim file dari URL

### 3. **handlers/admin.py**
- Handler `/add_photo` sekarang hanya memberikan informasi bahwa bot menggunakan API
- Tidak perlu upload gambar manual lagi

### 4. **config.py**
- Dihapus: `ASSETS_DIR`, `CLICKBAIT_DIR` (tidak diperlukan lagi)
- Ditambahkan: `ANIME_API_CATEGORIES` untuk konfigurasi kategori gambar

## Konfigurasi

Edit `config.py` untuk mengubah kategori gambar:

```python
# Categories yang tersedia: waifu, neko, kemonomimi, husbando, etc.
# Bot akan fetch 1 gambar NSFW random per posting
ANIME_API_CATEGORIES = ["waifu"]
```

Atau gunakan multiple categories:

```python
ANIME_API_CATEGORIES = ["waifu", "neko", "kemonomimi"]
```

## NSFW Level

Bot dikonfigurasi untuk mendapatkan gambar NSFW only menggunakan:

```python
nsfw_level=NsfwLevel.NSFW  # NSFW only
```

Level yang tersedia:
- `NsfwLevel.SFW` (0) - Safe for work
- `NsfwLevel.QUESTIONABLE` (1) - Questionable content
- `NsfwLevel.NSFW` (2) - NSFW content

## Cara Kerja

1. Scheduler memanggil `get_random_clickbait_image()` setiap interval posting
2. Fungsi tersebut fetch **1 gambar NSFW random** dari Nekos API
3. URL gambar dikirim langsung ke Telegram channel menggunakan Telethon
4. Tidak ada file yang disimpan di server lokal

## Keuntungan

✅ Tidak perlu upload gambar manual  
✅ Gambar NSFW selalu fresh dan bervariasi  
✅ Hemat storage server  
✅ Otomatis dan maintenance-free  
✅ Bisa ganti kategori dengan mudah  
✅ Fetch 1 gambar per request (efisien)

## Troubleshooting

Jika gambar tidak muncul, cek:
1. Koneksi internet
2. Log error di console
3. Pastikan anime-api terinstall dengan benar

```bash
python -c "from anime_api.apis import NekosAPI; print('OK')"
```
