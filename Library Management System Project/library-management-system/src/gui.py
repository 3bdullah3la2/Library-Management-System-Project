import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from .dao import *
from .models import Book, Member

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Kütüphane Yönetim Sistemi")
        self.root.geometry("1000x700")
        
        # Notebook (sekmeler)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sekmeleri oluştur
        self.tab_books = ttk.Frame(self.notebook)
        self.tab_members = ttk.Frame(self.notebook)
        self.tab_borrows = ttk.Frame(self.notebook)
        self.tab_reports = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_books, text="📖 Kitaplar")
        self.notebook.add(self.tab_members, text="👤 Üyeler")
        self.notebook.add(self.tab_borrows, text="🔄 Ödünç İşlemleri")
        self.notebook.add(self.tab_reports, text="📊 Raporlar")
        
        # Her sekmeyi kur
        self.setup_books_tab()
        self.setup_members_tab()
        self.setup_borrows_tab()
        self.setup_reports_tab()
        
        # Başlangıç verilerini yükle
        self.refresh_books()
        self.refresh_members()
        self.refresh_active_borrows()
    
    # ---------- KİTAPLAR SEKME ----------
    def setup_books_tab(self):
        frame = self.tab_books
        # Üst kısım: arama
        top = tk.Frame(frame)
        top.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(top, text="Ara:").pack(side=tk.LEFT)
        self.book_search_var = tk.StringVar()
        tk.Entry(top, textvariable=self.book_search_var, width=30).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="🔍 Ara", command=self.search_books).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="Tümünü Göster", command=self.refresh_books).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="➕ Yeni Kitap", command=self.add_book_dialog).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="✏️ Düzenle", command=self.edit_book_dialog).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="🗑 Sil", command=self.delete_book_selected).pack(side=tk.LEFT, padx=2)
        
        # Tablo
        columns = ('id', 'title', 'author', 'isbn', 'year', 'available')
        self.book_tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        self.book_tree.heading('id', text='ID')
        self.book_tree.heading('title', text='Başlık')
        self.book_tree.heading('author', text='Yazar')
        self.book_tree.heading('isbn', text='ISBN')
        self.book_tree.heading('year', text='Yıl')
        self.book_tree.heading('available', text='Mevcut')
        self.book_tree.column('id', width=40)
        self.book_tree.column('title', width=250)
        self.book_tree.column('author', width=180)
        self.book_tree.column('isbn', width=150)
        self.book_tree.column('year', width=60)
        self.book_tree.column('available', width=70)
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.book_tree.yview)
        self.book_tree.configure(yscrollcommand=scroll.set)
        self.book_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def refresh_books(self):
        for row in self.book_tree.get_children():
            self.book_tree.delete(row)
        for book in list_all_books():
            self.book_tree.insert('', tk.END, values=(
                book.id, book.title, book.author, book.isbn, book.year,
                '✅ Evet' if book.available else '❌ Hayır'
            ))
    
    def search_books(self):
        keyword = self.book_search_var.get().strip()
        if not keyword:
            self.refresh_books()
            return
        for row in self.book_tree.get_children():
            self.book_tree.delete(row)
        books = search_books(keyword)
        for book in books:
            self.book_tree.insert('', tk.END, values=(
                book.id, book.title, book.author, book.isbn, book.year,
                '✅ Evet' if book.available else '❌ Hayır'
            ))
    
    def add_book_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Yeni Kitap Ekle")
        dialog.geometry("400x300")
        entries = {}
        labels = ['Başlık', 'Yazar', 'ISBN', 'Yıl']
        for i, label in enumerate(labels):
            tk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = tk.Entry(dialog, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[label] = entry
        def save():
            try:
                book = Book(
                    title=entries['Başlık'].get().strip(),
                    author=entries['Yazar'].get().strip(),
                    isbn=entries['ISBN'].get().strip(),
                    year=int(entries['Yıl'].get().strip())
                )
                add_book(book)
                dialog.destroy()
                self.refresh_books()
                messagebox.showinfo("Başarılı", "Kitap eklendi.")
            except Exception as e:
                messagebox.showerror("Hata", str(e))
        tk.Button(dialog, text="Kaydet", command=save).grid(row=len(labels), column=1, pady=10)
    
    def edit_book_dialog(self):
        selected = self.book_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir kitap seçin.")
            return
        item = self.book_tree.item(selected[0])
        book_id = item['values'][0]
        book = get_book(book_id)
        if not book:
            messagebox.showerror("Hata", "Kitap bulunamadı.")
            return
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Kitap Düzenle - ID {book_id}")
        dialog.geometry("400x300")
        entries = {}
        labels = ['Başlık', 'Yazar', 'ISBN', 'Yıl']
        current_vals = [book.title, book.author, book.isbn, str(book.year)]
        for i, label in enumerate(labels):
            tk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = tk.Entry(dialog, width=30)
            entry.insert(0, current_vals[i])
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[label] = entry
        def save():
            try:
                updates = {}
                if entries['Başlık'].get().strip():
                    updates['title'] = entries['Başlık'].get().strip()
                if entries['Yazar'].get().strip():
                    updates['author'] = entries['Yazar'].get().strip()
                if entries['ISBN'].get().strip():
                    updates['isbn'] = entries['ISBN'].get().strip()
                if entries['Yıl'].get().strip():
                    updates['year'] = int(entries['Yıl'].get().strip())
                update_book(book_id, **updates)
                dialog.destroy()
                self.refresh_books()
                messagebox.showinfo("Başarılı", "Kitap güncellendi.")
            except Exception as e:
                messagebox.showerror("Hata", str(e))
        tk.Button(dialog, text="Güncelle", command=save).grid(row=len(labels), column=1, pady=10)
    
    def delete_book_selected(self):
        selected = self.book_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir kitap seçin.")
            return
        if messagebox.askyesno("Onay", "Bu kitabı silmek istediğinize emin misiniz?"):
            item = self.book_tree.item(selected[0])
            book_id = item['values'][0]
            try:
                delete_book(book_id)
                self.refresh_books()
                messagebox.showinfo("Başarılı", "Kitap silindi.")
            except Exception as e:
                messagebox.showerror("Hata", str(e))
    
    # ---------- ÜYELER SEKME ----------
    def setup_members_tab(self):
        frame = self.tab_members
        top = tk.Frame(frame)
        top.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(top, text="Ara:").pack(side=tk.LEFT)
        self.member_search_var = tk.StringVar()
        tk.Entry(top, textvariable=self.member_search_var, width=30).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="🔍 Ara", command=self.search_members).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="Tümünü Göster", command=self.refresh_members).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="➕ Yeni Üye", command=self.add_member_dialog).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="✏️ Düzenle", command=self.edit_member_dialog).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="🗑 Sil", command=self.delete_member_selected).pack(side=tk.LEFT, padx=2)
        
        columns = ('id', 'name', 'email', 'phone')
        self.member_tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        self.member_tree.heading('id', text='ID')
        self.member_tree.heading('name', text='Ad Soyad')
        self.member_tree.heading('email', text='E-posta')
        self.member_tree.heading('phone', text='Telefon')
        self.member_tree.column('id', width=40)
        self.member_tree.column('name', width=180)
        self.member_tree.column('email', width=250)
        self.member_tree.column('phone', width=150)
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.member_tree.yview)
        self.member_tree.configure(yscrollcommand=scroll.set)
        self.member_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def refresh_members(self):
        for row in self.member_tree.get_children():
            self.member_tree.delete(row)
        for member in list_all_members():
            self.member_tree.insert('', tk.END, values=(member.id, member.name, member.email, member.phone))
    
    def search_members(self):
        keyword = self.member_search_var.get().strip()
        if not keyword:
            self.refresh_members()
            return
        for row in self.member_tree.get_children():
            self.member_tree.delete(row)
        members = search_members(keyword)
        for m in members:
            self.member_tree.insert('', tk.END, values=(m.id, m.name, m.email, m.phone))
    
    def add_member_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Yeni Üye Ekle")
        dialog.geometry("400x250")
        entries = {}
        labels = ['Ad Soyad', 'E-posta', 'Telefon']
        for i, label in enumerate(labels):
            tk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = tk.Entry(dialog, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[label] = entry
        def save():
            try:
                member = Member(
                    name=entries['Ad Soyad'].get().strip(),
                    email=entries['E-posta'].get().strip(),
                    phone=entries['Telefon'].get().strip()
                )
                add_member(member)
                dialog.destroy()
                self.refresh_members()
                messagebox.showinfo("Başarılı", "Üye eklendi.")
            except Exception as e:
                messagebox.showerror("Hata", str(e))
        tk.Button(dialog, text="Kaydet", command=save).grid(row=len(labels), column=1, pady=10)
    
    def edit_member_dialog(self):
        selected = self.member_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir üye seçin.")
            return
        item = self.member_tree.item(selected[0])
        member_id = item['values'][0]
        member = get_member(member_id)
        if not member:
            messagebox.showerror("Hata", "Üye bulunamadı.")
            return
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Üye Düzenle - ID {member_id}")
        dialog.geometry("400x250")
        entries = {}
        labels = ['Ad Soyad', 'E-posta', 'Telefon']
        current_vals = [member.name, member.email, member.phone]
        for i, label in enumerate(labels):
            tk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = tk.Entry(dialog, width=30)
            entry.insert(0, current_vals[i])
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[label] = entry
        def save():
            try:
                updates = {}
                if entries['Ad Soyad'].get().strip():
                    updates['name'] = entries['Ad Soyad'].get().strip()
                if entries['E-posta'].get().strip():
                    updates['email'] = entries['E-posta'].get().strip()
                if entries['Telefon'].get().strip():
                    updates['phone'] = entries['Telefon'].get().strip()
                update_member(member_id, **updates)
                dialog.destroy()
                self.refresh_members()
                messagebox.showinfo("Başarılı", "Üye güncellendi.")
            except Exception as e:
                messagebox.showerror("Hata", str(e))
        tk.Button(dialog, text="Güncelle", command=save).grid(row=len(labels), column=1, pady=10)
    
    def delete_member_selected(self):
        selected = self.member_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir üye seçin.")
            return
        if messagebox.askyesno("Onay", "Bu üyeyi silmek istediğinize emin misiniz?"):
            item = self.member_tree.item(selected[0])
            member_id = item['values'][0]
            try:
                delete_member(member_id)
                self.refresh_members()
                messagebox.showinfo("Başarılı", "Üye silindi.")
            except Exception as e:
                messagebox.showerror("Hata", str(e))
    
    # ---------- ÖDÜNÇ SEKME ----------
    def setup_borrows_tab(self):
        frame = self.tab_borrows
        top = tk.Frame(frame)
        top.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(top, text="📤 Ödünç Ver", command=self.borrow_book_dialog).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="📥 İade Al", command=self.return_book_dialog).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="🔄 Yenile", command=self.refresh_active_borrows).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="📜 Geçmiş", command=self.show_history_dialog).pack(side=tk.LEFT, padx=2)
        
        columns = ('id', 'book', 'member', 'borrow_date', 'due_date', 'status')
        self.borrow_tree = ttk.Treeview(frame, columns=columns, show='headings', height=18)
        self.borrow_tree.heading('id', text='ID')
        self.borrow_tree.heading('book', text='Kitap')
        self.borrow_tree.heading('member', text='Üye')
        self.borrow_tree.heading('borrow_date', text='Ödünç Tarihi')
        self.borrow_tree.heading('due_date', text='İade Tarihi')
        self.borrow_tree.heading('status', text='Durum')
        self.borrow_tree.column('id', width=40)
        self.borrow_tree.column('book', width=200)
        self.borrow_tree.column('member', width=150)
        self.borrow_tree.column('borrow_date', width=100)
        self.borrow_tree.column('due_date', width=100)
        self.borrow_tree.column('status', width=120)
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.borrow_tree.yview)
        self.borrow_tree.configure(yscrollcommand=scroll.set)
        self.borrow_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def refresh_active_borrows(self):
        for row in self.borrow_tree.get_children():
            self.borrow_tree.delete(row)
        for item in get_active_borrows():
            due = item['due_date']
            days = item['days_overdue']
            status = "⏳ Süresinde" if days is None or days <= 0 else f"⚠️ {int(days)} gün gecikmiş"
            self.borrow_tree.insert('', tk.END, values=(
                item['id'], item['book_title'], item['member_name'],
                item['borrow_date'], due, status
            ))
    
    def borrow_book_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Ödünç Ver")
        dialog.geometry("400x200")
        tk.Label(dialog, text="Kitap ID:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        book_entry = tk.Entry(dialog, width=30)
        book_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(dialog, text="Üye ID:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        member_entry = tk.Entry(dialog, width=30)
        member_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(dialog, text="Gün (varsayılan 14):").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        days_entry = tk.Entry(dialog, width=30)
        days_entry.insert(0, "14")
        days_entry.grid(row=2, column=1, padx=5, pady=5)
        def do_borrow():
            try:
                book_id = int(book_entry.get())
                member_id = int(member_entry.get())
                days = int(days_entry.get())
                borrow_book(book_id, member_id, days)
                dialog.destroy()
                self.refresh_active_borrows()
                messagebox.showinfo("Başarılı", "Ödünç işlemi tamamlandı.")
            except Exception as e:
                messagebox.showerror("Hata", str(e))
        tk.Button(dialog, text="Ödünç Ver", command=do_borrow).grid(row=3, column=1, pady=10)
    
    def return_book_dialog(self):
        book_id = simpledialog.askinteger("İade", "İade edilecek kitap ID'sini girin:")
        if book_id:
            try:
                return_book(book_id)
                self.refresh_active_borrows()
                messagebox.showinfo("Başarılı", "İade alındı.")
            except Exception as e:
                messagebox.showerror("Hata", str(e))
    
    def show_history_dialog(self):
        # Tüm geçmişi gösteren basit bir pencere
        history = get_borrow_history()
        if not history:
            messagebox.showinfo("Bilgi", "Henüz ödünç kaydı yok.")
            return
        win = tk.Toplevel(self.root)
        win.title("Ödünç Geçmişi")
        win.geometry("600x400")
        tree = ttk.Treeview(win, columns=('book', 'member', 'borrow', 'return'), show='headings')
        tree.heading('book', text='Kitap')
        tree.heading('member', text='Üye')
        tree.heading('borrow', text='Ödünç Tarihi')
        tree.heading('return', text='İade Tarihi')
        tree.pack(fill=tk.BOTH, expand=True)
        for h in history:
            tree.insert('', tk.END, values=(
                h['book_title'], h['member_name'],
                h['borrow_date'], h['return_date'] if h['return_date'] else '☐ İade edilmedi'
            ))
    
    # ---------- RAPORLAR SEKME ----------
    def setup_reports_tab(self):
        frame = self.tab_reports
        text = tk.Text(frame, wrap=tk.WORD, font=('Consolas', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Butonlar
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(btn_frame, text="📊 En Çok Ödünç Alan Kitaplar",
                  command=lambda: self.show_report(text, 'most_borrowed')).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="⚠️ Gecikmiş Kitaplar",
                  command=lambda: self.show_report(text, 'overdue')).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="📋 Tüm Aktif Ödünçler",
                  command=lambda: self.show_report(text, 'active')).pack(side=tk.LEFT, padx=2)
    
    def show_report(self, text_widget, report_type):
        text_widget.delete(1.0, tk.END)
        if report_type == 'most_borrowed':
            data = most_borrowed_books(10)
            text_widget.insert(tk.END, "📈 EN ÇOK ÖDÜNÇ ALINAN KİTAPLAR\n")
            text_widget.insert(tk.END, "-" * 50 + "\n")
            for item in data:
                text_widget.insert(tk.END, f"{item['title']} - {item['author']} -> {item['borrow_count']} kez\n")
        elif report_type == 'overdue':
            data = overdue_books()
            text_widget.insert(tk.END, "⚠️ GECİKMİŞ KİTAPLAR\n")
            text_widget.insert(tk.END, "-" * 50 + "\n")
            if not data:
                text_widget.insert(tk.END, "Hiç gecikmiş kitap yok.\n")
            for item in data:
                text_widget.insert(tk.END, f"{item['title']} - {item['name']} -> {int(item['days_overdue'])} gün gecikmiş (İade: {item['due_date']})\n")
        elif report_type == 'active':
            data = get_active_borrows()
            text_widget.insert(tk.END, "📋 AKTİF ÖDÜNÇLER\n")
            text_widget.insert(tk.END, "-" * 50 + "\n")
            for item in data:
                status = "Süresinde" if item['days_overdue'] is None or item['days_overdue'] <= 0 else f"{int(item['days_overdue'])} gün gecikmiş"
                text_widget.insert(tk.END, f"{item['book_title']} -> {item['member_name']} (Bitiş: {item['due_date']}) - {status}\n")

# ---------- ÇALIŞTIRMA ----------
if __name__ == "__main__":
    from .database import init_database
    init_database()
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()