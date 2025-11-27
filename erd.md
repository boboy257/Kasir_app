# Entity Relationship Diagram (ERD) - Aplikasi Kasir

## Tabel Utama

### 1. user
- id (PK)
- username (UNIQUE)
- password

### 2. produk  
- id (PK)
- barcode (UNIQUE)
- nama
- harga
- stok

### 3. transaksi
- id (PK)
- tanggal
- total

### 4. detail_transaksi
- id (PK)
- transaksi_id (FK → transaksi.id)
- produk_nama
- jumlah
- harga
- subtotal

### 5. log_aktivitas
- id (PK)
- username
- aktivitas
- tanggal
- detail

## Relasi
- transaksi.id → detail_transaksi.transaksi_id
- log_aktivitas.username → user.username