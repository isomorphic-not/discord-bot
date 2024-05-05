import random
from pathlib import Path

import discord

from constants import CMC_KEY, TOKEN, media
from cutils import CoinMarketCapAPI
from db_manager import DatabaseManager

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready() -> None:
    if not Path("crypto_data.db").exists():
        print(f"Creating new database...")
        DatabaseManager().setup_db()
        print(f"Done!")
    if client.user:
        print(f"{client.user.name} has connected to Discord!")


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author == client.user:
        return
    msg = message.content.lower()
    msg_value = msg.split(" ")
    msg_value_len = len(msg_value)

    if msg_value_len > 2:
        return

    symbol = msg_value[0]
    command = None

    if msg_value_len == 2:
        command = msg_value[1]

    if symbol in DatabaseManager().get_symbols():
        if not CMC_KEY:
            raise EnvironmentError("CMC_KEY is empty")
        if command and command in ["price", "volume"]:
            print("did it")
        cmc_api = CoinMarketCapAPI(CMC_KEY)
        embed, image_path = cmc_api.getCryptoMessage(symbol)

        file = discord.File(image_path, filename=image_path.name)
        await message.channel.send(file=file, embed=embed)
    elif symbol == "!gct":
        response = random.choice(media)
        file = discord.File(response)
        await message.channel.send(file=file)


client.run(TOKEN)
