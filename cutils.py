import json
from typing import TYPE_CHECKING

from requests import Session

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
        results[f"!{json_data['data'][i]['symbol'].lower()}"] = {
            "name": json_data["data"][i]["slug"],
            "id": str(json_data["data"][i]["id"]),
        }


def getCryptoMessage(msg: str, cmc_api: str) -> str:
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

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
