import json
import os
import random
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from _typeshed import SupportsKeysAndGetItem

from dotenv import load_dotenv
from requests import Session

cmc_index = {"bitcoin": "1", "solana": "5426", "crow-with-knife": "30402"}

load_dotenv()
if not (TOKEN := os.getenv("DISCORD_TOKEN")):
    raise EnvironmentError(f"TOKEN is empty")
if not (CMC_KEY := os.getenv("CMC_KEY")):
    raise EnvironmentError(f"CMC_KEY is empty")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


def getInfo(index: str) -> str:
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    api = CMC_KEY
    if not api:
        raise EnvironmentError(f"API key for CMC is empty")
    key = None
    for key, val in cmc_index.items():
        if val == index:
            break
    parameters = {"slug": key, "convert": "USD"}

    headers: SupportsKeysAndGetItem[str, str] = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": api,
    }

    session = Session()
    session.headers.update(headers)

    response = session.get(url, params=parameters)
    name = json.loads(response.text)["data"][index]["symbol"]
    price = json.loads(response.text)["data"][index]["quote"]["USD"]["price"]
    return f"{name}: {price}"


@client.event
async def on_ready() -> None:
    if client.user:
        print(f"{client.user.name} has connected to Discord!")


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author == client.user:
        return

    responses = [
        "I like ground control token.",
        "GCT",
        ("Ground control token is stupid as fuck. JK!"),
    ]

    if message.content.lower() == "!Jumbalaya".lower():
        response = random.choice(responses)
        await message.channel.send(response)
    elif message.content.lower() == "!sol".lower():
        await message.channel.send(getInfo(cmc_index["solana"]))
    elif message.content.lower() == "!btc".lower():
        await message.channel.send(getInfo(cmc_index["bitcoin"]))
    elif message.content.lower() == "!caw".lower():
        await message.channel.send(getInfo(cmc_index["crow-with-knife"]))
    elif message.content.lower() == "!beer".lower():
        file = discord.File(
            "media/new-belgium-voodoo-ranger-danger-beach-ipa-voodoo-vice-ipa-LEAD.png"
        )
        await message.channel.send(file=file)


client.run(TOKEN)
