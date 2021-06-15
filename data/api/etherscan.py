import requests
import diskcache

cache = diskcache.Cache()

@cache.memoize(expire=(6 * 60 * 60))  # cached for 6 hours
def get_eth_supply() -> int:
    return int(requests.get("https://api.etherscan.io/api?module=stats&action=ethsupply", headers={"accept": "application/json"}).json()["result"])
