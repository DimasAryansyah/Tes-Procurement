import sqlite3
from pathlib import Path
from contextlib import contextmanager

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "procurement.db"


@contextmanager
def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


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

            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                description TEXT,
                unit TEXT NOT NULL DEFAULT 'Unit',
                created_at TEXT DEFAULT (
                    datetime('now', '+7 hours')
                )
            );

            CREATE TABLE IF NOT EXISTS purchase_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_number TEXT NOT NULL UNIQUE,
                requester_id INTEGER NOT NULL,
                item_id INTEGER,
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
                FOREIGN KEY (requester_id) REFERENCES users(id),
                FOREIGN KEY (item_id) REFERENCES items(id)
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

        # Tambahkan item_id ke tabel lama jika belum tersedia.
        # Data Purchase Request yang sudah ada tetap dipertahankan.
        columns = connection.execute(
            "PRAGMA table_info(purchase_requests)"
        ).fetchall()

        column_names = {column["name"] for column in columns}

        if "item_id" not in column_names:
            connection.execute("""
                ALTER TABLE purchase_requests
                ADD COLUMN item_id INTEGER
                REFERENCES items(id)
            """)

        # Sesuaikan timestamp baru dari UTC ke WIB.
        # Berlaku untuk insert berikutnya, bukan data lama.
        connection.executescript("""
            CREATE TRIGGER IF NOT EXISTS suppliers_wib_timestamp
            AFTER INSERT ON suppliers
            BEGIN
                UPDATE suppliers
                SET created_at = datetime('now', '+7 hours')
                WHERE id = NEW.id;
            END;

            CREATE TRIGGER IF NOT EXISTS purchase_requests_wib_timestamp
            AFTER INSERT ON purchase_requests
            BEGIN
                UPDATE purchase_requests
                SET created_at = datetime('now', '+7 hours')
                WHERE id = NEW.id;
            END;

            CREATE TRIGGER IF NOT EXISTS purchase_orders_wib_timestamp
            AFTER INSERT ON purchase_orders
            BEGIN
                UPDATE purchase_orders
                SET order_date = datetime('now', '+7 hours')
                WHERE id = NEW.id;
            END;

            CREATE TRIGGER IF NOT EXISTS goods_receipts_wib_timestamp
            AFTER INSERT ON goods_receipts
            BEGIN
                UPDATE goods_receipts
                SET received_date = datetime('now', '+7 hours')
                WHERE id = NEW.id;
            END;
        """)


if __name__ == "__main__":
    init_db()
    print("Database Procurement berhasil disiapkan!")
    print(f"Lokasi database: {DATABASE_PATH}")
