import json
from typing import TYPE_CHECKING

from requests import Session

from constants import CMC

if TYPE_CHECKING:
    from _typeshed import SupportsKeysAndGetItem


def getCryptoMessage(msg: str, cmc_api: str) -> str:
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    if not cmc_api:
        raise EnvironmentError(f"API key for CMC is empty")

    parameters = {"slug": CMC.crypto[msg]["name"], "convert": "USD"}

    headers: SupportsKeysAndGetItem[str, str] = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": cmc_api,
    }

    session = Session()
    session.headers.update(headers)

    response = session.get(url, params=parameters)
    index = CMC.crypto[msg]["id"]
    name = json.loads(response.text)["data"][index]["symbol"]
    price = json.loads(response.text)["data"][index]["quote"]["USD"]["price"]
    return f"{name}: {price}"
