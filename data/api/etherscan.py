import requests
import diskcache
import logging

from model.types import Wei


cache = diskcache.Cache('.etherscan_api.cache')


@cache.memoize(expire=(6 * 60 * 60))  # cached for 6 hours
def get_eth_supply(default=None) -> Wei:
    try:
        req = requests.get("https://api.etherscan.io/api?module=stats&action=ethsupply", headers={"accept": "application/json"})
        req.raise_for_status()
        return int(req.json()["result"])
    except requests.exceptions.HTTPError as err:
        logging.error(err)
        return default
