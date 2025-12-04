erDiagram
    USER {
        int id PK
        string username
        string password "Hash SHA256"
        string role "admin / kasir"
    }

    PRODUK {
        int id PK
        string barcode "Unique"
        string nama
        float harga
        int stok
    }

    TRANSAKSI {
        int id PK
        string tanggal "YYYY-MM-DD HH:MM:SS"
        float total
    }

    DETAIL_TRANSAKSI {
        int id PK
        int transaksi_id FK "Relasi ke Transaksi"
        string produk_nama
        int jumlah
        float harga
        float diskon "Baru"
        float subtotal
    }

    LOG_AKTIVITAS {
        int id PK
        string username
        string aktivitas
        string tanggal
        string detail
    }

    %% RELASI ANTAR TABEL
    TRANSAKSI ||--|{ DETAIL_TRANSAKSI : "memuat banyak item"}