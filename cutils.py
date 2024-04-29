import json
import typing
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

import discord
import requests
from requests import Session

import setup_db

if TYPE_CHECKING:
    from _typeshed import SupportsKeysAndGetItem


def getCMCjsondata(
    cmc_api: str, cmc_endpoint: str, params: typing.Optional[dict] = None
):
    url = f"https://pro-api.coinmarketcap.com/v1/{cmc_endpoint}"
    headers: SupportsKeysAndGetItem[str, str] = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": cmc_api,
    }

    session = Session()
    session.headers.update(headers)

    if not params:
        params = {}
    response = session.get(url, params=params)
    return json.loads(response.text)


def getAll(cmc_api: str) -> dict:
    json_data = getCMCjsondata(cmc_api=cmc_api, cmc_endpoint="cryptocurrency/map")
    data_len = len(json_data["data"])
    results: dict = {}

    for index in range(data_len):
        data_index = json_data["data"][index]
        symbol = f"${data_index['symbol'].lower()}"
        rank = data_index["rank"]

        if symbol in results and results[symbol]["rank"] < rank:
            continue

        if data_index["rank"]:
            results[f"${data_index['symbol'].lower()}"] = {
                "name": data_index["slug"],
                "id": str(data_index["id"]),
                "rank": rank,
            }
    return results


def getLogo(symbol: str, cmc_api: str) -> typing.Any:
    parameters = {"slug": setup_db.get_attr_with_symbol(symbol, "name")}
    json_data = getCMCjsondata(
        cmc_api=cmc_api, cmc_endpoint="cryptocurrency/info", params=parameters
    )

    cid = str(setup_db.get_attr_with_symbol(symbol, "id"))
    logo_url = json_data["data"][cid]["logo"]

    result = requests.get(logo_url)
    return result.content


def getCryptoMessage(symbol: str, cmc_api: str) -> tuple:
    name = setup_db.get_attr_with_symbol(symbol, "name")
    parameters = {"slug": name}
    json_data = getCMCjsondata(
        cmc_api=cmc_api, cmc_endpoint="cryptocurrency/quotes/latest", params=parameters
    )
    cmc_id = str(setup_db.get_attr_with_symbol(symbol, "id"))
    data_id = json_data["data"][cmc_id]
    data_usd = data_id["quote"]["USD"]
    price = data_usd["price"]
    dominance = f"{data_usd['market_cap_dominance']:.2f}%"
    mc = f"${data_usd['market_cap']:,.0f}"
    price_change = f"{data_usd['percent_change_24h']:.2f}%"
    volume_change = f"{data_usd['volume_change_24h']:.2f}%"

    if price > 1:
        price = f"${price:,.2f}"
    else:
        decimal_index = f".{abs(Decimal(price).adjusted()) + 2}f"
        price = f"${price:{decimal_index}}"

    image_path = f"{name}.png"
    if not Path(image_path).exists():
        print(f"populate_db_with_image {symbol}")
        setup_db.populate_db_with_image(symbol)

    embed = discord.Embed(title=f"--- **{name.upper()}** ---\n")
    embed.set_thumbnail(url=f"attachment://{image_path}")
    embed.add_field(name="Price", value=price, inline=False)
    embed.add_field(name="Market Cap", value=mc, inline=False)
    if name.lower() == "bitcoin":
        embed.add_field(name="Dominance", value=dominance, inline=False)
    embed.add_field(name="24h Price Change", value=price_change, inline=False)
    embed.add_field(name="24h Volume Change", value=volume_change, inline=False)
    return embed, image_path
