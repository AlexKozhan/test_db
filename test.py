import pytest
import sqlite3


@pytest.fixture(scope="function")
def db_connection():
    db_file = 'test_library.db'

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER NOT NULL
        )
    ''')

    cursor.execute('DELETE FROM books')

    input_books = [
        ('Преступление и наказание', 'Фёдор Достоевский', 1866),
        ('Война и мир', 'Лев Толстой', 1869),
        ('Мастер и Маргарита', 'Михаил Булгаков', 1967),
        ('Евгений Онегин', 'Александр Пушкин', 1833),
        ('Анна Каренина', 'Лев Толстой', 1877),
        ('Братья Карамазовы', 'Фёдор Достоевский', 1880)
    ]
    cursor.executemany('INSERT INTO books (title, author, year) VALUES (?, ?, ?)', input_books)

    connection.commit()

    yield connection

    connection.close()


class TestDatabaseOperations:
    def test_fetch_all_books(self, db_connection):
        cursor = db_connection.cursor()
        cursor.execute('SELECT * FROM books')
        books = cursor.fetchall()
        assert len(books) == 6

    def test_fetch_book_by_id(self, db_connection):
        cursor = db_connection.cursor()
        cursor.execute('SELECT * FROM books WHERE id=?', (1,))
        book = cursor.fetchone()
        assert book is not None

    def test_insert_book(self, db_connection):
        cursor = db_connection.cursor()
        cursor.execute('INSERT INTO books (title, author, year) VALUES (?, ?, ?)', ('Идиот', 'Фёдор Достоевский', 1869))
        db_connection.commit()

        cursor.execute('SELECT * FROM books WHERE title=?', ('Идиот',))
        book = cursor.fetchone()
        assert book is not None
        assert book[1] == 'Идиот'
        assert book[2] == 'Фёдор Достоевский'
        assert book[3] == 1869

    def test_update_book_info(self, db_connection):
        cursor = db_connection.cursor()

        cursor.execute('INSERT INTO books (title, author, year) VALUES (?, ?, ?)', ('Обломов', 'Иван Гончаров', 1859))
        db_connection.commit()

        cursor.execute('SELECT id FROM books WHERE title=?', ('Обломов',))
        book_id = cursor.fetchone()[0]

        cursor.execute('UPDATE books SET author=? WHERE id=?', ('Иван Александрович Гончаров', book_id))
        db_connection.commit()

        cursor.execute('SELECT * FROM books WHERE id=?', (book_id,))
        updated_book = cursor.fetchone()
        assert updated_book is not None
        assert updated_book[2] == 'Иван Александрович Гончаров'

    def test_remove_book(self, db_connection):
        cursor = db_connection.cursor()

        cursor.execute('INSERT INTO books (title, author, year) VALUES (?, ?, ?)', ('Чайка', 'Антон Чехов', 1896))
        db_connection.commit()

        cursor.execute('SELECT id FROM books WHERE title=?', ('Чайка',))
        book_id = cursor.fetchone()[0]

        cursor.execute('DELETE FROM books WHERE id=?', (book_id,))
        db_connection.commit()

        cursor.execute('SELECT * FROM books WHERE id=?', (book_id,))
        deleted_book = cursor.fetchone()
        assert deleted_book is None

    def test_fetch_nonexistent_book(self, db_connection):
        cursor = db_connection.cursor()

        cursor.execute('SELECT * FROM books WHERE id=?', (999,))
        book = cursor.fetchone()
        assert book is None
