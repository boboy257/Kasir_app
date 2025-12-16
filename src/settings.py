"""
Settings Manager
================
Mengelola konfigurasi aplikasi dari settings.json

✅ UPDATED: Menggunakan centralized paths
"""

import json

# ✅ UPDATED: Import dari config/paths
from src.config.paths import SETTINGS_FILE

# Data Default (Jika file belum ada)
DEFAULT_SETTINGS = {
    "nama_toko": "Toko Boboy",
    "alamat_toko": "Jl. Contoh No. 123, Jakarta",
    "telepon": "0812-3456-7890",
    "footer_struk": "Terima Kasih Telah Berbelanja!\nBarang yang dibeli tidak dapat ditukar."
}

def load_settings():
    """
    Membaca setting dari file JSON
    
    Returns:
        dict: Settings dictionary
    """
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS

def save_settings(data):
    """
    Menyimpan setting ke file JSON
    
    Args:
        data (dict): Settings dictionary to save
    """
    # Pastikan folder data ada
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving settings: {e}")
        raise