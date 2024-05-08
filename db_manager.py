import io
import sqlite3
from pathlib import Path

from PIL import Image

import cutils
from constants import CMC_KEY


class DatabaseManager:
    def __init__(self, db_name: str = "crypto_data.db") -> None:
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def __del__(self) -> None:
        self.conn.close()

    def setup_db(self) -> None:
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS crypto_data (
                            id INTEGER PRIMARY KEY,
                            symbol TEXT NOT NULL,
                            rank INTEGER NOT NULL,
                            name TEXT NOT NULL,
                            image BLOB NULL
                        )"""
        )

        self.conn.commit()
        data = cutils.CoinMarketCapAPI(CMC_KEY).getAll()
        for key, values in data.items():
            print(f"{key} {values}")
            self.cursor.execute(
                "INSERT INTO crypto_data (id, symbol, rank, name) VALUES (?, ?, ?, ?)",
                (values["id"], key, values["rank"], values["name"]),
            )
        self.conn.commit()

    def add_crypto(self, name) -> None:
        data = cutils.CoinMarketCapAPI(CMC_KEY).getSingle(name)
        self.cursor.execute(
            "UPDATE crypto_data SET symbol=?, rank=?, name=? WHERE id=?", data
        )
        self.conn.commit()

    def check_image_exists(self, crypto_id) -> bool:
        try:
            self.cursor.execute(
                "SELECT image FROM crypto_data WHERE id = ? AND image IS NOT NULL",
                (crypto_id),
            )
            crypto_row = self.cursor.fetchone()
        except sqlite3.OperationalError:
            pass
        return crypto_row is not None

    def get_db_item(self, symbol) -> None:
        self.cursor.execute("SELECT * FROM crypto_data WHERE symbol = ?", (symbol,))
        crypto_row = self.cursor.fetchone()
        if not crypto_row["image"]:
            self.populate_db_with_image(symbol)
        if crypto_row:
            self.check_image_exists(symbol)
            id, symbol, rank, name, image = crypto_row
            print(f"ID: {id}, Name: {name}, image: {image}")
            return crypto_row
        else:
            print("Item not found in the database.")

    def populate_db_with_image(self, symbol) -> None:
        logo_bytes = cutils.CoinMarketCapAPI(CMC_KEY).getLogo(symbol)
        new_image_data = io.BytesIO(logo_bytes).read()
        image = Image.open(io.BytesIO(new_image_data))
        image_path = Path.cwd() / self.get_attr_with_symbol(symbol, "name")
        image.save(f"media/{image_path.name}.png")
        self.cursor.execute(
            "UPDATE crypto_data SET image = ? WHERE id = ?",
            (sqlite3.Binary(new_image_data), self.get_attr_with_symbol(symbol, "id")),
        )
        self.conn.commit()

    def get_symbols(self) -> list:
        self.cursor.execute("SELECT symbol FROM crypto_data")
        symbols = [row[0] for row in self.cursor.fetchall()]
        return symbols

    def get_attr_with_symbol(self, symbol, attr_to_get) -> str:
        self.cursor.execute(
            f"SELECT {attr_to_get} FROM crypto_data WHERE symbol=?", (symbol,)
        )
        attr_value = self.cursor.fetchone()

        if attr_value:
            attr_value = attr_value[0]
        else:
            print(f"No entry found for symbol: {symbol}")
            attr_value = ""
        return attr_value
