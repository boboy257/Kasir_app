import json
from pathlib import Path

# Lokasi file settings.json (sejajar dengan database)
BASE_DIR = Path(__file__).parent.parent
SETTINGS_PATH = BASE_DIR / "data" / "settings.json"

# Data Default (Jika file belum ada)
DEFAULT_SETTINGS = {
    "nama_toko": "Toko Boboy",
    "alamat_toko": "Jl. Contoh No. 123, Jakarta",
    "telepon": "0812-3456-7890",
    "footer_struk": "Terima Kasih Telah Berbelanja!\nBarang yang dibeli tidak dapat ditukar."
}

def load_settings():
    """Membaca setting dari file JSON"""
    if not SETTINGS_PATH.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    
    try:
        with open(SETTINGS_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return DEFAULT_SETTINGS

def save_settings(data):
    """Menyimpan setting ke file JSON"""
    # Pastikan folder data ada
    SETTINGS_PATH.parent.mkdir(exist_ok=True)
    
    with open(SETTINGS_PATH, 'w') as f:
        json.dump(data, f, indent=4)