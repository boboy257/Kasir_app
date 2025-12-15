"""
Input Validators
================
Validation utilities untuk form inputs
"""

import re
from typing import Tuple

class Validators:
    """Collection of input validators"""
    
    @staticmethod
    def validate_barcode(barcode: str) -> Tuple[bool, str]:
        """Validate barcode format"""
        if not barcode or not barcode.strip():
            return False, "Barcode tidak boleh kosong"
        
        barcode = barcode.strip()
        
        if len(barcode) < 4:
            return False, "Barcode minimal 4 karakter"
        
        if len(barcode) > 20:
            return False, "Barcode maksimal 20 karakter"
        
        if not re.match(r'^[A-Za-z0-9\-]+$', barcode):
            return False, "Barcode hanya boleh huruf, angka, dan strip (-)"
        
        return True, ""
    
    @staticmethod
    def validate_product_name(name: str) -> Tuple[bool, str]:
        """Validate product name"""
        if not name or not name.strip():
            return False, "Nama produk tidak boleh kosong"
        
        name = name.strip()
        
        if len(name) < 3:
            return False, "Nama produk minimal 3 karakter"
        
        if len(name) > 100:
            return False, "Nama produk maksimal 100 karakter"
        
        return True, ""
    
    @staticmethod
    def validate_price(price_str: str) -> Tuple[bool, str, float]:
        """Validate and parse price"""
        if not price_str or not price_str.strip():
            return False, "Harga tidak boleh kosong", 0.0
        
        # Remove formatting
        price_str = price_str.strip().replace("Rp", "").replace(".", "").replace(",", "")
        
        try:
            price = float(price_str)
        except ValueError:
            return False, "Harga harus berupa angka", 0.0
        
        if price < 0:
            return False, "Harga tidak boleh negatif", 0.0
        
        if price > 999999999:
            return False, "Harga terlalu besar", 0.0
        
        return True, "", price
    
    @staticmethod
    def validate_stock(stock_str: str) -> Tuple[bool, str, int]:
        """Validate and parse stock"""
        if not stock_str or not stock_str.strip():
            return True, "", 0  # Stock optional
        
        stock_str = stock_str.strip()
        
        try:
            stock = int(stock_str)
        except ValueError:
            return False, "Stok harus berupa angka bulat", 0
        
        if stock < 0:
            return False, "Stok tidak boleh negatif", 0
        
        if stock > 100000:
            return False, "Stok terlalu besar", 0
        
        return True, "", stock
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """Validate username"""
        if not username or not username.strip():
            return False, "Username tidak boleh kosong"
        
        username = username.strip()
        
        if len(username) < 3:
            return False, "Username minimal 3 karakter"
        
        if len(username) > 20:
            return False, "Username maksimal 20 karakter"
        
        if not re.match(r'^[A-Za-z0-9_]+$', username):
            return False, "Username hanya boleh huruf, angka, dan underscore"
        
        return True, ""
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """Validate password"""
        if not password or not password.strip():
            return False, "Password tidak boleh kosong"
        
        if len(password) < 4:
            return False, "Password minimal 4 karakter"
        
        if len(password) > 50:
            return False, "Password maksimal 50 karakter"
        
        return True, ""