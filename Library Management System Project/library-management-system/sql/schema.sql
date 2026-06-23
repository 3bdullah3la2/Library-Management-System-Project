-- Kitaplar
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    isbn TEXT UNIQUE NOT NULL,
    year INTEGER CHECK (year > 1400 AND year <= strftime('%Y', 'now')),
    available BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Üyeler
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ödünç alma
CREATE TABLE IF NOT EXISTS borrows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    borrow_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
);

-- Index'ler
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
CREATE INDEX IF NOT EXISTS idx_borrows_member ON borrows(member_id);
CREATE INDEX IF NOT EXISTS idx_borrows_book ON borrows(book_id);

-- Trigger: Kitap ödünç verilince available = 0
CREATE TRIGGER IF NOT EXISTS trg_borrow_update
AFTER INSERT ON borrows
BEGIN
    UPDATE books SET available = 0 WHERE id = NEW.book_id;
END;

-- Trigger: Kitap iade edilince available = 1
CREATE TRIGGER IF NOT EXISTS trg_return_update
AFTER UPDATE OF return_date ON borrows
WHEN NEW.return_date IS NOT NULL
BEGIN
    UPDATE books SET available = 1 WHERE id = NEW.book_id;
END;

-- Başlangıç örnek veriler (isteğe bağlı)
INSERT OR IGNORE INTO books (title, author, isbn, year) VALUES
('Savaş ve Barış', 'Tolstoy', '978-975-07-1234-5', 1869),
('Suç ve Ceza', 'Dostoyevski', '978-975-07-5678-9', 1866);
INSERT OR IGNORE INTO members (name, email, phone) VALUES
('Ali Veli', 'ali@mail.com', '0555 123 4567'),
('Ayşe Yılmaz', 'ayse@mail.com', '0532 987 6543');