import io
import json
import typing
from typing import TYPE_CHECKING

import discord
from requests import Session, get

from constants import CMC

if TYPE_CHECKING:
    from _typeshed import SupportsKeysAndGetItem


def getAll(cmc_api: str) -> None:
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map"
    headers: SupportsKeysAndGetItem[str, str] = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": cmc_api,
    }

    session = Session()
    session.headers.update(headers)

    response = session.get(url)
    json_data = json.loads(response.text)
    data_len = len(json_data["data"])
    results = {}
    for i in range(data_len):
        if json_data["data"][i]["rank"] <= 500:
            results[f"!{json_data['data'][i]['symbol'].lower()}"] = {
                "name": json_data["data"][i]["slug"],
                "id": str(json_data["data"][i]["id"]),
            }
    print(results)


def getLogo(msg: str, cmc_api: str) -> typing.Any:
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/info"
    slug = CMC.crypto[msg]["name"]
    parameters = {"slug": slug}
    headers: SupportsKeysAndGetItem[str, str] = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": cmc_api,
    }

    session = Session()
    session.headers.update(headers)

    response = session.get(url, params=parameters)
    json_data = json.loads(response.text)

    cid = CMC.crypto[msg]["id"]
    return json_data["data"][cid]["logo"]


def getCryptoMessage(msg: str, cmc_api: str) -> discord.Embed:
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    slug = CMC.crypto[msg]["name"]
    parameters = {"slug": slug, "convert": "USD"}

    headers: SupportsKeysAndGetItem[str, str] = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": cmc_api,
    }

    session = Session()
    session.headers.update(headers)

    response = session.get(url, params=parameters)
    index = CMC.crypto[msg]["id"]
    json_data = json.loads(response.text)

    name = json_data["data"][index]["name"]
    price = json_data["data"][index]["quote"]["USD"]["price"]
    mc = f"{json_data['data'][index]['quote']['USD']['market_cap']:,.0f}"
    dominance = (
        f"{json_data['data'][index]['quote']['USD']['market_cap_dominance']:.2f}"
    )
    vdelta = f"{json_data['data'][index]['quote']['USD']['volume_change_24h']:.2f}"

    if price > 1:
        price = f"{price:,.2f}"
    logo_url = getLogo(msg, cmc_api)

    embed = discord.Embed(title=f"--- **{name.upper()}** ---\n")
    embed.set_thumbnail(url=logo_url)
    embed.add_field(name="Price", value=f"${price}", inline=False)
    embed.add_field(name="Market Cap", value=f"${mc}", inline=False)
    embed.add_field(name="Dominance", value=f"{dominance}%", inline=False)
    embed.add_field(name="Volume 24h change", value=f"{vdelta}%", inline=False)
    return embed
