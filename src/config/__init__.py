"""
Config Package
==============
Centralized configuration untuk aplikasi

Usage:
    from src.config.paths import DB_PATH, STRUK_FOLDER
    from src.config.paths import ensure_folders_exist
    from src.config import NAMA_TOKO, ALAMAT_TOKO  # Legacy constants
"""

from .paths import (
    # Directories
    ROOT_DIR,
    DATA_FOLDER,
    RESOURCES_FOLDER,
    BACKUP_FOLDER,
    EXPORT_FOLDER,
    LOGS_FOLDER,
    STRUK_FOLDER,
    BARCODE_FOLDER,
    STYLES_FOLDER,
    ICONS_FOLDER,
    IMAGES_FOLDER,
    
    # Files
    DB_PATH,
    SETTINGS_FILE,
    
    # Helpers
    ensure_folders_exist,
    migrate_old_folders,
    get_backup_filename,
    get_export_filename,
    validate_paths,
)

# ✅ ADDED: Legacy constants (untuk backward compatibility)
# TODO: Nanti akan diganti dengan dynamic loading dari settings.json
NAMA_TOKO = "Toko Boboy"
ALAMAT_TOKO = "Perumahan Grand Sulawes No.U52"

__all__ = [
    # Directories
    "ROOT_DIR",
    "DATA_FOLDER",
    "RESOURCES_FOLDER",
    "BACKUP_FOLDER",
    "EXPORT_FOLDER",
    "LOGS_FOLDER",
    "STRUK_FOLDER",
    "BARCODE_FOLDER",
    "STYLES_FOLDER",
    "ICONS_FOLDER",
    "IMAGES_FOLDER",
    
    # Files
    "DB_PATH",
    "SETTINGS_FILE",
    
    # Helpers
    "ensure_folders_exist",
    "migrate_old_folders",
    "get_backup_filename",
    "get_export_filename",
    "validate_paths",
    
    # Legacy
    "NAMA_TOKO",
    "ALAMAT_TOKO",
]