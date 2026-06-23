import unittest
import sys
import os

# Proje kök dizinini sys.path'e ekleyelim
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.validators import validate_isbn, validate_email, validate_phone, validate_year

class TestValidators(unittest.TestCase):

    def test_validate_isbn(self):
        # Geçerli ISBN-13 (tireli veya tiresiz)
        self.assertTrue(validate_isbn("978-975-07-1234-5"))
        self.assertTrue(validate_isbn("9789750712345"))
        # Geçersiz (uzunluk, harf)
        self.assertFalse(validate_isbn("1234567890"))
        self.assertFalse(validate_isbn("978-975-07-1234-A"))
        self.assertFalse(validate_isbn("97897507123"))

    def test_validate_email(self):
        self.assertTrue(validate_email("ali@ornek.com"))
        self.assertTrue(validate_email("ali.veli@ornek.gov.tr"))
        self.assertFalse(validate_email("ali@ornek"))
        self.assertFalse(validate_email("aliornek.com"))
        self.assertFalse(validate_email("@ornek.com"))

    def test_validate_phone(self):
        # Türkiye formatı
        self.assertTrue(validate_phone("05551234567"))
        self.assertTrue(validate_phone("5551234567"))  # 0'sız da olur
        self.assertTrue(validate_phone("0555 123 4567"))
        self.assertTrue(validate_phone("0555-123-4567"))
        self.assertFalse(validate_phone("555123456"))   # 9 hane
        self.assertFalse(validate_phone("055512345678")) # 12 hane
        self.assertFalse(validate_phone("0555-123-45"))

    def test_validate_year(self):
        from datetime import datetime
        current_year = datetime.now().year
        self.assertTrue(validate_year(2023))
        self.assertTrue(validate_year(1800))
        self.assertFalse(validate_year(1399))
        self.assertFalse(validate_year(current_year + 1))
        self.assertFalse(validate_year(-5))

if __name__ == '__main__':
    unittest.main()