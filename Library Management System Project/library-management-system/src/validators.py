import re

def validate_isbn(isbn: str) -> bool:
    """Basit ISBN-13 kontrolü (rakam ve tire kontrolü)"""
    cleaned = re.sub(r'[-\s]', '', isbn)
    return len(cleaned) == 13 and cleaned.isdigit()

def validate_email(email: str) -> bool:
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

def validate_phone(phone: str) -> bool:
    # Türkiye formatı: 05xx xxx xx xx veya 5xx xxx xx xx
    cleaned = re.sub(r'[\s()\-]', '', phone)
    return re.match(r'^(05\d{9}|5\d{9})$', cleaned) is not None

def validate_year(year: int) -> bool:
    from datetime import datetime
    current_year = datetime.now().year
    return 1400 <= year <= current_year