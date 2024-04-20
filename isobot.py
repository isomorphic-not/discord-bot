import os
import random

import discord
from dotenv import load_dotenv

from constants import MessageTriggers, media
from cutils import getCryptoMessage

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

load_dotenv()
if not (TOKEN := os.getenv("DISCORD_TOKEN")):
    raise EnvironmentError("TOKEN is empty")
if not (CMC_KEY := os.getenv("CMC_KEY")):
    raise EnvironmentError("CMC_KEY is empty")


@client.event
async def on_ready() -> None:
    if client.user:
        print(f"{client.user.name} has connected to Discord!")


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author == client.user:
        return
    msg = message.content.lower()
    if msg in MessageTriggers.crypto_ids:
        if not CMC_KEY:
            raise EnvironmentError("CMC_KEY is empty")
        await message.channel.send(getCryptoMessage(msg, CMC_KEY))
    elif msg in MessageTriggers.other_ids:
        response = random.choice(media)
        file = discord.File(response)
        await message.channel.send(file=file)


client.run(TOKEN)
