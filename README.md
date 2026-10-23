# Procurement Management System

Aplikasi web sederhana untuk mengelola proses pengadaan barang (*procurement*), mulai dari pengajuan kebutuhan hingga pencatatan penerimaan barang. Project ini dibangun menggunakan Flask dan SQLite.

## Fitur Utama

- **Dashboard** — ringkasan Purchase Request, approval yang menunggu diproses, Purchase Order, Goods Receipt, dan daftar permintaan terbaru.
- **Supplier Management** — melihat, menambahkan, mengubah, dan menghapus data supplier.
- **Item Management** — melihat, menambahkan, mengubah, dan menghapus data barang.
- **Purchase Request (PR)** — membuat permintaan pengadaan, menyimpan Draft, mengajukan permintaan, mengedit atau menghapus Draft, serta melihat detail permintaan.
- **Approval** — menyetujui atau menolak Purchase Request berstatus Submitted.
- **Purchase Order (PO)** — membuat pesanan kepada supplier berdasarkan Purchase Request yang telah disetujui.
- **Goods Receipt (GR)** — mencatat penerimaan barang berdasarkan Purchase Order.
- **Validasi proses** — membatasi proses berdasarkan status dan mencegah pembuatan PO atau pencatatan penerimaan berulang untuk transaksi yang sama.

## Alur Bisnis

```text
Draft → Submitted → Approved → Ordered → Received
                ↘ Rejected
```

- **Draft:** Permintaan disimpan dan belum diajukan.
- **Submitted:** Permintaan diajukan untuk approval.
- **Approved:** Permintaan disetujui dan dapat diproses menjadi PO.
- **Rejected:** Permintaan ditolak pada tahap approval.
- **Ordered:** Purchase Order telah dibuat.
- **Received:** Penerimaan barang telah dicatat.

**Catatan:** Versi MVP ini mendukung penerimaan barang secara lengkap, bukan penerimaan sebagian. Jumlah penerimaan harus sama dengan jumlah pada Purchase Request.

## Teknologi

- Python
- Flask
- SQLite
- HTML, CSS, dan Jinja2
- Git dan GitHub

## Persyaratan

Pastikan Python 3 dan pip sudah terpasang di perangkat.

## Instalasi dan Menjalankan Aplikasi

### 1. Clone repository

```bash
git clone https://github.com/DimasAryansyah/Tes-Procurement.git
cd Tes-Procurement
```

### 2. Buat virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instal dependency

Jika tersedia file `requirements.txt`:

```bash
pip install -r requirements.txt
```

Jika belum tersedia, instal Flask:

```bash
pip install Flask
```

### 4. Siapkan data awal

Jika file `seed.py` tersedia dan database belum memiliki data demo, jalankan:

```bash
python seed.py
```

Periksa isi script terlebih dahulu sebelum menjalankannya kembali agar data yang sudah tersimpan tidak terdampak.

### 5. Jalankan aplikasi

```bash
python app.py
```

Buka browser dan akses:

```text
http://127.0.0.1:5001
```

Aplikasi memanggil `init_db()` saat `app.py` dijalankan. Database SQLite disimpan dalam file `procurement.db` di direktori project.

## Akun Demo

Aplikasi menggunakan akun demo berikut untuk menjalankan alur bisnis:

| Peran | Email |
|---|---|
| Requester | `requester@example.com` |
| Approver | `approver@example.com` |
| Procurement Staff | `procurement@example.com` |

Akun tersebut merupakan identitas demo yang dicari berdasarkan email dan role di database. Implementasi ini bukan sistem login berbasis password atau sistem autentikasi lengkap.

## Catatan

- Database menggunakan SQLite.
- Data disimpan secara lokal dalam `procurement.db`.
- Jangan menghapus database jika ingin mempertahankan data yang sudah tersimpan.
- Aplikasi ditujukan untuk MVP/demo.
- `debug=True` digunakan untuk pengembangan lokal dan tidak disarankan untuk server produksi.

## Repository

[GitHub — Tes-Procurement](https://github.com/DimasAryansyah/Tes-Procurement)
