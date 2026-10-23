from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db, get_connection
from uuid import uuid4
import sqlite3

app = Flask(__name__)
app.secret_key = "procurement-development-key"

init_db()


@app.route("/")
def index():
    return render_template("index.html")

# Supplier Management Routes
@app.route("/suppliers")
def suppliers():
    with get_connection() as connection:
        supplier_list = connection.execute(
            "SELECT * FROM suppliers ORDER BY id DESC"
        ).fetchall()

    return render_template(
        "suppliers.html",
        suppliers=supplier_list
    )

# Supplier Management Add
@app.route("/suppliers/add", methods=["GET", "POST"])
def add_supplier():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        contact_person = request.form.get("contact_person", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        if not name:
            flash("Nama supplier wajib diisi.", "error")
            return redirect(url_for("add_supplier"))

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO suppliers
                    (name, contact_person, email, phone, address)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    name,
                    contact_person or None,
                    email or None,
                    phone or None,
                    address or None
                )
            )

        flash("Supplier berhasil ditambahkan.", "success")
        return redirect(url_for("suppliers"))

    return render_template("supplier_form.html")

# Supplier Management Edit
@app.route("/suppliers/<int:supplier_id>/edit", methods=["GET", "POST"])
def edit_supplier(supplier_id):
    with get_connection() as connection:
        supplier = connection.execute(
            "SELECT * FROM suppliers WHERE id = ?",
            (supplier_id,)
        ).fetchone()

    if supplier is None:
        flash("Supplier tidak ditemukan.", "error")
        return redirect(url_for("suppliers"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        contact_person = request.form.get("contact_person", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        if not name:
            flash("Nama supplier wajib diisi.", "error")
            return redirect(url_for(
                "edit_supplier", supplier_id=supplier_id
            ))

        with get_connection() as connection:
            connection.execute(
                """
                UPDATE suppliers
                SET name = ?,
                    contact_person = ?,
                    email = ?,
                    phone = ?,
                    address = ?
                WHERE id = ?
                """,
                (
                    name,
                    contact_person or None,
                    email or None,
                    phone or None,
                    address or None,
                    supplier_id
                )
            )

        flash("Data supplier berhasil diperbarui.", "success")
        return redirect(url_for("suppliers"))

    return render_template(
        "supplier_form.html",
        supplier=supplier
    )

# Supplier Management Delete
@app.route("/suppliers/<int:supplier_id>/delete", methods=["POST"])
def delete_supplier(supplier_id):
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM suppliers WHERE id = ?",
                (supplier_id,)
            )

            if cursor.rowcount == 0:
                flash("Supplier tidak ditemukan.", "error")
                return redirect(url_for("suppliers"))

        flash("Supplier berhasil dihapus.", "success")

    except Exception as error:
        from sqlite3 import IntegrityError

        if isinstance(error, IntegrityError):
            flash(
                "Supplier tidak dapat dihapus karena sudah digunakan "
                "dalam Purchase Order.",
                "error"
            )
        else:
            raise

    return redirect(url_for("suppliers"))


# Item Management Routes
@app.route("/items")
def items():
    with get_connection() as connection:
        item_list = connection.execute("""
            SELECT *
            FROM items
            ORDER BY id DESC
        """).fetchall()

    return render_template("items.html", items=item_list)


# Item Management Add
@app.route("/items/add", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        unit = request.form.get("unit", "").strip()

        if not name:
            flash("Nama barang wajib diisi.", "error")
            return redirect(url_for("add_item"))

        if not unit:
            flash("Satuan barang wajib diisi.", "error")
            return redirect(url_for("add_item"))

        with get_connection() as connection:
            connection.execute("""
                INSERT INTO items (name, category, description, unit)
                VALUES (?, ?, ?, ?)
            """, (
                name,
                category or None,
                description or None,
                unit
            ))

        flash("Barang berhasil ditambahkan.", "success")
        return redirect(url_for("items"))

    return render_template("item_form.html")


# Item Management Edit
@app.route("/items/<int:item_id>/edit", methods=["GET", "POST"])
def edit_item(item_id):
    with get_connection() as connection:
        item = connection.execute(
            "SELECT * FROM items WHERE id = ?",
            (item_id,)
        ).fetchone()

        if item is None:
            flash("Barang tidak ditemukan.", "error")
            return redirect(url_for("items"))

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            category = request.form.get("category", "").strip()
            description = request.form.get("description", "").strip()
            unit = request.form.get("unit", "").strip()

            if not name or not unit:
                flash(
                    "Nama dan satuan barang wajib diisi.",
                    "error"
                )
                return redirect(
                    url_for("edit_item", item_id=item_id)
                )

            connection.execute("""
                UPDATE items
                SET name = ?,
                    category = ?,
                    description = ?,
                    unit = ?
                WHERE id = ?
            """, (
                name,
                category or None,
                description or None,
                unit,
                item_id
            ))

            flash("Data barang berhasil diperbarui.", "success")
            return redirect(url_for("items"))

    return render_template("item_form.html", item=item)


# Item Management Delete
@app.route("/items/<int:item_id>/delete", methods=["POST"])
def delete_item(item_id):
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM items WHERE id = ?",
                (item_id,)
            )

            if cursor.rowcount == 0:
                flash("Barang tidak ditemukan.", "error")
                return redirect(url_for("items"))

        flash("Barang berhasil dihapus.", "success")

    except sqlite3.IntegrityError:
        flash(
            "Barang tidak dapat dihapus karena sudah digunakan "
            "dalam Purchase Request.",
            "error"
        )

    return redirect(url_for("items"))


# Purchase Request Routes
@app.route("/purchase-requests")
def purchase_requests():
    with get_connection() as connection:
        requests_list = connection.execute(
            """
            SELECT
                pr.*,
                u.name AS requester_name
            FROM purchase_requests pr
            JOIN users u ON pr.requester_id = u.id
            ORDER BY pr.id DESC
            """
        ).fetchall()

    return render_template(
        "purchase_requests.html",
        requests=requests_list
    )

# Purchase Request Add
@app.route("/purchase-requests/add", methods=["GET", "POST"])
def add_purchase_request():
    if request.method == "POST":
        item_id_raw = request.form.get("item_id", "").strip()
        description = request.form.get("description", "").strip()
        quantity_raw = request.form.get("quantity", "").strip()
        estimated_cost_raw = request.form.get(
            "estimated_cost", ""
        ).strip()
        action = request.form.get("action", "submit")

        # Validasi pilihan barang
        try:
            item_id = int(item_id_raw)
            if item_id <= 0:
                raise ValueError
        except (ValueError, TypeError):
            flash("Silakan pilih barang yang valid.", "error")
            return redirect(url_for("add_purchase_request"))

        # Validasi jumlah dan estimasi biaya
        try:
            quantity = int(quantity_raw)
            estimated_cost = float(estimated_cost_raw)

            if quantity <= 0 or estimated_cost < 0:
                raise ValueError

            if not (
                float("-inf") < estimated_cost < float("inf")
            ):
                raise ValueError

        except (ValueError, TypeError):
            flash(
                "Jumlah harus lebih dari 0 dan estimasi biaya "
                "harus berupa angka yang valid, minimal 0.",
                "error"
            )
            return redirect(url_for("add_purchase_request"))

        if action not in ("draft", "submit"):
            action = "submit"

        status = "Draft" if action == "draft" else "Submitted"

        with get_connection() as connection:
            # Ambil barang yang dipilih
            item = connection.execute(
                """
                SELECT id, name, description
                FROM items
                WHERE id = ?
                """,
                (item_id,)
            ).fetchone()

            if item is None:
                flash("Barang tidak ditemukan.", "error")
                return redirect(url_for("add_purchase_request"))

            requester = connection.execute(
                """
                SELECT id FROM users
                WHERE email = ? AND role = 'Requester'
                """,
                ("requester@example.com",)
            ).fetchone()

            if requester is None:
                flash(
                    "User Requester belum tersedia. Jalankan python seed.py.",
                    "error"
                )
                return redirect(url_for("add_purchase_request"))

            request_number = f"PR-{uuid4().hex[:8].upper()}"

            # Gunakan nama barang sebagai judul Purchase Request.
            # Jika deskripsi kosong, gunakan deskripsi barang.
            final_description = (
                description or item["description"] or ""
            )

            connection.execute(
                """
                INSERT INTO purchase_requests (
                    request_number,
                    requester_id,
                    item_id,
                    title,
                    description,
                    quantity,
                    estimated_cost,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request_number,
                    requester["id"],
                    item["id"],
                    item["name"],
                    final_description,
                    quantity,
                    estimated_cost,
                    status
                )
            )

        if status == "Draft":
            flash(
                "Purchase Request berhasil disimpan sebagai Draft.",
                "success"
            )
        else:
            flash(
                "Purchase Request berhasil diajukan untuk approval.",
                "success"
            )

        return redirect(url_for("purchase_requests"))

    # Ambil daftar barang untuk dropdown form
    with get_connection() as connection:
        items = connection.execute(
            """
            SELECT id, name, category, unit, description
            FROM items
            ORDER BY name ASC
            """
        ).fetchall()

    return render_template(
        "purchase_request_form.html",
        items=items
    )

# Purchase Request Edit
@app.route(
    "/purchase-requests/<int:request_id>/edit",
    methods=["GET", "POST"]
)
def edit_purchase_request(request_id):
    with get_connection() as connection:
        purchase_request = connection.execute(
            """
            SELECT *
            FROM purchase_requests
            WHERE id = ?
            """,
            (request_id,)
        ).fetchone()

        if purchase_request is None:
            flash("Purchase Request tidak ditemukan.", "error")
            return redirect(url_for("purchase_requests"))

        # Request yang sudah masuk proses approval tidak boleh diedit.
        if purchase_request["status"] != "Draft":
            flash(
                "Hanya Purchase Request berstatus Draft yang dapat diedit.",
                "error"
            )
            return redirect(url_for("purchase_requests"))

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            quantity_raw = request.form.get("quantity", "").strip()
            estimated_cost_raw = request.form.get(
                "estimated_cost", ""
            ).strip()

            if not title:
                flash("Judul permintaan wajib diisi.", "error")
                return redirect(
                    url_for(
                        "edit_purchase_request",
                        request_id=request_id
                    )
                )

            try:
                quantity = int(quantity_raw)
                estimated_cost = float(estimated_cost_raw)

                if quantity <= 0 or estimated_cost < 0:
                    raise ValueError

                if not (
                    float("-inf") < estimated_cost < float("inf")
                ):
                    raise ValueError

            except (ValueError, TypeError):
                flash(
                    "Jumlah harus lebih dari 0 dan estimasi biaya "
                    "harus berupa angka yang valid, minimal 0.",
                    "error"
                )
                return redirect(
                    url_for(
                        "edit_purchase_request",
                        request_id=request_id
                    )
                )

            connection.execute(
                """
                UPDATE purchase_requests
                SET title = ?,
                    description = ?,
                    quantity = ?,
                    estimated_cost = ?
                WHERE id = ? AND status = 'Draft'
                """,
                (
                    title,
                    description,
                    quantity,
                    estimated_cost,
                    request_id
                )
            )

            flash("Purchase Request berhasil diperbarui.", "success")
            return redirect(url_for("purchase_requests"))

    return render_template(
        "purchase_request_edit.html",
        purchase_request=purchase_request
    )

# Purchase Rqquest Delete
@app.route(
    "/purchase-requests/<int:request_id>/delete",
    methods=["POST"]
)
def delete_purchase_request(request_id):
    with get_connection() as connection:
        purchase_request = connection.execute(
            """
            SELECT id, status
            FROM purchase_requests
            WHERE id = ?
            """,
            (request_id,)
        ).fetchone()

        if purchase_request is None:
            flash("Purchase Request tidak ditemukan.", "error")
            return redirect(url_for("purchase_requests"))

        # Jangan menghapus request yang sudah diajukan
        # atau sudah masuk proses pengadaan.
        if purchase_request["status"] != "Draft":
            flash(
                "Hanya Purchase Request berstatus Draft yang dapat dihapus.",
                "error"
            )
            return redirect(url_for("purchase_requests"))

        connection.execute(
            """
            DELETE FROM purchase_requests
            WHERE id = ? AND status = 'Draft'
            """,
            (request_id,)
        )

    flash("Purchase Request berhasil dihapus.", "success")
    return redirect(url_for("purchase_requests"))

# Purchase Request Submit
@app.route(
    "/purchase-requests/<int:request_id>/submit",
    methods=["POST"]
)
def submit_purchase_request(request_id):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE purchase_requests
            SET status = 'Submitted'
            WHERE id = ? AND status = 'Draft'
            """,
            (request_id,)
        )

        if cursor.rowcount == 0:
            flash(
                "Request tidak ditemukan atau bukan berstatus Draft.",
                "error"
            )
        else:
            flash(
                "Purchase Request berhasil diajukan untuk approval.",
                "success"
            )

    return redirect(url_for("purchase_requests"))

# Purchase Request Approval
@app.route("/purchase-requests/<int:request_id>/approval", methods=["POST"])
def approve_purchase_request(request_id):
    action = request.form.get("action", "").strip()
    approval_note = request.form.get("approval_note", "").strip()

    if action not in ("approve", "reject"):
        flash("Aksi approval tidak valid.", "error")
        return redirect(url_for("purchase_requests"))

    new_status = "Approved" if action == "approve" else "Rejected"

    with get_connection() as connection:
        # Ambil user Approver demo
        approver = connection.execute(
            """
            SELECT id FROM users
            WHERE email = ? AND role = 'Approver'
            """,
            ("approver@example.com",)
        ).fetchone()

        if approver is None:
            flash("User Approver belum tersedia. Jalankan python seed.py.", "error")
            return redirect(url_for("purchase_requests"))

        # Hanya request berstatus Submitted yang boleh diproses
        cursor = connection.execute(
            """
            UPDATE purchase_requests
            SET status = ?, approval_note = ?
            WHERE id = ? AND status = 'Submitted'
            """,
            (
                new_status,
                approval_note or None,
                request_id
            )
        )

        if cursor.rowcount == 0:
            flash(
                "Request tidak ditemukan atau sudah diproses sebelumnya.",
                "error"
            )
            return redirect(url_for("purchase_requests"))

    flash(
        "Purchase Request berhasil disetujui."
        if action == "approve"
        else "Purchase Request berhasil ditolak.",
        "success"
    )

    return redirect(url_for("purchase_requests"))




@app.route("/purchase-orders")
def purchase_orders():
    with get_connection() as connection:
        orders = connection.execute(
            """
            SELECT
                po.*,
                s.name AS supplier_name,
                pr.request_number,
                pr.title AS request_title,
                pr.status AS request_status,
                gr.id AS receipt_id
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.id
            JOIN purchase_requests pr
                ON po.purchase_request_id = pr.id
            LEFT JOIN goods_receipts gr
                ON gr.purchase_order_id = po.id
            ORDER BY po.id DESC
            """
        ).fetchall()

    return render_template("purchase_orders.html", orders=orders)


# Purchase Order
@app.route(
    "/purchase-orders/create/<int:request_id>",
    methods=["GET", "POST"]
)
def create_purchase_order(request_id):
    with get_connection() as connection:
        purchase_request = connection.execute(
            """
            SELECT *
            FROM purchase_requests
            WHERE id = ?
            """,
            (request_id,)
        ).fetchone()

        if purchase_request is None:
            flash("Purchase Request tidak ditemukan.", "error")
            return redirect(url_for("purchase_requests"))

        if purchase_request["status"] != "Approved":
            flash(
                "PO hanya dapat dibuat dari request yang sudah disetujui.",
                "error"
            )
            return redirect(url_for("purchase_requests"))

        existing_order = connection.execute(
            """
            SELECT id FROM purchase_orders
            WHERE purchase_request_id = ?
            """,
            (request_id,)
        ).fetchone()

        if existing_order:
            flash("Purchase Request ini sudah memiliki PO.", "error")
            return redirect(url_for("purchase_orders"))

        if request.method == "POST":
            supplier_id = request.form.get("supplier_id", "").strip()
            notes = request.form.get("notes", "").strip()

            try:
                supplier_id = int(supplier_id)
            except (ValueError, TypeError):
                flash("Pilih supplier yang valid.", "error")
                return redirect(
                    url_for(
                        "create_purchase_order",
                        request_id=request_id
                    )
                )

            supplier = connection.execute(
                "SELECT id FROM suppliers WHERE id = ?",
                (supplier_id,)
            ).fetchone()

            if supplier is None:
                flash("Supplier tidak ditemukan.", "error")
                return redirect(
                    url_for(
                        "create_purchase_order",
                        request_id=request_id
                    )
                )

            po_number = f"PO-{uuid4().hex[:8].upper()}"

            try:
                connection.execute(
                    """
                    INSERT INTO purchase_orders (
                        po_number,
                        purchase_request_id,
                        supplier_id,
                        notes
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        po_number,
                        request_id,
                        supplier_id,
                        notes or None
                    )
                )

                connection.execute(
                    """
                    UPDATE purchase_requests
                    SET status = 'Ordered'
                    WHERE id = ? AND status = 'Approved'
                    """,
                    (request_id,)
                )

            except sqlite3.IntegrityError:
                flash(
                    "PO gagal dibuat. Request mungkin sudah memiliki PO.",
                    "error"
                )
                return redirect(url_for("purchase_orders"))

            flash(f"Purchase Order {po_number} berhasil dibuat.", "success")
            return redirect(url_for("purchase_orders"))

        suppliers = connection.execute(
            "SELECT * FROM suppliers ORDER BY name"
        ).fetchall()

    if not suppliers:
        flash("Tambahkan supplier terlebih dahulu.", "error")
        return redirect(url_for("suppliers"))

    return render_template(
        "purchase_order_form.html",
        purchase_request=purchase_request,
        suppliers=suppliers
    )

# 

@app.route("/goods-receipts")
def goods_receipts():
    with get_connection() as connection:
        receipts = connection.execute(
            """
            SELECT
                gr.*,
                po.po_number,
                pr.request_number,
                pr.title AS request_title,
                u.name AS receiver_name
            FROM goods_receipts gr
            JOIN purchase_orders po
                ON gr.purchase_order_id = po.id
            JOIN purchase_requests pr
                ON po.purchase_request_id = pr.id
            JOIN users u ON gr.received_by = u.id
            ORDER BY gr.id DESC
            """
        ).fetchall()

    return render_template("goods_receipts.html", receipts=receipts)

# Good Receipt 
@app.route(
    "/goods-receipts/create/<int:po_id>",
    methods=["GET", "POST"]
)
def create_goods_receipt(po_id):
    with get_connection() as connection:
        order = connection.execute(
            """
            SELECT
                po.id,
                po.po_number,
                pr.id AS request_id,
                pr.request_number,
                pr.title,
                pr.quantity AS requested_quantity,
                pr.status
            FROM purchase_orders po
            JOIN purchase_requests pr
                ON po.purchase_request_id = pr.id
            WHERE po.id = ?
            """,
            (po_id,)
        ).fetchone()

        if order is None:
            flash("Purchase Order tidak ditemukan.", "error")
            return redirect(url_for("purchase_orders"))

        if order["status"] != "Ordered":
            flash(
                "Penerimaan hanya bisa dicatat untuk request berstatus Ordered.",
                "error"
            )
            return redirect(url_for("purchase_orders"))

        existing_receipt = connection.execute(
            """
            SELECT id FROM goods_receipts
            WHERE purchase_order_id = ?
            """,
            (po_id,)
        ).fetchone()

        if existing_receipt:
            flash("Penerimaan untuk PO ini sudah tercatat.", "error")
            return redirect(url_for("goods_receipts"))

        if request.method == "POST":
            quantity_raw = request.form.get(
                "received_quantity", ""
            ).strip()
            notes = request.form.get("notes", "").strip()

            try:
                received_quantity = int(quantity_raw)
                if received_quantity <= 0:
                    raise ValueError
            except ValueError:
                flash("Jumlah penerimaan harus berupa bilangan positif.", "error")
                return redirect(
                    url_for("create_goods_receipt", po_id=po_id)
                )

            # Versi MVP ini mencatat penerimaan lengkap,
            # bukan penerimaan sebagian.
            if received_quantity != order["requested_quantity"]:
                flash(
                    f"Jumlah penerimaan harus sama dengan jumlah pesanan "
                    f"({order['requested_quantity']}) untuk menyelesaikan PO.",
                    "error"
                )
                return redirect(
                    url_for("create_goods_receipt", po_id=po_id)
                )

            receiver = connection.execute(
                """
                SELECT id FROM users
                WHERE email = ?
                  AND role = 'Procurement Staff'
                """,
                ("procurement@example.com",)
            ).fetchone()

            if receiver is None:
                flash(
                    "User Procurement Staff belum tersedia. "
                    "Jalankan python seed.py.",
                    "error"
                )
                return redirect(url_for("purchase_orders"))

            try:
                connection.execute(
                    """
                    INSERT INTO goods_receipts (
                        purchase_order_id,
                        received_quantity,
                        received_by,
                        notes
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        po_id,
                        received_quantity,
                        receiver["id"],
                        notes or None
                    )
                )

                connection.execute(
                    """
                    UPDATE purchase_requests
                    SET status = 'Received'
                    WHERE id = ? AND status = 'Ordered'
                    """,
                    (order["request_id"],)
                )

            except sqlite3.IntegrityError:
                flash(
                    "Penerimaan gagal disimpan. "
                    "Mungkin penerimaan PO ini sudah tercatat.",
                    "error"
                )
                return redirect(url_for("goods_receipts"))

            flash("Penerimaan barang berhasil dicatat.", "success")
            return redirect(url_for("goods_receipts"))

    return render_template(
        "goods_receipt_form.html",
        order=order
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
