import os

from dotenv import load_dotenv

load_dotenv()

if not (TOKEN := os.getenv("DISCORD_TOKEN")):
    raise EnvironmentError("TOKEN is empty")
if not (CMC_KEY := os.getenv("CMC_KEY")):
    raise EnvironmentError("CMC_KEY is empty")

media = (
    "media/gct1.gif",
    "media/gct2.gif",
    "media/gct3.gif",
)
