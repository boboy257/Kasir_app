import sqlite3
from pathlib import Path
import shutil
from datetime import datetime
import csv

DB_PATH = Path("data/pos.db")

def create_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Tabel produk
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE,
            nama TEXT NOT NULL,
            harga REAL NOT NULL,
            stok INTEGER DEFAULT 0
        )
    """)

    # Tabel transaksi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT NOT NULL,
            total REAL NOT NULL
        )
    """)

    # Tabel detail transaksi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detail_transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaksi_id INTEGER,
            produk_nama TEXT NOT NULL,
            jumlah INTEGER NOT NULL,
            harga REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY(transaksi_id) REFERENCES transaksi(id)
        )
    """)

    conn.commit()
    conn.close()

def tambah_produk(barcode, nama, harga, stok=0):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO produk (barcode, nama, harga, stok)
        VALUES (?, ?, ?, ?)
    """, (barcode, nama, harga, stok))
    conn.commit()
    conn.close()

def cari_produk_dari_barcode(barcode):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama, harga FROM produk WHERE barcode = ?", (barcode,))
    produk = cursor.fetchone()
    conn.close()
    return produk

def semua_produk():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT barcode, nama, harga, stok FROM produk")
    produk = cursor.fetchall()
    conn.close()
    return produk

# === TAMBAHAN UNTUK KELOLA DATABASE ===

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(f"data/backup_pos_{timestamp}.db")
    backup_path.parent.mkdir(exist_ok=True)
    shutil.copy(DB_PATH, backup_path)
    return backup_path

def restore_database(backup_path):
    shutil.copy(backup_path, DB_PATH)
    print(f"Database berhasil dipulihkan dari {backup_path}")

def export_produk_ke_csv():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT barcode, nama, harga, stok FROM produk")
    rows = cursor.fetchall()
    conn.close()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = Path(f"data/produk_{timestamp}.csv")
    csv_path.parent.mkdir(exist_ok=True)

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["barcode", "nama", "harga", "stok"])  # Header
        writer.writerows(rows)

    return csv_path

def import_produk_dari_csv(csv_path):
    conn = create_connection()
    cursor = conn.cursor()

    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO produk (barcode, nama, harga, stok)
                VALUES (?, ?, ?, ?)
            """, (row["barcode"], row["nama"], float(row["harga"]), int(row["stok"])))

    conn.commit()
    conn.close()