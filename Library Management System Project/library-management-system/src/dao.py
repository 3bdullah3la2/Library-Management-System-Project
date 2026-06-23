from .database import get_connection
from .models import Book, Member, Borrow
from .validators import validate_isbn, validate_email, validate_phone, validate_year
from datetime import datetime, timedelta
from typing import List, Optional

# ---------- KİTAP ----------
def add_book(book: Book) -> int:
    if not book.title or not book.author:
        raise ValueError("Başlık ve yazar zorunludur.")
    if not validate_isbn(book.isbn):
        raise ValueError("Geçersiz ISBN formatı (13 haneli olmalı).")
    if not validate_year(book.year):
        raise ValueError(f"Yıl 1400 ile {datetime.now().year} arasında olmalı.")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO books (title, author, isbn, year, available) VALUES (?, ?, ?, ?, ?)",
            (book.title, book.author, book.isbn, book.year, book.available)
        )
        conn.commit()
        return cursor.lastrowid

def update_book(book_id: int, **kwargs) -> None:
    allowed = ['title', 'author', 'isbn', 'year', 'available']
    updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not updates:
        return
    # validasyon
    if 'isbn' in updates and not validate_isbn(updates['isbn']):
        raise ValueError("Geçersiz ISBN.")
    if 'year' in updates and not validate_year(updates['year']):
        raise ValueError("Geçersiz yıl.")
    with get_connection() as conn:
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [book_id]
        conn.execute(f"UPDATE books SET {set_clause} WHERE id = ?", values)
        conn.commit()

def delete_book(book_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()

def get_book(book_id: int) -> Optional[Book]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    return Book(**row) if row else None

def search_books(keyword: str, available_only: bool = False) -> List[Book]:
    """Başlık, yazar veya ISBN'de arama"""
    with get_connection() as conn:
        query = "SELECT * FROM books WHERE (title LIKE ? OR author LIKE ? OR isbn LIKE ?)"
        params = [f'%{keyword}%'] * 3
        if available_only:
            query += " AND available = 1"
        rows = conn.execute(query, params).fetchall()
    return [Book(**row) for row in rows]

def list_all_books() -> List[Book]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM books ORDER BY title").fetchall()
    return [Book(**row) for row in rows]

# ---------- ÜYE ----------
def add_member(member: Member) -> int:
    if not member.name:
        raise ValueError("İsim zorunludur.")
    if not validate_email(member.email):
        raise ValueError("Geçersiz e-posta adresi.")
    if not validate_phone(member.phone):
        raise ValueError("Telefon numarası formatı geçersiz (örn: 0555 123 4567).")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO members (name, email, phone) VALUES (?, ?, ?)",
            (member.name, member.email, member.phone)
        )
        conn.commit()
        return cursor.lastrowid

def update_member(member_id: int, **kwargs) -> None:
    allowed = ['name', 'email', 'phone']
    updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if 'email' in updates and not validate_email(updates['email']):
        raise ValueError("Geçersiz e-posta.")
    if 'phone' in updates and not validate_phone(updates['phone']):
        raise ValueError("Geçersiz telefon.")
    with get_connection() as conn:
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [member_id]
        conn.execute(f"UPDATE members SET {set_clause} WHERE id = ?", values)
        conn.commit()

def delete_member(member_id: int) -> None:
    with get_connection() as conn:
        # Önce ödünç kayıtlarını sil (CASCADE ile otomatik ama manuel de yapabiliriz)
        conn.execute("DELETE FROM members WHERE id = ?", (member_id,))
        conn.commit()

def get_member(member_id: int) -> Optional[Member]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()
    return Member(**row) if row else None

def search_members(keyword: str) -> List[Member]:
    with get_connection() as conn:
        query = "SELECT * FROM members WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?"
        params = [f'%{keyword}%'] * 3
        rows = conn.execute(query, params).fetchall()
    return [Member(**row) for row in rows]

def list_all_members() -> List[Member]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM members ORDER BY name").fetchall()
    return [Member(**row) for row in rows]

# ---------- ÖDÜNÇ İŞLEMLERİ ----------
def borrow_book(book_id: int, member_id: int, days: int = 14) -> int:
    """Kitabı üyeye ödünç verir. days: iade süresi (gün)"""
    book = get_book(book_id)
    if not book:
        raise ValueError("Kitap bulunamadı.")
    if not book.available:
        raise ValueError("Kitap zaten ödünçte.")
    member = get_member(member_id)
    if not member:
        raise ValueError("Üye bulunamadı.")
    
    borrow_date = datetime.now().date()
    due_date = borrow_date + timedelta(days=days)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO borrows (book_id, member_id, borrow_date, due_date) VALUES (?, ?, ?, ?)",
            (book_id, member_id, borrow_date.isoformat(), due_date.isoformat())
        )
        conn.commit()
        return cursor.lastrowid

def return_book(book_id: int) -> None:
    """Kitabı iade alır (en son açık ödünç kaydını kapatır)"""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM borrows WHERE book_id = ? AND return_date IS NULL ORDER BY borrow_date DESC LIMIT 1",
            (book_id,)
        ).fetchone()
        if not row:
            raise ValueError("Bu kitaba ait açık ödünç kaydı yok.")
        conn.execute(
            "UPDATE borrows SET return_date = ? WHERE id = ?",
            (datetime.now().date().isoformat(), row['id'])
        )
        conn.commit()

def get_borrow_history(book_id: Optional[int] = None, member_id: Optional[int] = None) -> List[dict]:
    """Ödünç geçmişini getirir. Kitap veya üye filtresi uygulanabilir."""
    query = """
        SELECT b.id, b.borrow_date, b.due_date, b.return_date,
               bk.title as book_title, m.name as member_name
        FROM borrows b
        JOIN books bk ON b.book_id = bk.id
        JOIN members m ON b.member_id = m.id
        WHERE 1=1
    """
    params = []
    if book_id:
        query += " AND b.book_id = ?"
        params.append(book_id)
    if member_id:
        query += " AND b.member_id = ?"
        params.append(member_id)
    query += " ORDER BY b.borrow_date DESC"
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]

def get_active_borrows() -> List[dict]:
    """İade edilmemiş ödünç listesi"""
    query = """
        SELECT b.id, bk.title as book_title, m.name as member_name,
               b.borrow_date, b.due_date,
               (julianday('now') - julianday(b.due_date)) as days_overdue
        FROM borrows b
        JOIN books bk ON b.book_id = bk.id
        JOIN members m ON b.member_id = m.id
        WHERE b.return_date IS NULL
        ORDER BY b.due_date
    """
    with get_connection() as conn:
        rows = conn.execute(query).fetchall()
    return [dict(row) for row in rows]

# ---------- RAPORLAR ----------
def most_borrowed_books(limit: int = 5) -> List[dict]:
    """En çok ödünç alınan kitaplar"""
    query = """
        SELECT bk.id, bk.title, bk.author, COUNT(b.id) as borrow_count
        FROM books bk
        JOIN borrows b ON bk.id = b.book_id
        GROUP BY bk.id
        ORDER BY borrow_count DESC
        LIMIT ?
    """
    with get_connection() as conn:
        rows = conn.execute(query, (limit,)).fetchall()
    return [dict(row) for row in rows]

def overdue_books() -> List[dict]:
    """Bugün itibarıyla gecikmiş kitaplar (iade edilmemiş)"""
    query = """
        SELECT bk.title, m.name, b.due_date,
               (julianday('now') - julianday(b.due_date)) as days_overdue
        FROM borrows b
        JOIN books bk ON b.book_id = bk.id
        JOIN members m ON b.member_id = m.id
        WHERE b.return_date IS NULL AND b.due_date < date('now')
        ORDER BY days_overdue DESC
    """
    with get_connection() as conn:
        rows = conn.execute(query).fetchall()
    return [dict(row) for row in rows]