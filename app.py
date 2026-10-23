from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db, get_connection

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


if __name__ == "__main__":
    app.run(debug=True, port=5001)
