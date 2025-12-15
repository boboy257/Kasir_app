"""
Data Formatters
===============
Formatting utilities untuk display data
"""

from datetime import datetime
from typing import Union

class Formatters:
    """Collection of data formatters"""
    
    @staticmethod
    def format_currency(amount: Union[int, float], prefix: str = "Rp") -> str:
        """
        Format number as currency (Indonesian Rupiah)
        
        Example:
            >>> Formatters.format_currency(1000000)
            'Rp 1.000.000'
        """
        try:
            amount = int(amount)
            formatted = f"{amount:,}".replace(",", ".")
            return f"{prefix} {formatted}"
        except (ValueError, TypeError):
            return f"{prefix} 0"
    
    @staticmethod
    def parse_currency(currency_str: str) -> float:
        """Parse currency string to float"""
        try:
            clean = currency_str.replace("Rp", "").replace(".", "").replace(",", "").strip()
            return float(clean)
        except (ValueError, AttributeError):
            return 0.0
    
    @staticmethod
    def format_date(date_obj: datetime, format_str: str = "%d/%m/%Y") -> str:
        """Format datetime object to string"""
        try:
            return date_obj.strftime(format_str)
        except (ValueError, AttributeError):
            return ""
    
    @staticmethod
    def format_datetime(date_obj: datetime, format_str: str = "%d/%m/%Y %H:%M:%S") -> str:
        """Format datetime object with time"""
        try:
            return date_obj.strftime(format_str)
        except (ValueError, AttributeError):
            return ""
    
    @staticmethod
    def format_percentage(value: Union[int, float], decimals: int = 2) -> str:
        """Format number as percentage"""
        try:
            return f"{value:.{decimals}f}%"
        except (ValueError, TypeError):
            return "0.00%"
    
    @staticmethod
    def format_stock_status(stock: int, threshold: int = 5) -> str:
        """Format stock with status indicator"""
        if stock <= 0:
            return "⚠️ HABIS (0)"
        elif stock < threshold:
            return f"⚠️ Rendah ({stock})"
        else:
            return f"✅ {stock}"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
        """Truncate long text with suffix"""
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix