# Update Sistem Clickbait

## Perubahan

Bot sekarang menggunakan gambar clickbait lokal dari folder `assets/clickbait/` dan tidak lagi menggunakan API Neko.

### Fitur Baru

1. **Dua Tipe Clickbait:**
   - **Default**: Menggunakan `assets/clickbait/default.PNG`
   - **VIP**: Menggunakan `assets/clickbait/vip.PNG`

2. **Command Baru:**
   - `/add_video` - Menambahkan video dengan clickbait default
   - `/add_video_vip` - Menambahkan video dengan clickbait VIP (👑)

### Cara Penggunaan

#### Menambahkan Video Regular
```
1. Upload video/gambar ke grup admin
2. Reply video tersebut dengan: /add_video Judul Video
3. Bot akan menggunakan clickbait default.PNG
```

#### Menambahkan Video VIP
```
1. Upload video/gambar ke grup admin
2. Reply video tersebut dengan: /add_video_vip Judul Video VIP
3. Bot akan menggunakan clickbait vip.PNG
```

### File yang Diubah

1. **services/media.py**
   - Menghapus fungsi `get_random_clickbait_image()` yang menggunakan API
   - Menambahkan fungsi `get_clickbait_image(is_vip=False)` untuk mengambil gambar lokal

2. **handlers/admin.py**
   - Menambahkan support untuk command `/add_video_vip`
   - Menambahkan parameter `is_vip` saat menyimpan video
   - Menampilkan badge VIP (👑) atau Regular (📦) di konfirmasi

3. **database/models.py**
   - Menambahkan kolom `is_vip` (Boolean) di tabel `videos`

4. **database/crud.py**
   - Menambahkan parameter `is_vip` di fungsi `add_video()`

5. **services/scheduler.py**
   - Menggunakan `get_clickbait_image(is_vip=video.is_vip)` untuk memilih gambar yang sesuai
   - Menghapus cleanup temporary file (karena sekarang menggunakan file lokal)

### Migrasi Database

Jalankan script migrasi untuk menambahkan kolom `is_vip`:

```bash
python migrate_add_is_vip.py
```

### Keuntungan

✅ Tidak bergantung pada API eksternal (Neko)
✅ Lebih cepat (tidak perlu download gambar)
✅ Lebih stabil (tidak ada network error)
✅ Bisa customize gambar clickbait sendiri
✅ Support dua tipe konten (Regular & VIP)

### Catatan

- Pastikan file `assets/clickbait/default.PNG` dan `assets/clickbait/vip.PNG` ada
- Gambar clickbait bisa diganti kapan saja dengan mengganti file tersebut
- Semua video lama akan menggunakan clickbait default (is_vip=False)
