import typing
from decimal import Decimal
from pathlib import Path

import discord
import requests

from db_manager import DatabaseManager


class CoinMarketCapAPI:
    def __init__(self, cmc_api: str):
        self.cmc_api = cmc_api
        self.base_url = "https://pro-api.coinmarketcap.com/v1/"

    def _make_request(
        self, endpoint: str, params: typing.Optional[dict] = None
    ) -> typing.Optional[dict]:
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": self.cmc_api,
        }

        if params is None:
            params = {}

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        return response.json()

    def getAll(self) -> dict:
        json_data = self._make_request("cryptocurrency/map")["data"]
        if json_data is None:
            return {}

        results = {}
        for data_index in json_data:
            symbol = f"${data_index['symbol'].lower()}"
            rank = data_index["rank"]

            if symbol in results and results[symbol]["rank"] < rank:
                continue

            results[symbol] = {
                "name": data_index["slug"],
                "id": str(data_index["id"]),
                "rank": rank,
            }
        return results

    def getLogo(self, symbol: str) -> typing.Any:
        db_manager = DatabaseManager()
        parameters = {"slug": db_manager.get_attr_with_symbol(symbol, "name")}
        json_data = self._make_request("cryptocurrency/info", params=parameters)

        cmc_id = str(db_manager.get_attr_with_symbol(symbol, "id"))
        logo_url = json_data["data"][cmc_id]["logo"]

        response = requests.get(logo_url)
        response.raise_for_status()

        return response.content

    def getCryptoMessage(
        self, symbol: str, cmd: str = "general"
    ) -> typing.Tuple[discord.Embed, Path]:
        db_manager = DatabaseManager()
        name = db_manager.get_attr_with_symbol(symbol, "name")
        parameters = {"slug": name}

        data = self._make_request("cryptocurrency/quotes/latest", params=parameters)[
            "data"
        ]
        data_id = data[str(db_manager.get_attr_with_symbol(symbol, "id"))]
        data_usd = data_id["quote"]["USD"]

        price = data_usd.get("price", 0)
        dominance = f"{data_usd.get('market_cap_dominance', 0):.2f}%"
        mc = f"${data_usd.get('market_cap', 0):,.0f}"
        price_change = f"{data_usd.get('percent_change_24h', 0):.2f}%"
        volume_change = f"{data_usd.get('volume_change_24h', 0):.2f}%"

        if price > 1:
            price = f"${price:,.2f}"
        else:
            decimal_index = f".{abs(Decimal(price).adjusted()) + 2}f"
            price = f"${price:{decimal_index}}"

        image_path = Path(f"media/{name}.png")
        if not image_path.exists():
            print(f"populate_db_with_image {symbol}")
            db_manager.populate_db_with_image(symbol)

        embed = discord.Embed(title=f"--- **{name.upper()}** ---\n")
        embed.set_thumbnail(url=f"attachment://{image_path.name}")
        embed.add_field(name="Price", value=price, inline=False)
        embed.add_field(name="Market Cap", value=mc, inline=False)
        if name.lower() == "bitcoin":
            embed.add_field(name="Dominance", value=dominance, inline=False)
        embed.add_field(name="24h Price Change", value=price_change, inline=False)
        embed.add_field(name="24h Volume Change", value=volume_change, inline=False)
        return embed, image_path
