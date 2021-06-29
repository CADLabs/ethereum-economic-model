import requests
import diskcache

from model.types import Wei


cache = diskcache.Cache('.etherscan_api.cache')


@cache.memoize(expire=(6 * 60 * 60))  # cached for 6 hours
def get_eth_supply(default=None) -> Wei:
    result = int(requests.get("https://api.etherscan.io/api?module=stats&action=ethsupply", headers={"accept": "application/json"}).json()["result"])
    return result if result else default
