import sqlite3

DB_FILE = "ebookstore.db"


# -----------------------------
# Database helpers
# -----------------------------
def connect_db():
    """Open a connection to the database."""
    return sqlite3.connect(DB_FILE)


def setup_db():
    """Create tables and populate them if empty."""
    with connect_db() as conn:
        cur = conn.cursor()

        # create author table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS author (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                country TEXT NOT NULL
            )
        """)

        # create book table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS book (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author_id INTEGER NOT NULL,
                qty INTEGER NOT NULL,
                FOREIGN KEY (author_id) REFERENCES author(id)
            )
        """)

        # populate authors if empty
        cur.execute("SELECT COUNT(*) FROM author")
        if cur.fetchone()[0] == 0:
            authors = [
                (1290, "J.K. Rowling", "England"),
                (8937, "Charles Dickens", "England"),
                (2356, "C.S. Lewis", "Ireland"),
                (6380, "J.R.R. Tolkien", "South Africa"),
                (5620, "Lewis Carroll", "England")
            ]
            cur.executemany("INSERT INTO author VALUES (?, ?, ?)", authors)

        # populate books if empty
        cur.execute("SELECT COUNT(*) FROM book")
        if cur.fetchone()[0] == 0:
            books = [
                (3001, "A Tale of Two Cities", 8937, 30),
                (3002, "Harry Potter and the Philosopher's Stone", 1290, 40),
                (3003, "The Lion, the Witch and the Wardrobe", 2356, 25),
                (3004, "The Lord of the Rings", 6380, 37),
                (3005, "Alice’s Adventures in Wonderland", 5620, 12)
            ]
            cur.executemany("INSERT INTO book VALUES (?, ?, ?, ?)", books)
        conn.commit()


# -----------------------------
# Input validation
# -----------------------------
def check_id(input_str):
    """Make sure ID is a 4-digit number."""
    if input_str.isdigit() and len(input_str) == 4:
        return int(input_str)
    raise ValueError("ID must be a 4-digit number.")


def check_quantity(input_str):
    """Make sure quantity is a positive integer."""
    if input_str.isdigit() and int(input_str) >= 0:
        return int(input_str)
    raise ValueError("Quantity must be a non-negative number.")


def get_non_empty_input(input_str, field_name):
    """Ensure a string input is not empty."""
    if input_str.strip() == "":
        raise ValueError(f"{field_name} cannot be empty.")
    return input_str.strip()


# -----------------------------
# Book and author operations
# -----------------------------
def add_author():
    """Add a new author."""
    try:
        author_id = check_id(input("Enter a 4-digit author ID: "))
        name = get_non_empty_input(input("Author's name: "), "Name")
        country = get_non_empty_input(input("Country: "), "Country")
    except ValueError as ve:
        print(f"Oops! {ve}")
        return

    try:
        with connect_db() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO author (id, name, country) VALUES (?, ?, ?)",
                        (author_id, name, country))
            conn.commit()
            print(f"✅ Author '{name}' added. Nice one!")
    except sqlite3.IntegrityError:
        print("Hmm… that author ID already exists.")


def add_book():
    """Add a new book."""
    try:
        book_id = check_id(input("Type a 4-digit book ID: "))
        title = get_non_empty_input(input("Book title: "), "Title")
        author_id = check_id(input("Author ID (must exist): "))
        qty = check_quantity(input("Quantity of copies: "))
    except ValueError as ve:
        print(f"Oops! {ve}")
        return

    try:
        with connect_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM author WHERE id = ?", (author_id,))
            if not cur.fetchone():
                print("That author ID isn't in our records yet. Add author first.")
                return
            cur.execute("INSERT INTO book (id, title, author_id, qty) VALUES (?, ?, ?, ?)",
                        (book_id, title, author_id, qty))
            conn.commit()
            print(f"📚 '{title}' added successfully!")
    except sqlite3.IntegrityError:
        print("That book ID already exists. Try a different one.")


def update_book():
    """Update book details or author information."""
    try:
        book_id = check_id(input("Enter the book ID you want to update: "))
    except ValueError as ve:
        print(f"Oops! {ve}")
        return

    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT book.title, author.id, author.name, author.country, book.qty
            FROM book
            INNER JOIN author ON book.author_id = author.id
            WHERE book.id = ?
        """, (book_id,))
        result = cur.fetchone()

        if not result:
            print("No book found with that ID. Sorry!")
            return

        title, author_id, author_name, author_country, qty = result
        print(f"\nCurrent details:\nTitle: {title}\nQty: {qty}\n"
              f"Author: {author_name} ({author_country})")

        print("\nWhat do you want to update?")
        print("1. Quantity (default)")
        print("2. Title")
        print("3. Author details")
        choice = input("Your choice [1-3]: ").strip() or "1"

        try:
            if choice == "1":
                new_qty = check_quantity(input("Enter new quantity: "))
                cur.execute("UPDATE book SET qty = ? WHERE id = ?", (new_qty, book_id))
                conn.commit()
                print("✅ Quantity updated!")
            elif choice == "2":
                new_title = get_non_empty_input(input("Enter new title: "), "Title")
                cur.execute("UPDATE book SET title = ? WHERE id = ?", (new_title, book_id))
                conn.commit()
                print("✅ Title updated!")
            elif choice == "3":
                new_name = input(f"Author name [{author_name}]: ").strip() or author_name
                new_country = input(f"Author country [{author_country}]: ").strip() or author_country
                cur.execute("UPDATE author SET name = ?, country = ? WHERE id = ?",
                            (new_name, new_country, author_id))
                conn.commit()
                print("✅ Author details updated!")
            else:
                print("Hmm… invalid choice.")
        except ValueError as ve:
            print(f"Oops! {ve}")
        except sqlite3.Error as e:
            print(f"Database error: {e}")


def delete_book():
    """Delete a book."""
    try:
        book_id = check_id(input("Book ID to delete: "))
    except ValueError as ve:
        print(f"Oops! {ve}")
        return

    try:
        with connect_db() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM book WHERE id = ?", (book_id,))
            if cur.rowcount == 0:
                print("No book found with that ID.")
            else:
                conn.commit()
                print("✅ Book removed.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")


def search_books():
    """Search books by title, author or ID."""
    keyword = input("Type a keyword to search for: ").strip()
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT book.id, book.title, author.name, author.country, book.qty
            FROM book
            JOIN author ON book.author_id = author.id
            WHERE book.title LIKE ? OR author.name LIKE ? OR CAST(book.id AS TEXT) LIKE ?
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        results = cur.fetchall()

    if results:
        print("\nSearch results:")
        for book in results:
            print(f"ID: {book[0]} | Title: {book[1]} | Author: {book[2]} ({book[3]}) | Qty: {book[4]}")
    else:
        print("No books matched that keyword.")


def view_all_books():
    """Show all books with author info."""
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT book.title, author.name, author.country
            FROM book
            JOIN author ON book.author_id = author.id
            ORDER BY book.id
        """)
        results = cur.fetchall()

    if results:
        print("\nAll books --------------------------------------------------")
        for title, author, country in results:
            print(f"Title: {title}\nAuthor: {author}\nCountry: {country}\n----------------------------------------------------")
    else:
        print("No books in the database yet.")


def view_all_authors():
    """Show all authors."""
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, country FROM author ORDER BY id")
        results = cur.fetchall()

    if results:
        print("\nAll authors --------------------------------------------------")
        for aid, name, country in results:
            print(f"ID: {aid}\nName: {name}\nCountry: {country}\n----------------------------------------------------")
    else:
        print("No authors in the database yet.")


# -----------------------------
# Menu system
# -----------------------------
def menu():
    """Display main menu and handle user input."""
    while True:
        print("\n=== Welcome to the eBookstore system ===")
        print("1. Add a book")
        print("2. Update a book")
        print("3. Remove a book")
        print("4. Search books")
        print("5. View all books")
        print("6. Add an author")
        print("7. View all authors")
        print("0. Exit")

        choice = input("What would you like to do? ").strip()
        options = {
            "1": add_book,
            "2": update_book,
            "3": delete_book,
            "4": search_books,
            "5": view_all_books,
            "6": add_author,
            "7": view_all_authors,
            "0": exit
        }

        action = options.get(choice)
        if action:
            action()
        else:
            print("Hmm… that’s not a valid choice, try again.")


# -----------------------------
# Run program
# -----------------------------
if __name__ == "__main__":
    setup_db()
    menu()