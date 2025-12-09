"""
Generate 100 produk dummy untuk testing.
Produk akan punya barcode, nama, harga, dan stok random.
"""

import sqlite3
import random
from pathlib import Path

DB_PATH = Path("data/pos.db")

# Kategori produk
CATEGORIES = [
    "Makanan Ringan", "Minuman", "Alat Tulis", "Perlengkapan Mandi",
    "Makanan Instan", "Bumbu Dapur", "Obat-obatan", "Elektronik Kecil"
]

# Nama produk per kategori
PRODUCT_NAMES = {
    "Makanan Ringan": ["Chitato", "Cheetos", "Taro", "Lays", "Pringles", "Oreo", "Good Time"],
    "Minuman": ["Aqua", "Le Minerale", "Coca Cola", "Pepsi", "Sprite", "Fanta", "Teh Botol"],
    "Alat Tulis": ["Pulpen", "Pensil", "Penghapus", "Penggaris", "Buku Tulis", "Spidol", "Tip-Ex"],
    "Perlengkapan Mandi": ["Sabun", "Shampoo", "Pasta Gigi", "Sikat Gigi", "Handuk Kecil"],
    "Makanan Instan": ["Indomie", "Mie Sedaap", "Pop Mie", "Sarimi", "Supermi"],
    "Bumbu Dapur": ["Garam", "Gula", "Merica", "Kecap", "Saos", "Minyak Goreng"],
    "Obat-obatan": ["Paracetamol", "Antimo", "Tolak Angin", "Promag", "Bodrex"],
    "Elektronik Kecil": ["Baterai AA", "Baterai AAA", "Kabel USB", "Earphone", "Powerbank Mini"]
}

def generate_products():
    if not DB_PATH.exists():
        print("❌ Database tidak ditemukan! Jalankan aplikasi dulu.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("🎲 Generating 100 produk dummy...\n")
        
        count = 0
        for i in range(1, 101):
            # Random kategori
            category = random.choice(CATEGORIES)
            base_name = random.choice(PRODUCT_NAMES[category])
            
            # Variasi produk (ukuran, rasa, dll)
            variants = ["Original", "Large", "Small", "Jumbo", "Mini", "Pedas", "Manis", "Asin"]
            variant = random.choice(variants)
            nama = f"{base_name} {variant}"
            
            # Barcode unik (format: 89 + 11 digit)
            barcode = f"89{random.randint(10000000000, 99999999999)}"
            
            # Harga random (1000 - 50000)
            harga = random.randint(1, 50) * 1000
            
            # Stok random (0 - 100)
            stok = random.randint(0, 100)
            
            # Cek barcode duplikat
            cursor.execute("SELECT COUNT(*) FROM produk WHERE barcode = ?", (barcode,))
            if cursor.fetchone()[0] > 0:
                continue  # Skip kalau barcode duplikat
            
            # Insert produk
            cursor.execute(
                "INSERT INTO produk (barcode, nama, harga, stok) VALUES (?, ?, ?, ?)",
                (barcode, nama, harga, stok)
            )
            
            count += 1
            print(f"✅ {count:3d}. {nama:30s} | Rp {harga:,} | Stok: {stok}")
        
        conn.commit()
        print(f"\n🎉 Berhasil menambahkan {count} produk dummy!")
        
        # Summary
        cursor.execute("SELECT COUNT(*) FROM produk")
        total = cursor.fetchone()[0]
        print(f"📊 Total produk di database: {total}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    generate_products()