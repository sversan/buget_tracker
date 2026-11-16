
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "budget.db"


def get_connection():
    DATA_DIR.mkdir(exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT DEFAULT '',
                transaction_date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


def add_transaction(transaction_type, amount, category,
                    description, transaction_date):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO transactions (
                transaction_type,
                amount,
                category,
                description,
                transaction_date
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            transaction_type,
            amount,
            category,
            description,
            transaction_date
        ))


def get_transactions():
    with get_connection() as conn:
        return conn.execute("""
            SELECT * FROM transactions
            ORDER BY transaction_date DESC, id DESC
        """).fetchall()


def get_monthly_totals(year, month):
    with get_connection() as conn:
        result = conn.execute("""
            SELECT
                transaction_type,
                COALESCE(SUM(amount), 0) AS total
            FROM transactions
            WHERE strftime('%Y', transaction_date) = ?
              AND strftime('%m', transaction_date) = ?
            GROUP BY transaction_type
        """, (str(year), f"{month:02d}")).fetchall()

    totals = {"Income": 0.0, "Expense": 0.0}

    for row in result:
        totals[row["transaction_type"]] = row["total"]

    return totals


def get_all_totals():
    with get_connection() as conn:
        result = conn.execute("""
            SELECT
                transaction_type,
                COALESCE(SUM(amount), 0) AS total
            FROM transactions
            GROUP BY transaction_type
        """).fetchall()

    totals = {"Income": 0.0, "Expense": 0.0}

    for row in result:
        totals[row["transaction_type"]] = row["total"]

    return totals


def get_category_totals(year, month):
    with get_connection() as conn:
        return conn.execute("""
            SELECT category, SUM(amount) AS total
            FROM transactions
            WHERE transaction_type = 'Expense'
              AND strftime('%Y', transaction_date) = ?
              AND strftime('%m', transaction_date) = ?
            GROUP BY category
            ORDER BY total DESC
        """, (str(year), f"{month:02d}")).fetchall()


def get_daily_totals(year, month):
    with get_connection() as conn:
        return conn.execute("""
            SELECT
                transaction_date,
                SUM(CASE WHEN transaction_type = 'Income'
                    THEN amount ELSE 0 END) AS income,
                SUM(CASE WHEN transaction_type = 'Expense'
                    THEN amount ELSE 0 END) AS expenses
            FROM transactions
            WHERE strftime('%Y', transaction_date) = ?
              AND strftime('%m', transaction_date) = ?
            GROUP BY transaction_date
            ORDER BY transaction_date
        """, (str(year), f"{month:02d}")).fetchall()


def get_month_comparison(year, month):
    with get_connection() as conn:
        return conn.execute("""
            SELECT
                strftime('%m', transaction_date) AS month,
                SUM(CASE WHEN transaction_type = 'Income'
                    THEN amount ELSE 0 END) AS income,
                SUM(CASE WHEN transaction_type = 'Expense'
                    THEN amount ELSE 0 END) AS expenses
            FROM transactions
            WHERE strftime('%Y', transaction_date) = ?
            GROUP BY strftime('%m', transaction_date)
            ORDER BY month
        """, (str(year),)).fetchall()

 
