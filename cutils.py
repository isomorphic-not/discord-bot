import json
import typing
from decimal import Decimal
from typing import TYPE_CHECKING

import discord
from requests import Session

from constants import CMC

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


def getAll(cmc_api: str) -> None:
    json_data = getCMCjsondata(cmc_api=cmc_api, cmc_endpoint="cryptocurrency/map")
    data_len = len(json_data["data"])
    results: dict = {}

    for i in range(data_len):
        data_index = json_data["data"][i]
        key = f"${data_index['symbol'].lower()}"
        rank = data_index["rank"]

        if key in results and results[key]["rank"] < rank:
            continue

        if data_index["rank"]:
            results[f"${data_index['symbol'].lower()}"] = {
                "name": data_index["slug"],
                "id": str(data_index["id"]),
                "rank": rank,
            }
    return


def getLogo(symbol: str, cmc_api: str) -> typing.Any:
    parameters = {"slug": CMC.crypto[symbol]["name"]}
    json_data = getCMCjsondata(
        cmc_api=cmc_api, cmc_endpoint="cryptocurrency/info", params=parameters
    )

    cid = CMC.crypto[symbol]["id"]
    return json_data["data"][cid]["logo"]


def getCryptoMessage(symbol: str, cmc_api: str) -> discord.Embed:
    parameters = {"slug": CMC.crypto[symbol]["name"]}
    json_data = getCMCjsondata(
        cmc_api=cmc_api, cmc_endpoint="cryptocurrency/quotes/latest", params=parameters
    )

    data_id = json_data["data"][CMC.crypto[symbol]["id"]]
    data_usd = data_id["quote"]["USD"]
    name = data_id["name"]
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
    logo_url = getLogo(symbol, cmc_api)

    embed = discord.Embed(title=f"--- **{name.upper()}** ---\n")
    embed.set_thumbnail(url=logo_url)
    embed.add_field(name="Price", value=price, inline=False)
    embed.add_field(name="Market Cap", value=mc, inline=False)
    if name.lower() == "bitcoin":
        embed.add_field(name="Dominance", value=dominance, inline=False)
    embed.add_field(name="24h Price Change", value=price_change, inline=False)
    embed.add_field(name="24h Volume Change", value=volume_change, inline=False)
    return embed
