import unittest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database import init_database, get_connection
from src.dao import *
from src.models import Book, Member

class TestDAO(unittest.TestCase):
    def setUp(self):
        init_database()
        self.conn = get_connection()
    
    def tearDown(self):
        self.conn.close()
        # Temizlik
        os.remove(os.path.join(os.path.dirname(__file__), '..', 'db', 'library.db'))
    
    def test_book_crud(self):
        b = Book(title="Test", author="Yazar", isbn="9781234567890", year=2023)
        bid = add_book(b)
        self.assertIsNotNone(get_book(bid))
        update_book(bid, title="Yeni Başlık")
        self.assertEqual(get_book(bid).title, "Yeni Başlık")
        delete_book(bid)
        self.assertIsNone(get_book(bid))
    
    def test_member_crud(self):
        m = Member(name="Ahmet", email="ahmet@test.com", phone="05551234567")
        mid = add_member(m)
        self.assertIsNotNone(get_member(mid))
        update_member(mid, name="Mehmet")
        self.assertEqual(get_member(mid).name, "Mehmet")
        delete_member(mid)
        self.assertIsNone(get_member(mid))
    
    def test_borrow_flow(self):
        b = Book(title="Kitap", author="Yazar", isbn="9781234567890", year=2023)
        bid = add_book(b)
        m = Member(name="Ali", email="ali@test.com", phone="05551234567")
        mid = add_member(m)
        borrow_book(bid, mid)
        self.assertEqual(get_book(bid).available, False)
        return_book(bid)
        self.assertEqual(get_book(bid).available, True)

if __name__ == '__main__':
    unittest.main()