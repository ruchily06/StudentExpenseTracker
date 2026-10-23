from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "expenses.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def index():

    conn = get_db_connection()

    expenses = conn.execute("""
        SELECT * FROM expenses
        ORDER BY id DESC
    """).fetchall()

    total = conn.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
    """).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        expenses=expenses,
        total=total
    )


@app.route("/add", methods=["POST"])
def add_expense():

    name = request.form.get("name")
    amount = request.form.get("amount")
    category = request.form.get("category")

    if not name or not amount or not category:
        return redirect(url_for("index"))

    try:
        amount = float(amount)

    except ValueError:
        return redirect(url_for("index"))

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO expenses (name, amount, category)
        VALUES (?, ?, ?)
    """, (name, amount, category))

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


@app.route("/delete/<int:expense_id>")
def delete_expense(expense_id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )