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

    def getSingle(self, name: str) -> tuple:
        parameters = {"slug": name}
        json_data = self._make_request("cryptocurrency/info", params=parameters)["data"]
        single_id = list(json_data.keys())[0]
        name = json_data[single_id]["slug"]
        symbol = f"${json_data[single_id]['symbol'].lower()}"
        rank = 10
        return symbol, rank, name, single_id

    def getLogo(self, symbol: str) -> typing.Any:
        db_manager = DatabaseManager()
        parameters = {"slug": db_manager.get_attr_with_symbol(symbol, "name")}
        json_data = self._make_request("cryptocurrency/info", params=parameters)

        cmc_id = str(db_manager.get_attr_with_symbol(symbol, "id"))
        logo_url = json_data["data"][cmc_id]["logo"]

        response = requests.get(logo_url)
        response.raise_for_status()

        return response.content

    def get_volume(self, data_usd) -> dict:
        cmc_attributes = {}
        cmc_attributes["Price"] = data_usd.get("price", 0)
        cmc_attributes["Market Cap"] = f"${data_usd.get('market_cap', 0):,.0f}"
        cmc_attributes["Dominance"] = f"{data_usd.get('market_cap_dominance', 0):.2f}%"
        cmc_attributes["24h Price Change"] = (
            f"{data_usd.get('percent_change_24h', 0):.2f}%"
        )
        cmc_attributes["24h Volume Change"] = (
            f"{data_usd.get('volume_change_24h', 0):.2f}%"
        )

    def get_price(self, data_usd) -> dict:
        cmc_attributes = {}
        cmc_attributes["Price"] = data_usd.get("price", 0)
        cmc_attributes["1h Price Change"] = (
            f"${data_usd.get('percent_change_1h', 0):.2f}%"
        )
        cmc_attributes["24h Price Change"] = (
            f"{data_usd.get('percent_change_24h', 0):.2f}%"
        )
        cmc_attributes["7d Price Change"] = (
            f"{data_usd.get('percent_change_7d', 0):.2f}%"
        )
        cmc_attributes["30d Price Change"] = (
            f"{data_usd.get('percent_change_30d', 0):.2f}%"
        )
        return cmc_attributes

    def get_general(self, data_usd):
        cmc_attributes = {}
        cmc_attributes["Price"] = data_usd.get("price", 0)
        cmc_attributes["Market Cap"] = f"${data_usd.get('market_cap', 0):,.0f}"
        cmc_attributes["Dominance"] = f"{data_usd.get('market_cap_dominance', 0):.2f}%"
        cmc_attributes["24h Price Change"] = (
            f"{data_usd.get('percent_change_24h', 0):.2f}%"
        )
        cmc_attributes["24h Volume Change"] = (
            f"{data_usd.get('volume_change_24h', 0):.2f}%"
        )
        return cmc_attributes

    def get_cmc_attributes(self, data_usd, cmd: typing.Optional[str]) -> dict:
        if not cmd:
            return self.get_general(data_usd)
        elif cmd == "price":
            return self.get_price(data_usd)
        elif cmd == "volume":
            return self.get_volume(data_usd)
        else:
            raise RuntimeError("BAD")

    def getCryptoMessage(
        self, symbol: str, cmd: typing.Optional[str] = None
    ) -> typing.Tuple[discord.Embed, Path]:
        db_manager = DatabaseManager()
        name = db_manager.get_attr_with_symbol(symbol, "name")
        parameters = {"slug": name}

        data = self._make_request("cryptocurrency/quotes/latest", params=parameters)[
            "data"
        ]
        data_id = data[str(db_manager.get_attr_with_symbol(symbol, "id"))]
        data_usd = data_id["quote"]["USD"]
        cmc_attributes = self.get_cmc_attributes(data_usd, cmd)
        price = cmc_attributes["Price"]

        if price > 1:
            price = f"${price:,.2f}"
        else:
            decimal_index = f".{abs(Decimal(price).adjusted()) + 2}f"
            price = f"${price:{decimal_index}}"

        cmc_attributes["Price"] = price
        image_path = Path(f"media/{name}.png")
        if not image_path.exists():
            print(f"populate_db_with_image {symbol}")
            db_manager.populate_db_with_image(symbol)

        embed = discord.Embed(title=f"--- **{name.upper()}** ---\n")
        embed.set_thumbnail(url=f"attachment://{image_path.name}")
        for key, value in cmc_attributes.items():
            if key == "Dominance" and name.lower() == "bitcoin" and cmd is None:
                embed.add_field(name=key, value=value, inline=False)
            elif key != "Dominance":
                embed.add_field(name=key, value=value, inline=False)

        return embed, image_path


DatabaseManager().add_crypto("kendu-inu")
