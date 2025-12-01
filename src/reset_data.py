import sys
import os
import sqlite3

# --- SETUP PATH ---
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    # Kita import fungsi hash_password langsung dari sumbernya!
    # Ini MENJAMIN password yang dibuat di sini pasti bisa dibaca saat login nanti.
    from src.database import DB_PATH, hash_password
except ImportError:
    print("Error: Tidak bisa menemukan src/database.py")
    sys.exit(1)

def injeksi_data():
    print(f"TARGET DATABASE: {DB_PATH}")
    
    folder_db = os.path.dirname(DB_PATH)
    if not os.path.exists(folder_db):
        os.makedirs(folder_db)

    # Reset Database
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("[Info] Database lama dihapus. Resetting...")
        except PermissionError:
            print("[ERROR] Database sedang dipakai! Tutup aplikasi dulu.")
            return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- BUAT TABEL ---
    # 1. Produk
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE,
            nama TEXT NOT NULL,
            harga REAL NOT NULL,
            stok INTEGER DEFAULT 0
        )
    """)
    
    # 2. User
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'kasir'
        )
    """)

    # 3. Transaksi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT NOT NULL,
            total REAL NOT NULL
        )
    """)

    # 4. Detail Transaksi
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

    # 5. Log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_aktivitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            aktivitas TEXT NOT NULL,
            tanggal TEXT NOT NULL,
            detail TEXT
        )
    """)

    # --- ISI DATA ---
    
    # 1. Produk Dummy
    barang_toko = [
        ("1001", "Indomie Goreng", 3500, 100),
        ("1002", "Indomie Soto", 3000, 50),
        ("1003", "Telur Ayam (kg)", 28000, 15),
        ("1004", "Beras Ramos 5kg", 65000, 20),
        ("1005", "Minyak Goreng 1L", 18000, 25),
        ("1006", "Gula Pasir 1kg", 16000, 30),
        ("1009", "Aqua Botol 600ml", 4000, 50),
        ("1010", "Le Minerale 600ml", 3500, 50),
        ("1013", "Sabun Lifebuoy", 4500, 12),
        ("1019", "Kecap Bango Kecil", 10000, 4),
        ("2001", "Rokok Sampoerna Mild", 32000, 50),
        ("3001", "Gas LPG 3kg", 22000, 0),
    ]

    for barcode, nama, harga, stok in barang_toko:
        try:
            cursor.execute("INSERT INTO produk (barcode, nama, harga, stok) VALUES (?, ?, ?, ?)", (barcode, nama, harga, stok))
        except Exception: pass
            
    # 2. User (Generate Password Pakai Fungsi Asli)
    pass_admin = hash_password("admin")  # <--- Ini kuncinya!
    pass_kasir = hash_password("kasir")  # <--- Ini kuncinya!

    cursor.execute("INSERT INTO user (username, password, role) VALUES (?, ?, ?)", ("admin", pass_admin, "admin"))
    cursor.execute("INSERT INTO user (username, password, role) VALUES (?, ?, ?)", ("kasir", pass_kasir, "kasir"))

    conn.commit()
    conn.close()
    print(f"\nSUKSES! Database diperbarui dengan password yang 100% SINKRON.")

if __name__ == "__main__":
    injeksi_data()