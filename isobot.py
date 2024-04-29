import random
from pathlib import Path

import discord

import setup_db
from constants import CMC_KEY, TOKEN, media
from cutils import getCryptoMessage
from setup_db import get_symbols

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready() -> None:
    if not Path("crypto_data.db").exists():
        print(f"Creating new database...")
        setup_db.setup_db()
        print(f"Done!")
    if client.user:
        print(f"{client.user.name} has connected to Discord!")


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author == client.user:
        return
    msg = message.content.lower()
    if msg in get_symbols():
        if not CMC_KEY:
            raise EnvironmentError("CMC_KEY is empty")
        embed, image_path = getCryptoMessage(msg, CMC_KEY)
        file = discord.File(image_path, filename=image_path)
        await message.channel.send(file=file, embed=embed)
    elif msg == "!gct":
        response = random.choice(media)
        file = discord.File(response)
        await message.channel.send(file=file)


client.run(TOKEN)
