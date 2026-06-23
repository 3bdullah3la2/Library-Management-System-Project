from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Book:
    id: Optional[int] = None
    title: str = ''
    author: str = ''
    isbn: str = ''
    year: int = 0
    available: bool = True
    created_at: Optional[str] = None

@dataclass
class Member:
    id: Optional[int] = None
    name: str = ''
    email: str = ''
    phone: str = ''
    registered_at: Optional[str] = None

@dataclass
class Borrow:
    id: Optional[int] = None
    book_id: int = 0
    member_id: int = 0
    borrow_date: str = ''
    due_date: str = ''
    return_date: Optional[str] = None
    book_title: Optional[str] = None
    member_name: Optional[str] = None