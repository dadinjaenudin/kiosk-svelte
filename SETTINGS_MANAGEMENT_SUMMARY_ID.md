# Manajemen Pengaturan - Ringkasan Implementasi

## Gambaran Umum

Fitur Manajemen Pengaturan yang lengkap untuk Panel Admin POS, menyediakan konfigurasi tenant dan manajemen outlet yang komprehensif.

**URL Akses**: http://localhost:5175/settings

## Fitur Utama

### Tab 1: Pengaturan Tenant

#### 1. Manajemen Logo
- Upload logo bisnis (maksimal 2MB)
- Preview logo sebelum upload
- Hapus logo yang ada
- Format didukung: PNG, JPG, JPEG, GIF

#### 2. Informasi Bisnis
- **Nama Tenant** (wajib)
- **Telepon**: Nomor kontak bisnis
- **Email**: Email bisnis dengan validasi format
- **Website**: URL website bisnis
- **Deskripsi**: Deskripsi multi-baris

#### 3. Warna Branding
- **Warna Utama**: Warna brand utama dengan color picker
- **Warna Sekunder**: Warna brand kedua dengan color picker
- Validasi format hex (#RRGGBB)
- Input manual atau color picker

#### 4. Pengaturan Keuangan
- **Tarif Pajak**: Persentase pajak (contoh: 10.00%)
- **Biaya Layanan**: Persentase service charge (contoh: 5.00%)
- Presisi desimal hingga 2 digit

### Tab 2: Manajemen Outlet

#### 1. Dashboard Statistik
- **Total Outlet**: Jumlah semua outlet
- **Outlet Aktif**: Jumlah outlet aktif
- **Outlet Tidak Aktif**: Jumlah outlet non-aktif
- **Kota**: Jumlah kota unik

#### 2. Sistem Filter
- **Pencarian**: Cari berdasarkan nama, alamat, kota, telepon, email
- **Filter Status**: Semua, Aktif, Tidak Aktif
- **Filter Kota**: Dropdown kota yang tersedia
- **Filter Provinsi**: Dropdown provinsi yang tersedia

#### 3. Tabel Outlet

Kolom yang ditampilkan:
- ☑️ Checkbox untuk operasi massal
- 📍 **Outlet**: Nama dengan icon dan ID
- 🗺️ **Lokasi**: Kota, provinsi, alamat lengkap
- 📞 **Kontak**: Telepon dan email
- ⏰ **Jam Operasional**: Waktu buka dan tutup
- ✅ **Status**: Badge aktif/tidak aktif
- ⚙️ **Aksi**: Tombol Edit dan Hapus

#### 4. Operasi Massal (Bulk Operations)
- Pilih multiple outlet dengan checkbox
- Tombol "Aktifkan Terpilih"
- Tombol "Nonaktifkan Terpilih"
- Counter jumlah outlet terpilih
- Shift-click untuk seleksi rentang

#### 5. Form Outlet (Create/Edit)

**Field Wajib**:
- Nama Outlet
- Alamat Lengkap
- Kota
- Telepon

**Field Opsional**:
- Provinsi
- Kode Pos
- Email (dengan validasi format)
- Latitude (koordinat GPS)
- Longitude (koordinat GPS)
- Jam Buka (time picker)
- Jam Tutup (time picker)
- Status Aktif (checkbox)

## API Endpoints

### Pengaturan Tenant

| Endpoint | Metode | Deskripsi |
|----------|--------|-----------|
| `/api/admin/settings/tenant/` | GET | Dapatkan pengaturan tenant |
| `/api/admin/settings/tenant/{id}/` | PUT/PATCH | Update pengaturan tenant |
| `/api/admin/settings/tenant/{id}/upload_logo/` | POST | Upload logo tenant |
| `/api/admin/settings/tenant/{id}/delete_logo/` | DELETE | Hapus logo tenant |

### Manajemen Outlet

| Endpoint | Metode | Deskripsi |
|----------|--------|-----------|
| `/api/admin/settings/outlets/` | GET | Daftar outlet dengan filter |
| `/api/admin/settings/outlets/` | POST | Buat outlet baru |
| `/api/admin/settings/outlets/{id}/` | GET | Detail outlet |
| `/api/admin/settings/outlets/{id}/` | PUT/PATCH | Update outlet |
| `/api/admin/settings/outlets/{id}/` | DELETE | Hapus outlet (soft delete) |
| `/api/admin/settings/outlets/stats/` | GET | Statistik outlet |
| `/api/admin/settings/outlets/bulk_update/` | POST | Update massal |

## Contoh Penggunaan API

### 1. Mendapatkan Pengaturan Tenant
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/admin/settings/tenant/
```

### 2. Update Pengaturan Tenant
```bash
curl -X PATCH http://localhost:8000/api/admin/settings/tenant/1/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Restoran Saya",
    "primary_color": "#FF0000",
    "tax_rate": "11.00"
  }'
```

### 3. Upload Logo
```bash
curl -X POST http://localhost:8000/api/admin/settings/tenant/1/upload_logo/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "logo=@/path/to/logo.png"
```

### 4. Membuat Outlet Baru
```bash
curl -X POST http://localhost:8000/api/admin/settings/outlets/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cabang Jakarta Pusat",
    "address": "Jl. Sudirman No. 123",
    "city": "Jakarta",
    "province": "DKI Jakarta",
    "postal_code": "12345",
    "phone": "+6281234567890",
    "opening_time": "10:00:00",
    "closing_time": "22:00:00",
    "is_active": true
  }'
```

### 5. Mendapatkan Statistik Outlet
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/admin/settings/outlets/stats/
```

### 6. Update Massal Outlet
```bash
curl -X POST http://localhost:8000/api/admin/settings/outlets/bulk_update/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "outlet_ids": [1, 2, 3],
    "updates": {
      "is_active": false
    }
  }'
```

## Panduan Testing

### Langkah 1: Restart Container Backend
```bash
cd /home/user/webapp
docker-compose restart backend
docker-compose logs -f backend
```

### Langkah 2: Akses Halaman Settings
1. Buka browser ke http://localhost:5175/settings
2. Hard refresh (Ctrl+Shift+R atau Cmd+Shift+R di Mac)

### Langkah 3: Test Pengaturan Tenant

#### ✅ Checklist Testing:

**Manajemen Logo:**
- [ ] Jika tidak ada logo, tampil placeholder dengan tombol "Upload Logo"
- [ ] Klik tombol "Upload Logo"
- [ ] Pilih file gambar (PNG/JPG)
- [ ] Preview gambar muncul
- [ ] Klik "Upload"
- [ ] Logo ter-upload dan ditampilkan
- [ ] Tombol "Delete Logo" muncul
- [ ] Klik "Delete Logo"
- [ ] Logo terhapus

**Informasi Bisnis:**
- [ ] Semua field terisi dengan data saat ini
- [ ] Ubah Nama Tenant
- [ ] Ubah Telepon, Email, Website
- [ ] Edit Deskripsi
- [ ] Coba email tidak valid → error muncul
- [ ] Coba nama tenant kosong → error muncul

**Warna Branding:**
- [ ] Klik color picker warna utama
- [ ] Pilih warna baru
- [ ] Field teks ter-update
- [ ] Ketik kode hex manual (#FF0000)
- [ ] Color picker ter-update
- [ ] Coba hex tidak valid → error muncul
- [ ] Ulangi untuk warna sekunder

**Pengaturan Keuangan:**
- [ ] Ubah Tarif Pajak (misal: 11.50)
- [ ] Ubah Biaya Layanan (misal: 6.00)
- [ ] Nilai menerima desimal

**Simpan Pengaturan:**
- [ ] Klik tombol "Save Settings"
- [ ] Tombol menampilkan "Saving..." selama proses
- [ ] Alert sukses muncul
- [ ] Refresh halaman untuk verifikasi perubahan tersimpan

### Langkah 4: Test Manajemen Outlet

**Dashboard Statistik:**
- [ ] Total Outlet ditampilkan
- [ ] Outlet Aktif dihitung benar
- [ ] Outlet Tidak Aktif dihitung benar
- [ ] Jumlah Kota ditampilkan benar

**Sistem Filter:**
- [ ] Ketik di kotak pencarian
- [ ] Tunggu debounce (500ms)
- [ ] Tabel terfilter sesuai pencarian
- [ ] Pilih filter status (Aktif/Tidak Aktif)
- [ ] Tabel ter-update
- [ ] Pilih filter kota
- [ ] Tabel terfilter berdasarkan kota
- [ ] Clear filter → semua outlet ditampilkan

**Tabel Outlet:**
- [ ] Outlet ditampilkan di tabel
- [ ] Kolom checkbox untuk seleksi
- [ ] Nama outlet dan ID ditampilkan
- [ ] Detail lokasi (kota, provinsi, alamat)
- [ ] Info kontak (telepon, email)
- [ ] Jam operasional terformat dengan benar
- [ ] Badge status dengan warna (hijau=aktif, merah=tidak aktif)
- [ ] Tombol Edit dan Hapus tersedia

**Buat Outlet:**
- [ ] Klik tombol "Add Outlet"
- [ ] Modal terbuka
- [ ] Isi field wajib: Nama, Alamat, Kota, Telepon
- [ ] Isi field opsional
- [ ] Set jam buka dan tutup
- [ ] Centang checkbox "Active"
- [ ] Klik "Create Outlet"
- [ ] Outlet baru muncul di tabel
- [ ] Alert sukses ditampilkan

**Edit Outlet:**
- [ ] Klik tombol Edit pada outlet
- [ ] Modal terbuka dengan data outlet
- [ ] Ubah nama outlet
- [ ] Ubah jam operasional
- [ ] Klik "Update Outlet"
- [ ] Perubahan terlihat di tabel
- [ ] Alert sukses ditampilkan

**Hapus Outlet:**
- [ ] Klik tombol Delete pada outlet testing
- [ ] Modal konfirmasi terbuka
- [ ] Nama outlet ditampilkan
- [ ] Klik "Cancel" → modal tutup, tidak ada penghapusan
- [ ] Klik Delete lagi
- [ ] Klik "Delete Outlet" → outlet terhapus
- [ ] Alert sukses ditampilkan

**Operasi Massal:**
- [ ] Centang checkbox untuk 2-3 outlet
- [ ] Toolbar aksi massal muncul
- [ ] Menampilkan jumlah outlet terpilih
- [ ] Klik "Nonaktifkan Terpilih"
- [ ] Outlet terpilih menjadi tidak aktif
- [ ] Badge status berubah menjadi merah
- [ ] Centang lagi
- [ ] Klik "Aktifkan Terpilih"
- [ ] Outlet menjadi aktif kembali

**Select All:**
- [ ] Klik checkbox di header tabel
- [ ] Semua outlet di halaman terpilih
- [ ] Klik lagi → semua tidak terpilih

**Pagination:**
- [ ] Jika lebih dari 10 outlet, pagination muncul
- [ ] Klik "Next" → halaman berikutnya
- [ ] Klik "Previous" → kembali
- [ ] Ubah ukuran halaman (25, 50)
- [ ] Tabel ter-update dengan ukuran baru
- [ ] Counter menampilkan "Showing X-Y of Z" dengan benar

## Validasi Form

### Pengaturan Tenant:
- Nama tenant wajib diisi
- Email harus format valid
- Warna harus format hex valid (#RRGGBB)
- File logo maksimal 2MB
- File logo harus format gambar

### Form Outlet:
- Nama outlet wajib diisi
- Alamat wajib diisi
- Kota wajib diisi
- Telepon wajib diisi
- Email harus format valid (jika diisi)

## Troubleshooting

### Masalah: 404 Error pada Endpoints Settings

**Penyebab**: Container backend belum direstart

**Solusi**:
```bash
cd /home/user/webapp
docker-compose restart backend
docker-compose logs -f backend
```

### Masalah: Halaman Settings Tidak Loading

**Penyebab**: Frontend belum mendeteksi route baru

**Solusi**:
```bash
docker-compose restart admin
# Hard refresh browser: Ctrl+Shift+R
```

### Masalah: "No tenant found" Error

**Penyebab**: User tidak terasosiasi dengan tenant

**Solusi**: Verifikasi asosiasi tenant user:
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/tenants/me/
```

### Masalah: Upload Logo Gagal

**Penyebab**: File terlalu besar atau format salah

**Solusi**:
- Pastikan file gambar kurang dari 2MB
- Gunakan format yang didukung: PNG, JPG, JPEG, GIF
- Periksa permission direktori media

### Masalah: Pembuatan Outlet Gagal

**Penyebab**: Auto-assignment tenant tidak bekerja

**Solusi**: Verifikasi TenantMiddleware mengatur context tenant dengan benar

### Masalah: Warna Tidak Ter-update

**Penyebab**: Format hex tidak valid

**Solusi**: Pastikan format warna adalah #RRGGBB (6 digit hex dengan prefix #)

### Masalah: Statistik Tidak Loading

**Penyebab**: Query outlet mengembalikan hasil kosong

**Solusi**:
```bash
# Test endpoint stats secara langsung
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/admin/settings/outlets/stats/
```

## Keamanan

### Upload File
- Validasi tipe file (hanya gambar)
- Batas ukuran file (2MB)
- Penyimpanan file aman di direktori media
- Penghapusan otomatis logo lama saat penggantian

### Validasi Data
- Validasi field wajib
- Validasi format email
- Validasi format warna hex
- Validasi nomor telepon
- Presisi desimal untuk pengaturan keuangan

### Kontrol Akses
- Autentikasi wajib untuk semua endpoint
- Permission berbasis peran (Admin, Owner, Manager)
- Isolasi data multi-tenant
- Bypass super admin untuk maintenance

### Soft Delete
- Outlet menggunakan soft delete (is_active=False)
- Data dipertahankan untuk audit trail
- Dapat diaktifkan kembali jika diperlukan

## Fitur Tambahan di Masa Depan

### Jangka Pendek
- [ ] Tampilan peta outlet dengan Google Maps
- [ ] Import outlet dari CSV
- [ ] Export outlet ke CSV
- [ ] Galeri foto outlet
- [ ] Jam operasional per hari

### Jangka Menengah
- [ ] Dukungan multi-bahasa
- [ ] Metrik performa outlet
- [ ] Konfigurasi radius pengiriman
- [ ] Penugasan staff per outlet
- [ ] Inventory per outlet

### Jangka Panjang
- [ ] Fitur manajemen franchise
- [ ] Penugasan regional manager
- [ ] Analytics lanjutan per outlet
- [ ] Review customer per outlet
- [ ] Automated reporting outlet

## Kesimpulan

Fitur Manajemen Pengaturan menyediakan solusi komprehensif untuk mengelola konfigurasi tenant dan outlet. Interface yang intuitif untuk pengaturan bisnis, kustomisasi branding, dan manajemen multi-lokasi.

**Manfaat Utama**:
✅ Manajemen konfigurasi terpusat
✅ Kustomisasi branding mudah
✅ Manajemen multi-outlet efisien
✅ Filter dan pencarian komprehensif
✅ Operasi massal untuk produktivitas
✅ Statistik dan insight real-time
✅ Desain mobile-responsive
✅ Upload file aman

**Langkah Selanjutnya**:
1. Restart container backend untuk load endpoint baru
2. Test semua fungsionalitas menggunakan panduan testing
3. Konfigurasi media storage produksi (S3, dll)
4. Setup CDN untuk delivery logo
5. Konfigurasi backup untuk gambar yang di-upload

---
**Versi Dokumentasi**: 1.0
**Terakhir Diperbarui**: 28 Desember 2024
**Penyelesaian Fitur**: 100%
