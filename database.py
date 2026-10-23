import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "procurement.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_connection() as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL CHECK (
                    role IN (
                        'Requester',
                        'Approver',
                        'Procurement Staff'
                    )
                )
            );

            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS purchase_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_number TEXT NOT NULL UNIQUE,
                requester_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                estimated_cost REAL NOT NULL CHECK (
                    estimated_cost >= 0
                ),
                status TEXT NOT NULL DEFAULT 'Draft' CHECK (
                    status IN (
                        'Draft',
                        'Submitted',
                        'Approved',
                        'Rejected',
                        'Ordered',
                        'Received'
                    )
                ),
                approval_note TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (requester_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS purchase_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                po_number TEXT NOT NULL UNIQUE,
                purchase_request_id INTEGER NOT NULL UNIQUE,
                supplier_id INTEGER NOT NULL,
                order_date TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (purchase_request_id)
                    REFERENCES purchase_requests(id),
                FOREIGN KEY (supplier_id)
                    REFERENCES suppliers(id)
            );

            CREATE TABLE IF NOT EXISTS goods_receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                purchase_order_id INTEGER NOT NULL UNIQUE,
                received_quantity INTEGER NOT NULL CHECK (
                    received_quantity > 0
                ),
                received_by INTEGER NOT NULL,
                received_date TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (purchase_order_id)
                    REFERENCES purchase_orders(id),
                FOREIGN KEY (received_by) REFERENCES users(id)
            );
        """)


if __name__ == "__main__":
    init_db()
    print("Database Procurement berhasil dibuat!")
    print(f"Lokasi database: {DATABASE_PATH}")
