import os
from datetime import date

import psycopg2
from flask import Flask

app = Flask(__name__)

DB_URL = os.environ.get("DATABASE_URL", "postgresql://localhost/hurz")


def get_conn():
    return psycopg2.connect(DB_URL)


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS entries (
                    id   SERIAL PRIMARY KEY,
                    day  DATE NOT NULL
                )
                """
            )
        conn.commit()


@app.route("/hurz")
def hurz():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO entries (day) VALUES (%s)", (date.today(),))
            cur.execute("SELECT id, day FROM entries ORDER BY id")
            rows = cur.fetchall()
        conn.commit()

    lines = "\n".join(f"{row[0]:>4}  {row[1]}" for row in rows)
    return f"Eingetragen: {date.today()}\n\nAlle Einträge:\n{lines}\n", 200, {
        "Content-Type": "text/plain; charset=utf-8"
    }


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
