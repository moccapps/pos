import sqlite3

def initialize_database():
    conn = sqlite3.connect('pos_system.db')
    cursor = conn.cursor()

    # Create Inventory table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Inventory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        price REAL NOT NULL
                    )''')

    # Create Transactions table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        total_price REAL NOT NULL,
                        date TEXT NOT NULL,
                        FOREIGN KEY(item_id) REFERENCES Inventory(id)
                    )''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()