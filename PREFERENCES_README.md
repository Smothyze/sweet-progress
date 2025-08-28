# Fitur Preferences - Sweet Progress

## Overview
Fitur Preferences telah ditambahkan ke Sweet Progress untuk memberikan kontrol lebih baik atas pengaturan aplikasi, terutama untuk direktori backup.

## Fitur Baru

### 1. Menu Preferences
- **Lokasi**: Option > Preferences
- **Akses**: Klik menu "Option" di menu bar, kemudian pilih "Preferences"

### 2. Opsi Save Output Directory
- **Deskripsi**: Checkbox "Save output directory" yang memungkinkan semua game disimpan dalam direktori backup yang sama
- **Fungsi**: 
  - Ketika diaktifkan: Semua game akan menggunakan direktori backup default yang sama
  - Ketika dinonaktifkan: Setiap game dapat memiliki direktori backup yang berbeda

### 3. Default Backup Directory
- **Fungsi**: Field untuk mengatur direktori backup default
- **Fitur**: Tombol "Browse..." untuk memilih direktori
- **Status**: Field akan aktif/nonaktif berdasarkan status checkbox "Save output directory"

### 4. Pengaturan Path Display
- **Opsi**: Auto, Game Path, Standard
- **Fungsi**: Mengatur cara menampilkan path dalam file backup

### 5. Pengaturan Timestamp
- **Opsi**: Enable, Disable
- **Fungsi**: Mengatur apakah backup menggunakan timestamp atau tidak

## Cara Penggunaan

### Mengaktifkan Save Output Directory
1. Buka **Option > Preferences**
2. Centang checkbox **"Save output directory"**
3. Masukkan direktori backup default di field **"Default Backup Directory"**
4. Klik **"Save"**

### Menggunakan Direktori Backup Default
1. Setelah mengaktifkan preferensi, field "Backup Location" akan otomatis terisi dengan direktori default
2. Semua game yang di-backup akan menggunakan direktori yang sama
3. Struktur folder akan menjadi: `[Default Backup Directory]/[Game Title]/[Savegame Folder]`

### Menonaktifkan Save Output Directory
1. Buka **Option > Preferences**
2. Hapus centang checkbox **"Save output directory"**
3. Klik **"Save"**
4. Setiap game dapat memiliki direktori backup yang berbeda

## Struktur Folder Backup

### Ketika Save Output Directory Aktif
```
[Default Backup Directory]/
├── Game Title 1/
│   ├── Savegame Folder 1/
│   └── Readme.txt
├── Game Title 2/
│   ├── Savegame Folder 2/
│   └── Readme.txt
└── Game Title 3/
    ├── Savegame Folder 3/
    └── Readme.txt
```

### Ketika Save Output Directory Nonaktif
```
[Backup Location 1]/
├── Game Title 1/
│   ├── Savegame Folder 1/
│   └── Readme.txt

[Backup Location 2]/
├── Game Title 2/
│   ├── Savegame Folder 2/
│   └── Readme.txt
```

## Keuntungan

1. **Organisasi Lebih Baik**: Semua backup game dalam satu lokasi
2. **Kemudahan Backup**: Tidak perlu memilih direktori untuk setiap game
3. **Konsistensi**: Struktur folder yang seragam untuk semua game
4. **Fleksibilitas**: Tetap bisa menggunakan direktori terpisah jika diinginkan

## Catatan Teknis

- Preferensi disimpan dalam file konfigurasi aplikasi
- Perubahan preferensi langsung diterapkan tanpa restart aplikasi
- Direktori backup default divalidasi keberadaannya sebelum digunakan
- Fallback ke direktori backup individual jika direktori default tidak tersedia

## Troubleshooting

### Direktori Default Tidak Muncul
- Pastikan direktori yang dipilih benar-benar ada
- Pastikan aplikasi memiliki akses write ke direktori tersebut
- Cek log aplikasi untuk pesan error

### Preferensi Tidak Tersimpan
- Pastikan aplikasi memiliki akses write ke file konfigurasi
- Restart aplikasi jika diperlukan
- Cek permission folder aplikasi

## Versi
Fitur ini tersedia mulai versi Sweet Progress yang mendukung Preferences.

