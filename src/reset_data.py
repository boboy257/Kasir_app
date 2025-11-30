import sys
import os
import sqlite3

# --- SETUP PATH (Biar sinkron sama aplikasi utama) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from src.database import DB_PATH
except ImportError:
    print("Error: Tidak bisa menemukan src/database.py")
    sys.exit(1)

def injeksi_data():
    print(f"TARGET DATABASE: {DB_PATH}")
    
    # 1. Pastikan folder ada
    folder_db = os.path.dirname(DB_PATH)
    if not os.path.exists(folder_db):
        os.makedirs(folder_db)

    # 2. Hapus file lama (Reset Total)
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("[Info] Database lama dihapus. Memulai dari nol.")
        except PermissionError:
            print("[ERROR] Database sedang dipakai! Tutup aplikasi kasir dulu.")
            return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- 3. BUAT SEMUA TABEL (LENGKAP) ---

    # A. Tabel Produk
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE,
            nama TEXT NOT NULL,
            harga REAL NOT NULL,
            stok INTEGER DEFAULT 0
        )
    """)
    
    # B. Tabel User
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # C. Tabel Transaksi (Header)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT NOT NULL,
            total REAL NOT NULL
        )
    """)

    # D. Tabel Detail Transaksi (DENGAN KOLOM DISKON)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detail_transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaksi_id INTEGER,
            produk_nama TEXT NOT NULL,
            jumlah INTEGER NOT NULL,
            harga REAL NOT NULL,
            diskon REAL DEFAULT 0,  
            subtotal REAL NOT NULL,
            FOREIGN KEY(transaksi_id) REFERENCES transaksi(id)
        )
    """)

    # E. Tabel Log Aktivitas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_aktivitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            aktivitas TEXT NOT NULL,
            tanggal TEXT NOT NULL,
            detail TEXT
        )
    """)

    # --- 4. ISI DATA DUMMY PRODUK ---
    barang_toko = [
        ("1001", "Indomie Goreng", 3500, 100),
        ("1002", "Indomie Soto", 3000, 50),
        ("1003", "Telur Ayam (kg)", 28000, 15),
        ("1004", "Beras Ramos 5kg", 65000, 20),
        ("1005", "Minyak Goreng 1L", 18000, 25),
        ("1006", "Gula Pasir 1kg", 16000, 30),
        ("1007", "Kopi Kapal Api", 1500, 200),
        ("1008", "Teh Celup Sariwangi", 8500, 40),
        ("1009", "Aqua Botol 600ml", 4000, 50),
        ("1010", "Le Minerale 600ml", 3500, 50),
        ("1011", "Roti Tawar", 15000, 5),
        ("1012", "Susu UHT Coklat", 6000, 24),
        ("1013", "Sabun Lifebuoy", 4500, 12),
        ("1014", "Shampo Pantene", 12000, 10),
        ("1015", "Pasta Gigi Pepsodent", 11000, 15),
        ("1016", "Deterjen Rinso", 22000, 8),
        ("1017", "Sunlight Jeruk", 15000, 20),
        ("1018", "Tepung Segitiga Biru", 14000, 15),
        ("1019", "Kecap Bango Kecil", 10000, 4),
        ("1020", "Saos Sambal ABC", 8000, 10),
        ("2001", "Rokok Sampoerna Mild", 32000, 50),
        ("2002", "Rokok Surya 12", 25000, 50),
        ("3001", "Gas LPG 3kg", 22000, 0),
    ]

    print("--- Mengisi Data Produk ---")
    count = 0
    for barcode, nama, harga, stok in barang_toko:
        try:
            cursor.execute("INSERT INTO produk (barcode, nama, harga, stok) VALUES (?, ?, ?, ?)", 
                         (barcode, nama, harga, stok))
            count += 1
        except Exception:
            pass
            
    # Buat user admin default juga
    # Password 'admin' di-hash manual (SHA256 untuk 'admin')
    pass_admin = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
    cursor.execute("INSERT INTO user (username, password) VALUES (?, ?)", ("admin", pass_admin))

    conn.commit()
    conn.close()
    print(f"\nSUKSES! Database baru telah dibuat dengan struktur LENGKAP.")

if __name__ == "__main__":
    injeksi_data()