import io
import sqlite3
from pathlib import Path

from PIL import Image

import cutils
from constants import CMC_KEY

if Path("crypto_data.db").exists():
    conn = sqlite3.connect("crypto_data.db")
    cursor = conn.cursor()


def setup_db():
    conn = sqlite3.connect("crypto_data.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS crypto_data (
                        id INTEGER PRIMARY KEY,
                        symbol TEXT NOT NULL,
                        rank INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        image BLOB NULL
                    )"""
    )

    conn.commit()
    data = cutils.getAll(CMC_KEY)
    for key, values in data.items():
        print(f"{key} {values}")
        cursor.execute(
            "INSERT INTO crypto_data (id, symbol, rank, name) VALUES (?, ?, ?, ?)",
            (values["id"], key, values["rank"], values["name"]),
        )
    conn.commit()
    cursor.close()
    conn.close()


def check_image_exists(crypto_id):
    conn = sqlite3.connect("crypto_data.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT image FROM crypto_data WHERE id = ? AND image IS NOT NULL",
            (crypto_id,),
        )
        crypto_row = cursor.fetchone()
    except sqlite3.OperationalError:
        pass
    cursor.close()
    conn.close()
    return crypto_row is not None


def get_db_item(symbol):
    conn = sqlite3.connect("crypto_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crypto_data WHERE symbol = ?", (symbol,))
    crypto_row = cursor.fetchone()
    if not crypto_row["image"]:
        populate_db_with_image(symbol, crypto_row, conn, cursor)
    if crypto_row:
        check_image_exists(symbol)
        id, symbol, rank, name, image = crypto_row
        print(f"ID: {id}, Name: {name}, image: {image}")
        return crypto_row
    else:
        print("Item not found in the database.")
    cursor.close()
    conn.close()


def populate_db_with_image(symbol):
    conn = sqlite3.connect("crypto_data.db")
    cursor = conn.cursor()
    logo_bytes = cutils.getLogo(symbol, CMC_KEY)
    new_image_data = io.BytesIO(logo_bytes).read()
    image = Image.open(io.BytesIO(new_image_data))
    image_path = Path.cwd() / get_attr_with_symbol(symbol, "name")
    image.save(f"{image_path.name}.png")
    cursor.execute(
        "UPDATE crypto_data SET image = ? WHERE id = ?",
        (sqlite3.Binary(new_image_data), get_attr_with_symbol(symbol, "id")),
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_symbols():
    conn = sqlite3.connect("crypto_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT symbol FROM crypto_data")
    symbols = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return symbols


def get_attr_with_symbol(symbol, attr_to_get):
    conn = sqlite3.connect("crypto_data.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT {attr_to_get} FROM crypto_data WHERE symbol=?", (symbol,))
    attr_value = cursor.fetchone()

    if attr_value:
        attr_value = attr_value[0]
        return attr_value
    else:
        print(f"No entry found for symbol: {symbol}")
    cursor.close()
    conn.close()
