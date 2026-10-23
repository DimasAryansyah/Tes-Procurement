from database import get_connection, init_db

init_db()

with get_connection() as connection:
    connection.execute(
        """
        INSERT OR IGNORE INTO users (name, email, role)
        VALUES (?, ?, ?)
        """,
        ("Demo Requester", "requester@example.com", "Requester")
    )

    connection.execute(
        """
        INSERT OR IGNORE INTO users (name, email, role)
        VALUES (?, ?, ?)
        """,
        ("Demo Approver", "approver@example.com", "Approver")
    )

    connection.execute(
        """
        INSERT OR IGNORE INTO users (name, email, role)
        VALUES (?, ?, ?)
        """,
        ("Demo Procurement", "procurement@example.com", "Procurement Staff")
    )

print("Data user demo berhasil disiapkan.")
